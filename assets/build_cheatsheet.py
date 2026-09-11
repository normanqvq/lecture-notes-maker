#!/usr/bin/env python3
"""
Build a cheatsheet PDF from a content module.

    python assets/build_cheatsheet.py content.py --out cheatsheet.pdf [--check] [--measure]

--check    rasterise pages + column crops into _check/ and report code lines that will be clipped
--measure  lay every fragment out in one real-width column and print heights per page,
           as a fraction of one column (3 columns per side => a side holds 3.00 minus break waste)
"""
import argparse, html, importlib.util, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cheatsheet as cs

def load(path):
    spec = importlib.util.spec_from_file_location("content", path)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, os.path.dirname(os.path.abspath(path)))
    spec.loader.exec_module(mod)
    return mod

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("content"); ap.add_argument("--out", default="cheatsheet.pdf")
    ap.add_argument("--check", action="store_true"); ap.add_argument("--measure", action="store_true")
    a = ap.parse_args()
    mod = load(a.content)
    pages = mod.PAGES; title = getattr(mod, "TITLE", "Cheatsheet")
    css_extra = getattr(mod, "CSS_EXTRA", ""); layout = getattr(mod, "LAYOUT", {})
    L = dict(cs.LAYOUT_DEFAULTS); L.update(layout)
    cs.LINE_LIMIT = L["code_line_limit"]

    html_doc = cs.build_html(pages, title, css_extra, layout)
    html_path = os.path.splitext(a.out)[0] + ".html"
    open(html_path, "w").write(html_doc)
    cs.render_pdf(html_path, a.out)
    n = cs.pdf_pages(a.out)
    print(f"wrote {a.out}: {n} page(s), expected {len(pages)}")
    if n != len(pages):
        print("!! page count differs from PAGES - a page box is taller than the paper or content is empty")

    # clipped code lines: scan the generated <pre class="code"> blocks
    bad = []
    for m in re.finditer(r'<pre class="code[^"]*">(.*?)</pre>', html_doc, re.S):
        for ln in re.sub(r"<[^>]+>", "", m.group(1)).split("\n"):
            ln = html.unescape(ln)
            if len(ln) > L["code_line_limit"]:
                bad.append(ln)
    if bad:
        print(f"!! {len(bad)} code line(s) longer than {L['code_line_limit']} chars will be clipped at the column edge:")
        for ln in bad[:40]: print("   ", len(ln), ln)

    if a.measure:
        res, colh = cs.measure(pages, title, css_extra, layout)
        tot = {}
        for p, i, h in res: tot[p] = tot.get(p, 0) + h
        for p in sorted(tot):
            print(f"side {p+1}: content = {tot[p]/colh:.2f} columns of {L['columns']} (add ~0.1 for column-break waste)")
        for p, i, h in res:
            frag = re.sub(r"<[^>]+>", " ", pages[p][i]); frag = html.unescape(re.sub(r"\s+", " ", frag)).strip()[:60]
            print(f"  side {p+1} #{i:>2} {h:5d}px {h/colh:5.2f}col  {frag}")

    if a.check:
        out_dir = os.path.join(os.path.dirname(os.path.abspath(a.out)), "_check")
        cs.rasterize(a.out, out_dir, n, L["columns"])
        print(f"check images in {out_dir}: pg-N.png (whole side), zN-cC-rR.png (column C, half R at 220 dpi). LOOK AT THEM.")

if __name__ == "__main__":
    main()
