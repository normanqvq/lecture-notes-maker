"""
cheatsheet.py — library for building dense, double-sided A4 exam cheatsheets.

A *content module* (see content_template.py) imports the helpers from here,
builds a list of pages (each page = list of HTML fragments) and exposes:

    TITLE     = "CS2040C Quiz 1 Cheatsheet"      # <title> of the HTML
    PAGES     = [P1, P2]                         # one list of fragments per side
    CSS_EXTRA = ""                               # optional overrides
    LAYOUT    = {}                               # optional: columns, fonts, ...

build_cheatsheet.py turns that into HTML, renders it with headless Chrome and
(optionally) rasterises the result for inspection.
"""
import base64, html, os, re, shutil, subprocess, sys, glob, platform

# ----------------------------------------------------------------------------
# Layout defaults (all tuned on real A4 landscape prints; see references/)
# ----------------------------------------------------------------------------
LAYOUT_DEFAULTS = dict(
    page="A4 landscape",
    margin="4mm 4.5mm",
    columns=3,
    column_gap="2.6mm",
    page_height="202mm",       # 210mm - top/bottom margins
    body_pt=5.5,
    code_pt=5.0,
    table_pt=5.0,
    h1_pt=7.4,
    h2_pt=6.2,
    code_line_limit=78,        # chars per code line before it is clipped (3 cols, Consolas 5pt)
    mono='"ConsolasEmb", Consolas, Menlo, "DejaVu Sans Mono", monospace',
    serif='"Times New Roman", Times, "PingFang SC", "Songti SC", serif',
)

def base_css(L):
    return f'''
@page {{ size: {L["page"]}; margin: {L["margin"]}; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; font-family: {L["serif"]}; font-size: {L["body_pt"]}pt; line-height: 1.12; color: #000; }}
/* fixed-height page box + overflow:hidden => Chrome never shrinks-to-fit; overflow is CLIPPED (visible in --check) */
.page {{ column-count: {L["columns"]}; column-gap: {L["column_gap"]}; column-fill: auto; height: {L["page_height"]}; column-rule: 0.35pt solid #777; overflow: hidden; }}
.pb {{ break-after: page; }}
h1 {{ font-size: {L["h1_pt"]}pt; margin: 1.8pt 0 0.7pt; padding-bottom: 0.6pt; border-bottom: 0.9pt solid #000; break-after: avoid; }}
h2 {{ font-size: {L["h2_pt"]}pt; margin: 1.4pt 0 0.4pt; break-after: avoid; color: #0b2d6b; }}
p {{ margin: 0 0 1.2pt; }}
ul {{ margin: 0 0 1.2pt; padding-left: 7pt; }}
li {{ margin: 0; }}
r {{ color: #c00000; font-weight: bold; }}          /* red = exam point / trap / F */
t {{ font-weight: bold; color: #0b5a1e; }}          /* green = T */
b {{ font-weight: bold; }}
k {{ font-family: {L["mono"]}; font-weight: bold; font-size: 0.95em; }}   /* inline code */
y {{ background: #fff2a8; }}                        /* yellow highlight */
.hdr {{ border: 1pt solid #000; padding: 1pt 3pt; margin-bottom: 1.5pt; text-align: center; }}
.hdr .t {{ font-size: 9pt; font-weight: bold; line-height: 1.1; }}
.hdr .t2 {{ font-size: 7.6pt; font-weight: bold; line-height: 1.1; }}
.hdr .s {{ font-size: 5.8pt; }}
pre.code {{ font-family: {L["mono"]}; font-weight: normal; font-size: {L["code_pt"]}pt; line-height: 1.1; background: #f5f7fa; border: 0.4pt solid #a9b4c0; border-left: 2pt solid #2f5fc4; padding: 1.3pt 2.6pt; margin: 1.4pt 0; white-space: pre; break-inside: avoid; color: #111; overflow: hidden; }}
pre.code.pl {{ font-family: {L["mono"]}; }}
.kw {{ color: #0033cc; font-weight: bold; }} .ty {{ color: #7b1fa2; font-weight: bold; }} .cm {{ color: #1b7f3b; font-style: italic; }} .st {{ color: #b3261e; }} .nu {{ color: #c65100; }}
.cr {{ color: #c00000; font-style: italic; font-weight: bold; }} .hl {{ background: #fff2a8; display: inline-block; width: 100%; }} .rl {{ color: #c00000; display: inline-block; width: 100%; }}
table {{ border-collapse: collapse; width: 100%; margin: 1pt 0 1.5pt; font-size: {L["table_pt"]}pt; line-height: 1.1; break-inside: auto; }}
tr {{ break-inside: avoid; }}
th, td {{ border: 0.3pt solid #555; padding: 0.6pt 1.6pt; vertical-align: top; text-align: left; }}
th {{ background: #e8ecf3; font-weight: bold; }}
td.m, th.m {{ font-family: {L["mono"]}; font-weight: bold; font-size: {L["code_pt"] - 0.1}pt; white-space: pre; }}
table.tf td:last-child {{ width: 9pt; text-align: center; font-weight: bold; }}
.two {{ display: flex; gap: 2.5pt; }}
.two > * {{ flex: 1; min-width: 0; }}
.fig {{ text-align: center; margin: 1pt 0; break-inside: avoid; }}
.fig .cap {{ font-size: {L["body_pt"] - 0.2}pt; }}
svg text {{ font-family: {L["serif"]}; }}
.tiny {{ font-size: {L["body_pt"] - 0.4}pt; }}
/* consecutive functions of one snippet: one box, dashed separators, columns may break between them */
pre.code.first {{ margin-bottom: 0; border-bottom: none; }}
pre.code.mid {{ margin-top: 0; margin-bottom: 0; border-top: 0.4pt dashed #b9c2cc; border-bottom: none; padding-top: 2pt; }}
pre.code.last {{ margin-top: 0; border-top: 0.4pt dashed #b9c2cc; padding-top: 2pt; }}
'''

# ----------------------------------------------------------------------------
# Syntax highlighting (C/C++/Java-ish; extend KW/TY per course)
# ----------------------------------------------------------------------------
KW = set("int void bool double char float long class struct public private protected friend virtual template typename return if else while for do new delete NULL nullptr true false this const using namespace break continue operator switch case default static sizeof def import from elif lambda None True False".split())
TY = set("ListNode List TreeNode BinarySearchTree BST Stack Queue Node Animal Dog Cat BeeBooStack Food T queue string cout cin endl vector".split())
TOKEN = re.compile(r'//.*|#.*|"[^"]*"|[A-Za-z_]\w*|\d+|\s+|.')
LINE_LIMIT = LAYOUT_DEFAULTS["code_line_limit"]

def hl_line(line):
    out = []
    for m in TOKEN.finditer(line):
        t = m.group(0); e = html.escape(t)
        if t.startswith('//!'):
            out.append(f'<span class="cr">{html.escape("//" + t[3:])}</span>')   # red comment
        elif t.startswith('//') or (t.startswith('#') and not t.startswith('#include')):
            out.append(f'<span class="cm">{e}</span>')
        elif t.startswith('"'):
            out.append(f'<span class="st">{e}</span>')
        elif t in KW:
            out.append(f'<span class="kw">{e}</span>')
        elif t in TY:
            out.append(f'<span class="ty">{e}</span>')
        elif t.isdigit():
            out.append(f'<span class="nu">{e}</span>')
        else:
            out.append(e)
    return ''.join(out)

def _strip_marks(ln):
    return re.sub(r'^!! |^!R ', '', ln)

def align(block, limit=None, max_col=46):
    """Align trailing // comments of a block on one column when they fit in `limit` chars."""
    limit = limit or LINE_LIMIT
    rows = []
    for ln in block.split('\n'):
        core = _strip_marks(ln); pre = ln[:len(ln) - len(core)]
        if '//' in core and not core.lstrip().startswith('//') and '"' not in core.split('//')[0]:
            code_part, cmt = core.split('//', 1)
            rows.append((pre, code_part.rstrip(), cmt.strip()))
        else:
            rows.append((pre, core, None))
    lens = [len(c) for _, c, m in rows if m is not None]
    target = min(max(lens) + 2, max_col) if lens else 0
    out = []
    for pre, c, m in rows:
        if m is None:
            out.append(pre + c); continue
        if len(c) + 2 <= target and target + 3 + len(m) <= limit:
            out.append(pre + c.ljust(target) + '// ' + m)
        else:
            out.append(pre + c + '  // ' + m)
    return '\n'.join(out)

def _one_block(src, cls, limit):
    lines = []
    for ln in align(src.strip('\n'), limit).split('\n'):
        if ln.startswith('!! '):
            lines.append(f'<span class="hl">{hl_line(ln[3:])}</span>')
        elif ln.startswith('!R '):
            lines.append(f'<span class="rl">{hl_line(ln[3:])}</span>')
        else:
            lines.append(hl_line(ln))
    return f'<pre class="code {cls}">' + '\n'.join(lines) + '</pre>'

def code(src, cls="", limit=None):
    """Render a code snippet. Blank lines split it into separately-breakable boxes
    (one function per box). Line prefixes: '!! ' = yellow key line, '!R ' = red line.
    Comment prefix '//!' = red comment. cls='pl' = plain text (traces, ascii art)."""
    limit = limit or LINE_LIMIT
    blocks = [b for b in src.strip('\n').split('\n\n') if b.strip()]
    if len(blocks) == 1:
        return _one_block(blocks[0], cls, limit)
    out = []
    for i, b in enumerate(blocks):
        c = cls + (' first' if i == 0 else ' mid' if i < len(blocks) - 1 else ' last')
        out.append(_one_block(b, c, limit))
    return ''.join(out)

def long_lines(src, limit=None):
    """Lines of a snippet that would be clipped at the column edge (after alignment)."""
    limit = limit or LINE_LIMIT
    bad = []
    for blk in src.strip('\n').split('\n\n'):
        for ln in align(blk, limit).split('\n'):
            c = _strip_marks(ln)
            if len(c) > limit:
                bad.append((len(c), c))
    return bad

# ----------------------------------------------------------------------------
# Small HTML helpers
# ----------------------------------------------------------------------------
def sec(t):  return f'<h1>{t}</h1>'
def sub(t):  return f'<h2>{t}</h2>'
def fig(svg, cap): return f'<div class="fig">{svg}<div class="cap">{cap}</div></div>'
def header(title, subtitle, legend):
    return (f'<div class="hdr"><div class="t">{title}</div><div class="t2">{subtitle}</div>'
            f'<div class="s">{legend}</div></div>')
def tf_table(rows):
    """rows = [(statement_html, 'T'|'F'), ...] -> one statement per line, F in red."""
    cells = ''.join(f"<tr><td>{q}</td><td>{'<r>F</r>' if a == 'F' else '<t>T</t>'}</td></tr>" for q, a in rows)
    return f'<table class="tf">{cells}</table>'
def steps(*lines):
    """Steps for a complexity example: each Step on its own line; last line = conclusion."""
    return '<br>'.join(lines)
def table(headers, rows, mono_first=False):
    th = ''.join(f'<th{" class=m" if mono_first and i == 0 else ""}>{h}</th>' for i, h in enumerate(headers))
    body = ''
    for r in rows:
        body += '<tr>' + ''.join(f'<td{" class=m" if mono_first and i == 0 else ""}>{c}</td>' for i, c in enumerate(r)) + '</tr>'
    return f'<table><tr>{th}</tr>{body}</table>'

# ----------------------------------------------------------------------------
# Generic tree figure (BST / recursion trees)
# ----------------------------------------------------------------------------
def tree_svg(nodes, edges, width_mm=47, badges=None, highlight=(), notes=(), r=9.5, view=(330, 112)):
    """nodes: {label: (x, y)}, edges: [(a, b)], badges: {label: text} drawn red at top-right,
    highlight: labels drawn pink, notes: [(x, y, text)] blue side notes."""
    s = [f'<svg viewBox="0 0 {view[0]} {view[1]}" width="{width_mm}mm" xmlns="http://www.w3.org/2000/svg">']
    for a, b in edges:
        (x1, y1), (x2, y2) = nodes[a], nodes[b]
        s.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#333" stroke-width="1"/>')
    for k, (x, y) in nodes.items():
        fill = '#ffd2d2' if k in highlight else '#fff8d6'
        s.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="#000" stroke-width="1"/>')
        s.append(f'<text x="{x}" y="{y+3}" font-size="8.5" text-anchor="middle" font-weight="bold">{k}</text>')
        if badges and k in badges:
            s.append(f'<text x="{x+11}" y="{y-5}" font-size="6.5" fill="#c00000">{badges[k]}</text>')
    for x, y, t in notes:
        s.append(f'<text x="{x}" y="{y}" font-size="6.5" fill="#0b2d6b">{t}</text>')
    s.append('</svg>')
    return ''.join(s)

# ----------------------------------------------------------------------------
# Fonts: embed Consolas if it is installed (Word/Excel on macOS, Windows fonts dir)
# ----------------------------------------------------------------------------
FONT_CANDIDATES = [
    "/Applications/Microsoft Word.app/Contents/Resources/DFonts",
    "/Applications/Microsoft Excel.app/Contents/Resources/DFonts",
    "/Applications/Microsoft PowerPoint.app/Contents/Resources/DFonts",
    "/Applications/Microsoft Outlook.app/Contents/Resources/DFonts",
    "C:/Windows/Fonts", os.path.expanduser("~/Library/Fonts"), "/Library/Fonts",
    "/usr/share/fonts", os.path.expanduser("~/.fonts"),
]
FONT_FILES = [("consola.ttf", "normal", "normal"), ("consolab.ttf", "bold", "normal"),
              ("consolai.ttf", "normal", "italic"), ("consolaz.ttf", "bold", "italic")]

def fonts_css():
    css = ""
    for d in FONT_CANDIDATES:
        if not os.path.isdir(d): continue
        found = {}
        for f in os.listdir(d):
            found[f.lower()] = os.path.join(d, f)
        if "consola.ttf" in found:
            for name, w, st in FONT_FILES:
                if name in found:
                    b = base64.b64encode(open(found[name], 'rb').read()).decode()
                    css += f"@font-face {{ font-family: 'ConsolasEmb'; font-weight: {w}; font-style: {st}; src: url(data:font/ttf;base64,{b}) format('truetype'); }}\n"
            return css
    print("[cheatsheet] Consolas not found; code falls back to Consolas/Menlo/DejaVu Sans Mono", file=sys.stderr)
    return ""

# ----------------------------------------------------------------------------
# Assembly + rendering
# ----------------------------------------------------------------------------
def build_html(pages, title, css_extra="", layout=None):
    L = dict(LAYOUT_DEFAULTS); L.update(layout or {})
    css = fonts_css() + base_css(L) + css_extra
    body = ''.join(f'<div class="page{" pb" if i < len(pages) - 1 else ""}">{"".join(p)}</div>' for i, p in enumerate(pages))
    return f'<!doctype html><html><head><meta charset="utf-8"><title>{html.escape(title)}</title><style>{css}</style></head><body>{body}</body></html>'

def find_chrome():
    env = os.environ.get("CHROME")
    if env and os.path.exists(env): return env
    cands = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
             "/Applications/Chromium.app/Contents/MacOS/Chromium",
             "C:/Program Files/Google/Chrome/Application/chrome.exe",
             "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
             os.path.expandvars("%LOCALAPPDATA%/Google/Chrome/Application/chrome.exe")]
    for c in cands:
        if os.path.exists(c): return c
    for c in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome"):
        p = shutil.which(c)
        if p: return p
    sys.exit("Chrome/Chromium not found. Install Google Chrome or set CHROME=/path/to/chrome")

def render_pdf(html_path, pdf_path):
    chrome = find_chrome()
    cmd = [chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
           f"--print-to-pdf={os.path.abspath(pdf_path)}", os.path.abspath(html_path)]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def pdf_pages(pdf_path):
    if shutil.which("pdfinfo"):
        out = subprocess.run(["pdfinfo", pdf_path], capture_output=True, text=True).stdout
        m = re.search(r"Pages:\s+(\d+)", out)
        return int(m.group(1)) if m else -1
    return -1

def rasterize(pdf_path, out_dir, n_pages, columns=3):
    """_check/pg-N.png (whole page, 110 dpi) + _check/zN-cC-rR.png (column halves, 220 dpi)."""
    if not shutil.which("pdftoppm"):
        print("[cheatsheet] pdftoppm (poppler) missing: brew install poppler / apt install poppler-utils", file=sys.stderr)
        return
    os.makedirs(out_dir, exist_ok=True)
    for f in glob.glob(os.path.join(out_dir, "*.png")): os.remove(f)
    subprocess.run(["pdftoppm", "-r", "110", "-png", pdf_path, os.path.join(out_dir, "pg")], check=True)
    W = int(297 / 25.4 * 220); H = int(210 / 25.4 * 220); CW = W // columns; HH = H // 2
    for p in range(1, n_pages + 1):
        for c in range(columns):
            for r in range(2):
                subprocess.run(["pdftoppm", "-r", "220", "-f", str(p), "-l", str(p), "-x", str(c * CW), "-y", str(r * HH),
                                "-W", str(CW), "-H", str(HH), "-png", pdf_path, os.path.join(out_dir, f"z{p}-c{c}-r{r}")], check=True)

def measure(pages, title, css_extra="", layout=None, col_width_mm=94.3):
    """Lay every fragment out in ONE column of the real width and report heights.
    Returns [(page_idx, frag_idx, height_px, text_preview)], column height in px."""
    L = dict(LAYOUT_DEFAULTS); L.update(layout or {})
    css = fonts_css() + base_css(L) + css_extra + f" .page{{column-count:1;height:auto;width:{col_width_mm}mm;overflow:visible}}"
    items = ''.join(f'<div class="it" data-p="{pi}" data-i="{i}">{x}</div>' for pi, p in enumerate(pages) for i, x in enumerate(p))
    js = ('<script>var o=[];document.querySelectorAll(".it").forEach(function(e){o.push(e.dataset.p+":"+e.dataset.i+":"+e.offsetHeight)});'
          'document.body.innerHTML="<pre id=m>"+o.join("|")+"</pre>";</script>')
    doc = f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body><div class="page">{items}</div>{js}</body></html>'
    tmp = os.path.abspath("_measure.html"); open(tmp, "w").write(doc)
    out = subprocess.run([find_chrome(), "--headless=new", "--disable-gpu", "--dump-dom", tmp], capture_output=True, text=True).stdout
    os.remove(tmp)
    m = re.search(r'<pre id="m">(.*?)</pre>', out, re.S)
    res = []
    if m:
        for it in m.group(1).split('|'):
            p, i, h = it.split(':'); res.append((int(p), int(i), int(h)))
    col_h_px = float(re.sub("[^0-9.]", "", L["page_height"])) / 25.4 * 96
    return res, col_h_px
