#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build a study-notes PDF from HTML fragments.

    python build.py --parts parts --css notes.css --out notes.pdf \
                    --footer "Course - Lecture 2" --check

Reads every *.html in --parts (sorted by filename), highlights code blocks,
injects the stylesheet, and renders with WeasyPrint.

--check additionally rasterises the result so the layout can be inspected
before delivery: full-size page images (pg-NN.png, at --check-dpi) plus small
contact sheets tiled from them for the overview pass.

Dependencies:  pip install weasyprint pillow
--check additionally requires poppler (for pdftoppm) as a hard dependency:
it exits non-zero if pdftoppm is missing rather than skipping the check.
"""

import argparse
import glob
import html
import os
import re
import subprocess
import sys

# --------------------------------------------------------------------------
# Syntax highlighting
#
# Mark code blocks up as:
#     <pre class="code" data-lang="arm">...</pre>
#
# data-lang picks a profile below; omit it for the generic profile, which
# highlights comments, strings and numbers only. <pre class="plain"> skips
# highlighting entirely.
#
# To support another language, append one entry to PROFILES. Nothing else
# needs to change.
# --------------------------------------------------------------------------

Q3D = '"' * 3
Q3S = "'" * 3

PROFILES = {
    "arm": {
        "comment": r"[@;][^\n]*$",
        "string": None,
        "directive": r"^[ \t]*\.[A-Za-z_]\w*",
        "label": r"^[A-Za-z_.]\w*:",
        "number": r"[#=][A-Za-z_0-9][\w+\-]*|0[xX][0-9A-Fa-f]+|\b\d+\b",
        "keywords": set("""
            LDR STR LDRB STRB LDRH STRH LDRSB LDRSH LDRD STRD LDM STM PUSH POP
            MOV MOVS MOVW MOVT MVN MVNS ADD ADDS ADDW ADC ADCS SUB SUBS SUBW
            SBC SBCS RSB RSBS MUL MULS MLA MLS SDIV UDIV CMP CMN TST TEQ
            AND ANDS ORR ORRS EOR EORS BIC BICS LSL LSLS LSR LSRS ASR ASRS
            ROR RORS RRX B BL BX BLX BEQ BNE BGT BLT BGE BLE BHI BLS BCS BCC
            BMI BPL BVS BVC IT ITE ITT ITTT NOP ADR
        """.split()),
        "special": set(["R%d" % i for i in range(16)]
                       + "SP LR PC APSR IP FP".split()),
        "fold_case": True,
    },
    "c": {
        "comment": r"//[^\n]*$|(?s:/\*.*?\*/)",
        "string": r'"(?:[^"\\]|\\.)*"' + r"|'(?:[^'\\]|\\.)*'",
        "directive": r"^[ \t]*#[ \t]*[a-z]+",
        "label": None,
        "number": r"\b0[xX][0-9A-Fa-f]+\b|\b\d+\.?\d*[uUlLfF]*\b",
        "keywords": set("""
            auto break case char const continue default do double else enum
            extern float for goto if inline int long register restrict return
            short signed sizeof static struct switch typedef union unsigned
            void volatile while bool true false NULL
        """.split()),
        "special": set("""
            uint8_t uint16_t uint32_t uint64_t int8_t int16_t int32_t int64_t
            size_t FILE
        """.split()),
        "fold_case": False,
    },
    "python": {
        "comment": r"#[^\n]*$",
        "string": ("(?s:" + Q3D + r".*?" + Q3D + ")|"
                   + "(?s:" + Q3S + r".*?" + Q3S + ")|"
                   + r'"(?:[^"\\]|\\.)*"' + r"|'(?:[^'\\]|\\.)*'"),
        "directive": None,
        "label": None,
        "number": r"\b0[xX][0-9A-Fa-f]+\b|\b\d+\.?\d*\b",
        "keywords": set("""
            and as assert async await break class continue def del elif else
            except finally for from global if import in is lambda None nonlocal
            not or pass raise return True False try while with yield
        """.split()),
        "special": set("""
            self cls print len range enumerate zip dict list set tuple
            int str float bool open
        """.split()),
        "fold_case": False,
    },
    "verilog": {
        # Verilog has no '#' comment: '#' introduces a delay control (#25).
        # The generic profile would swallow the rest of such a line.
        "comment": r"//[^\n]*$|(?s:/\*.*?\*/)",
        "string": r'"(?:[^"\\]|\\.)*"',
        "directive": r"^[ \t]*`[A-Za-z_]\w*",
        "label": None,
        # sized/unsized based literals (4'ha, 16'h0x0z, 'd1), delays (#25),
        # and plain numbers with underscore separators (2_000_000)
        "number": (r"[0-9_]*'[sS]?[bBoOdDhH][0-9a-fA-FxXzZ?_]+"
                   r"|#\d[\d_]*"
                   r"|\b\d[\d_]*(?:\.\d[\d_]*)?(?:[eE][+-]?\d+)?"),
        "keywords": set("""
            module endmodule input output inout wire tri reg integer real time
            parameter localparam defparam assign always initial begin end
            if else case casex casez endcase default for while repeat forever
            function endfunction task endtask posedge negedge generate
            endgenerate genvar signed wait disable fork join
        """.split()),
        # built-in gate primitives get their own colour: a listing that says
        # "and2" or "inv" is not using a primitive, and that shows up visually
        "special": set("""
            and nand or nor xor xnor buf not bufif0 bufif1 notif0 notif1
            pullup pulldown
        """.split()),
        "fold_case": False,
    },
    "sql": {
        "comment": r"--[^\n]*$",
        "string": r"'(?:[^'\\]|\\.)*'",
        "directive": None,
        "label": None,
        "number": r"\b\d+\.?\d*\b",
        "keywords": set("""
            SELECT FROM WHERE GROUP BY HAVING ORDER LIMIT OFFSET JOIN LEFT
            RIGHT INNER OUTER FULL ON AS INSERT INTO VALUES UPDATE SET DELETE
            CREATE TABLE ALTER DROP INDEX VIEW UNION ALL DISTINCT AND OR NOT
            NULL IS IN BETWEEN LIKE CASE WHEN THEN ELSE END WITH ASC DESC
        """.split()),
        "special": set("COUNT SUM AVG MIN MAX COALESCE CAST ROUND".split()),
        "fold_case": True,
    },
    "generic": {
        "comment": r"#[^\n]*$|//[^\n]*$",
        "string": r'"(?:[^"\\]|\\.)*"',
        "directive": None,
        "label": None,
        # tolerate underscore digit separators (1_000_000, 0xDEAD_BEEF)
        "number": r"\b0[xX][0-9A-Fa-f_]+\b|\b\d[\d_]*\.?[\d_]*\b",
        "keywords": set(),
        "special": set(),
        "fold_case": False,
    },
}

_CLASS = {"comment": "c-cm", "string": "c-st", "directive": "c-di",
          "label": "c-lb", "number": "c-im", "punct": "c-pu"}


def _compile(profile):
    """Build one alternation regex per profile, preserving group order."""
    parts = []
    for name in ("comment", "string", "directive", "label", "number"):
        pattern = profile.get(name)
        if pattern:
            parts.append("(?P<%s>%s)" % (name, pattern))
    parts.append(r"(?P<word>[A-Za-z_]\w*)")
    parts.append(r"(?P<punct>[\[\]{}!,])")
    return re.compile("|".join(parts), re.M)


_COMPILED = {name: _compile(p) for name, p in PROFILES.items()}


def highlight(source, lang="generic"):
    """Wrap recognised tokens in <span> elements for CSS colouring."""
    profile = PROFILES.get(lang, PROFILES["generic"])
    token_re = _COMPILED.get(lang, _COMPILED["generic"])
    fold = profile["fold_case"]

    # Fragments are HTML, so entities may already be escaped.
    # Decode first, then re-escape, to avoid &amp;lt; in output.
    text = html.unescape(source.strip("\n"))
    out, pos = [], 0

    for m in token_re.finditer(text):
        out.append(html.escape(text[pos:m.start()]))
        pos = m.end()
        kind, raw = m.lastgroup, m.group()
        esc = html.escape(raw)

        if kind == "directive":
            indent = raw[:len(raw) - len(raw.lstrip())]
            out.append('%s<span class="c-di">%s</span>'
                       % (indent, html.escape(raw.strip())))
        elif kind == "word":
            probe = raw.upper() if fold else raw
            if probe in profile["special"]:
                out.append('<span class="c-rg">%s</span>' % esc)
            elif probe in profile["keywords"]:
                out.append('<span class="c-mn">%s</span>' % esc)
            else:
                out.append('<span class="c-id">%s</span>' % esc)
        elif kind in _CLASS:
            out.append('<span class="%s">%s</span>' % (_CLASS[kind], esc))
        else:
            out.append(esc)

    out.append(html.escape(text[pos:]))
    return "".join(out)


# class= may sit anywhere in the tag: <pre data-lang="c" class="code"> has to
# match too, otherwise the block is silently left unhighlighted.
_BLOCK = re.compile(
    r'<pre(?P<attr>[^>]*?\sclass="(?P<cls>code|asm)(?P<extra>[^"]*)"[^>]*)>'
    r'(?P<body>.*?)</pre>', re.S)

_LANG_ATTR = re.compile(r'data-lang="([^"]+)"')


def render_code_blocks(doc):
    def repl(m):
        attr = m.group("attr")
        found = _LANG_ATTR.search(attr)
        # class="asm" without data-lang keeps the ARM default.
        lang = found.group(1) if found else (
            "arm" if m.group("cls") == "asm" else "generic")
        # attr is the original attribute text, so it round-trips verbatim.
        return '<pre%s>%s</pre>' % (attr, highlight(m.group("body"), lang))
    return _BLOCK.sub(repl, doc)


# --------------------------------------------------------------------------
# Assembly and rendering
# --------------------------------------------------------------------------

def assemble(parts_dir, css_path, footer):
    files = sorted(glob.glob(os.path.join(parts_dir, "*.html")))
    if not files:
        sys.exit("No .html fragments found in %s" % parts_dir)

    body = "\n".join(open(f, encoding="utf-8").read() for f in files)
    body = render_code_blocks(body)

    css = open(css_path, encoding="utf-8").read()
    css = css.replace("__FOOTER__", html.escape(footer))

    return ("<!DOCTYPE html><html><head><meta charset='utf-8'>"
            "<style>%s</style></head><body>%s</body></html>" % (css, body))


SHEET_DPI = 55          # contact-sheet thumbnails only


def visual_check(pdf_path, dpi=120, per_sheet=6):
    """Rasterise pages and tile them into contact sheets for inspection.

    Two resolutions on purpose. The pg-NN.png rasters come out at `dpi`, high
    enough that 7-8 pt code and SVG labels are actually legible - that is what
    Step 7 asks you to judge, and it cannot be judged on a thumbnail. The
    contact sheets are tiled from downscaled copies and are only the overview
    pass: skim them, then open the individual pages that look wrong.
    """
    out_dir = os.path.join(os.path.dirname(pdf_path) or ".", "_check")
    os.makedirs(out_dir, exist_ok=True)
    for stale in glob.glob(os.path.join(out_dir, "*.png")):
        os.remove(stale)

    # --check is a guarantee, not a best-effort: if it cannot actually look at
    # the pages it must fail loudly rather than exit 0 having checked nothing.
    try:
        subprocess.run(["pdftoppm", "-r", str(dpi), "-png", pdf_path,
                        os.path.join(out_dir, "pg")], check=True)
    except FileNotFoundError:
        sys.exit(
            "ERROR: --check requires pdftoppm, which was not found on PATH.\n"
            "  The visual check is a non-negotiable step (SKILL.md Step 7);\n"
            "  skipping it would mean delivering an uninspected PDF.\n"
            "  Install poppler:\n"
            "    Windows  winget install oschwartz10612.Poppler\n"
            "    macOS    brew install poppler\n"
            "    Linux    apt install poppler-utils\n"
            "  (then restart the shell so PATH picks it up)")
    except subprocess.CalledProcessError as e:
        sys.exit("ERROR: pdftoppm failed on %s (exit %d); "
                 "cannot verify layout." % (pdf_path, e.returncode))

    try:
        from PIL import Image
    except ImportError:
        print("  ! Pillow unavailable - page rasters written, "
              "no contact sheets")
        return

    scale = float(SHEET_DPI) / dpi
    pages = sorted(glob.glob(os.path.join(out_dir, "pg-*.png")))
    for start in range(0, len(pages), per_sheet):
        chunk = []
        for p in pages[start:start + per_sheet]:
            img = Image.open(p)
            if scale < 1:
                img = img.resize((max(1, int(img.width * scale)),
                                  max(1, int(img.height * scale))),
                                 Image.LANCZOS)
            chunk.append(img)
        w, h = chunk[0].size
        # a 1- or 2-page chunk should not be padded out to a 3-wide sheet
        cols = min(3, len(chunk))
        rows = (len(chunk) + cols - 1) // cols
        sheet = Image.new("RGB", (w * cols, h * rows), "white")
        for i, img in enumerate(chunk):
            sheet.paste(img, ((i % cols) * w, (i // cols) * h))
        sheet.save(os.path.join(out_dir,
                                "sheet%02d.png" % (start // per_sheet + 1)))

    print("  contact sheets -> %s/sheetNN.png  (overview pass)" % out_dir)
    print("  page rasters   -> %s/pg-NN.png    (%d dpi - open these to judge "
          "labels, overflow and page breaks)" % (out_dir, dpi))


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--parts", default="parts",
                    help="directory of .html fragments (default: parts)")
    ap.add_argument("--css", default="notes.css",
                    help="stylesheet path (default: notes.css)")
    ap.add_argument("--out", default="notes.pdf", help="output PDF path")
    ap.add_argument("--footer", default="Study notes",
                    help="running footer text")
    ap.add_argument("--keep-html", action="store_true",
                    help="also write the assembled HTML next to the PDF")
    ap.add_argument("--check", action="store_true",
                    help="rasterise pages and build contact sheets")
    ap.add_argument("--check-dpi", type=int, default=120, metavar="N",
                    help="resolution of the --check page rasters "
                         "(default: 120; below ~100 small text is unreadable)")
    ap.add_argument("--list-langs", action="store_true",
                    help="print available data-lang profiles and exit")
    args = ap.parse_args()

    if args.list_langs:
        print("Available data-lang profiles: %s"
              % ", ".join(sorted(PROFILES)))
        return

    from weasyprint import HTML

    doc = assemble(args.parts, args.css, args.footer)

    out_dir = os.path.dirname(args.out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    if args.keep_html:
        open(os.path.splitext(args.out)[0] + ".html", "w",
             encoding="utf-8").write(doc)

    HTML(string=doc, base_url=os.path.abspath(args.parts)).write_pdf(args.out)
    print("built %s  (%d KB)" % (args.out, os.path.getsize(args.out) // 1024))

    if args.check:
        visual_check(args.out, dpi=args.check_dpi)


if __name__ == "__main__":
    main()
