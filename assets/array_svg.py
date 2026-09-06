#!/usr/bin/env python3
"""Render an array as a row of cells with pointers and colour bands — for
partition / merge / binary-search traces.

    from array_svg import render_array, stack_rows

    svg = render_array([22, 35, 10, 42, 7, 51, 18, "∞"],
                       pointers={1: "low", 7: "high"},
                       highlight={0}, green=range(0, 0), red={1, 6},
                       title="swap 35 ↔ 18", index_base=1)
    html = stack_rows([svg1, svg2, svg3])      # one trace, rows stacked

Colour roles: highlight (amber) = pivot / element under discussion,
green = settled / known-correct, red = the two cells about to change,
ghost = sentinel or unused slot.
"""

import html as _html

CELL_W = 34
CELL_H = 26
FONT = ('font-family="Menlo,DejaVu Sans Mono,NotoCJK,monospace" '
        'font-size="12px"')
SMALL = ('font-family="Helvetica Neue,DejaVu Sans,NotoCJK,sans-serif" '
         'font-size="9px"')
STYLES = {
    "default":   ("#ffffff", "#2a6ba8"),
    "highlight": ("#ffe1a8", "#e8721c"),
    "green":     ("#c9f0d6", "#21955c"),
    "red":       ("#ffd0c9", "#d9432f"),
    "ghost":     ("#f3f5f8", "#9aa3ad"),
}


def render_array(cells, pointers=None, highlight=(), green=(), red=(), ghost=(),
                 title=None, index_base=0, show_index=True, label=None):
    """cells: list of values. pointers: {index: "name"} drawn as arrows below.
    Indices in every argument are 0-based positions in `cells`; index_base only
    changes the printed index row."""
    pointers = pointers or {}
    n = len(cells)
    left = 10 + (70 if label else 0)
    top = 14 + (16 if title else 0)
    w = left + n * CELL_W + 10
    h = top + CELL_H + (14 if show_index else 0) + (26 if pointers else 0) + 6
    parts = [f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
             'xmlns="http://www.w3.org/2000/svg">']
    if title:
        parts.append(f'<text x="{left}" y="12" {SMALL} font-weight="700" fill="#123a63">'
                     f'{_html.escape(str(title))}</text>')
    if label:
        parts.append(f'<text x="{left-6}" y="{top+CELL_H/2+4}" text-anchor="end" {SMALL} '
                     f'fill="#5a6675">{_html.escape(str(label))}</text>')
    for i, v in enumerate(cells):
        style = ("highlight" if i in highlight else "green" if i in green
                 else "red" if i in red else "ghost" if i in ghost else "default")
        fill, stroke = STYLES[style]
        x = left + i * CELL_W
        parts.append(f'<rect x="{x}" y="{top}" width="{CELL_W}" height="{CELL_H}" '
                     f'fill="{fill}" stroke="{stroke}" stroke-width="1.4"/>')
        parts.append(f'<text x="{x+CELL_W/2}" y="{top+CELL_H/2+4.5}" text-anchor="middle" '
                     f'{FONT} font-weight="700" fill="#1c2430">{_html.escape(str(v))}</text>')
        if show_index:
            parts.append(f'<text x="{x+CELL_W/2}" y="{top+CELL_H+11}" text-anchor="middle" '
                         f'{SMALL} fill="#9aa3ad">{i+index_base}</text>')
    py = top + CELL_H + (14 if show_index else 0)
    for i, name in pointers.items():
        x = left + i * CELL_W + CELL_W / 2
        parts.append(f'<path d="M{x},{py+2} L{x-5},{py+10} L{x+5},{py+10} z" fill="#d9432f"/>')
        parts.append(f'<text x="{x}" y="{py+22}" text-anchor="middle" {SMALL} '
                     f'fill="#d9432f" font-weight="700">{_html.escape(str(name))}</text>')
    parts.append('</svg>')
    return "\n".join(parts)


def stack_rows(svgs, gap=4):
    return (f'<div style="display:flex;flex-direction:column;gap:{gap}px;'
            'align-items:flex-start">' + "".join(f'<div>{s}</div>' for s in svgs) + '</div>')


if __name__ == "__main__":
    print(render_array([22, 35, 10, 42, 7, 51, 18, "∞"], pointers={1: "low", 7: "high"},
                       highlight={0}, ghost={7}, title="pivot = 22", index_base=1))
