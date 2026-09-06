#!/usr/bin/env python3
"""Second-renderer check: rasterise a PDF with PDFium (the engine inside
Chrome / Edge) so font-embedding defects that poppler hides become visible.

    python assets/render_check.py notes.pdf            # all pages
    python assets/render_check.py notes.pdf --pages 1,3

Writes _check/pdfium-pg-NN.png next to the PDF and lists the embedded fonts.
Cross-platform; needs `pip install pypdfium2`. On macOS `qlmanage -t` is an
additional Quartz check, but this script is the one that works everywhere.
"""

import argparse
import os
import sys


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("pdf")
    ap.add_argument("--pages", default="", help="comma-separated 1-based page numbers")
    ap.add_argument("--scale", type=float, default=1.5, help="render scale (1.0 = 72 dpi)")
    args = ap.parse_args()

    try:
        import pypdfium2 as pdfium
    except ImportError:
        sys.exit("render_check: pypdfium2 is not installed - run: pip install pypdfium2")

    if not os.path.exists(args.pdf):
        sys.exit(f"render_check: no such file: {args.pdf}")

    out_dir = os.path.join(os.path.dirname(os.path.abspath(args.pdf)), "_check")
    os.makedirs(out_dir, exist_ok=True)

    doc = pdfium.PdfDocument(args.pdf)
    n = len(doc)
    wanted = ([int(x) for x in args.pages.split(",") if x.strip()]
              if args.pages else list(range(1, n + 1)))
    for i in wanted:
        if not 1 <= i <= n:
            sys.exit(f"render_check: page {i} out of range 1..{n}")
        img = doc[i - 1].render(scale=args.scale).to_pil()
        path = os.path.join(out_dir, "pdfium-pg-%02d.png" % i)
        img.save(path)
        print("rendered", path)

    # Font inventory: anything from the macOS system CJK families means the
    # build fell back past the bundled Noto fonts and will look wrong in
    # Quartz viewers even if these rasters happen to look fine.
    fonts = set()
    import ctypes
    import pypdfium2.raw as raw
    get_name = (getattr(raw, "FPDFFont_GetBaseFontName", None)
                or getattr(raw, "FPDFFont_GetFontName"))
    for i in range(n):
        for obj in doc[i].get_objects(max_depth=2):
            if obj.type != raw.FPDF_PAGEOBJ_TEXT:
                continue
            try:
                font = raw.FPDFTextObj_GetFont(obj)
                size = get_name(font, None, 0)
                buf = ctypes.create_string_buffer(size)
                get_name(font, buf, size)
                fonts.add(buf.value.decode(errors="replace"))
            except Exception:
                pass
    if fonts:
        print("embedded fonts:", ", ".join(sorted(fonts)))
        bad = [f for f in fonts if "PingFang" in f or "Hiragino" in f]
        if bad:
            print("WARNING: macOS system CJK fonts present - rebuild with the "
                  "bundled Noto fonts (python assets/get_fonts.py):", ", ".join(bad))
            sys.exit(1)
    print("ok - open the pdfium-pg-NN.png files and confirm every glyph is present")


if __name__ == "__main__":
    main()
