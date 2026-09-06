#!/usr/bin/env python3
"""Render binary trees (BST / AVL / heaps / recursion trees) as inline SVG.

Import from a notes-building script:

    from tree_svg import Tree, render, side_by_side

    t = Tree(50, Tree(30, Tree(20), Tree(40)), Tree(70, None, Tree(80)))
    svg = render(t, title="insert 80", highlight={80}, badge={50: "h=2"})
    html = side_by_side([svg_before, svg_after], arrow="rotate left at 30")

Nodes are laid out by inorder position (x) and depth (y), so a BST always
reads left-to-right in sorted order and every subtree is a clean triangle.
Output is a bare <svg> string sized to the tree; drop it inside <figure>.

Conventions (match references/layout.md colour roles):
    default node     blue outline, white fill
    highlight        amber fill      - the node under discussion
    ghost            dashed grey     - a node being removed / a NULL slot
    green            green fill      - result / balanced
    red              red fill        - the violating / changed node
"""

import html as _html

NODE_R = 15          # circle radius
X_GAP = 40           # horizontal distance between consecutive inorder slots
Y_GAP = 52           # vertical distance between depths
FONT = ('font-family="Helvetica Neue,DejaVu Sans,NotoCJK,sans-serif" '
        'font-size="12px"')
SMALL = ('font-family="Helvetica Neue,DejaVu Sans,NotoCJK,sans-serif" '
         'font-size="9px" fill="#5a6675"')
STYLES = {
    "default":   ("#ffffff", "#2a6ba8", "#1c2430"),
    "highlight": ("#ffe1a8", "#e8721c", "#1c2430"),
    "green":     ("#c9f0d6", "#21955c", "#1c2430"),
    "red":       ("#ffd0c9", "#d9432f", "#1c2430"),
    "ghost":     ("#f3f5f8", "#9aa3ad", "#9aa3ad"),
}


class Tree:
    """A node. `key` is shown inside the circle; children may be None."""

    def __init__(self, key, left=None, right=None, elabel=None):
        self.key = key
        self.left = left
        self.right = right
        self.elabel = elabel      # optional text drawn on the edge from the parent

    @staticmethod
    def from_keys(keys):
        """Build a BST by inserting keys in order (duplicates ignored)."""
        root = None
        for k in keys:
            root = _bst_insert(root, k)
        return root


def _bst_insert(t, k):
    if t is None:
        return Tree(k)
    if k < t.key:
        t.left = _bst_insert(t.left, k)
    elif k > t.key:
        t.right = _bst_insert(t.right, k)
    return t


def _layout(t, depth, slot, pos):
    """Assign (x_slot, depth) by inorder traversal. Returns next free slot."""
    if t is None:
        return slot
    slot = _layout(t.left, depth + 1, slot, pos)
    pos[id(t)] = (slot, depth)
    slot += 1
    slot = _layout(t.right, depth + 1, slot, pos)
    return slot


def _depth(t):
    return -1 if t is None else 1 + max(_depth(t.left), _depth(t.right))


def _edges(t, pos, out):
    if t is None:
        return
    for c in (t.left, t.right):
        if c is not None:
            out.append((pos[id(t)], pos[id(c)]))
            _edges(c, pos, out)


def _nodes(t, out):
    if t is None:
        return
    out.append(t)
    _nodes(t.left, out)
    _nodes(t.right, out)


def render(t, title=None, highlight=(), green=(), red=(), ghost=(),
           badge=None, null_slots=(), width=None, note=None, scale=1.0):
    """Return an <svg> string.

    highlight / green / red / ghost : iterables of keys to colour
    badge      : {key: "text"} drawn to the upper-right of the node
                 (use for heights, ranks, balance factors)
    null_slots : iterable of (parent_key, "L"|"R") - draws a dashed empty
                 box where a child would be inserted
    note       : one line of small text under the tree
    scale      : shrink the drawn size (viewBox unchanged) so several panels
                 fit side by side; 0.7 fits two 11-node trees on an A4 line
    """
    pos = {}
    slots = _layout(t, 0, 0, pos)
    d = _depth(t)
    # badges hang to the upper-right of a node; the rightmost node's badge
    # needs room past the last slot or it is clipped by the viewBox
    w = width or max(slots * X_GAP + 20 + (36 if badge else 0), 120)
    h = (d + 1) * Y_GAP + 30 + (16 if title else 0) + (14 if note else 0)
    top = 16 + (16 if title else 0)
    badge = badge or {}

    def xy(p):
        return (10 + p[0] * X_GAP + X_GAP / 2, top + p[1] * Y_GAP + NODE_R)

    parts = [f'<svg viewBox="0 0 {w:.0f} {h:.0f}" width="{w*scale:.0f}" height="{h*scale:.0f}" '
             'xmlns="http://www.w3.org/2000/svg">']
    if title:
        parts.append(f'<text x="{w/2:.0f}" y="13" text-anchor="middle" {FONT} '
                     f'font-weight="700" fill="#123a63">{_html.escape(str(title))}</text>')
    edges = []
    _edges(t, pos, edges)
    for a, b in edges:
        (x1, y1), (x2, y2) = xy(a), xy(b)
        parts.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                     'stroke="#5a6675" stroke-width="1.4"/>')
    # edge labels (child.elabel), drawn beside the midpoint, offset away from the edge
    def _elabels(n):
        if n is None:
            return
        for c in (n.left, n.right):
            if c is not None and getattr(c, "elabel", None):
                (x1, y1), (x2, y2) = xy(pos[id(n)]), xy(pos[id(c)])
                mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                side = -1 if c is n.left else 1
                parts.append(f'<text x="{mx + side*9:.1f}" y="{my - 3:.1f}" '
                             f'text-anchor="{"end" if side < 0 else "start"}" {SMALL} '
                             f'fill="#d9432f">{_html.escape(str(c.elabel))}</text>')
            _elabels(c)
    _elabels(t)
    # dashed NULL slots
    by_key = {}
    nodes = []
    _nodes(t, nodes)
    for n in nodes:
        by_key[n.key] = n
    for pk, side in null_slots:
        p = by_key.get(pk)
        if p is None:
            continue
        (px, py) = xy(pos[id(p)])
        dx = -X_GAP * 0.6 if side == "L" else X_GAP * 0.6
        cx, cy = px + dx, py + Y_GAP
        parts.append(f'<line x1="{px:.1f}" y1="{py:.1f}" x2="{cx:.1f}" y2="{cy:.1f}" '
                     'stroke="#9aa3ad" stroke-width="1.2" stroke-dasharray="3,3"/>')
        parts.append(f'<rect x="{cx-12:.1f}" y="{cy-10:.1f}" width="24" height="20" rx="4" '
                     'fill="#f3f5f8" stroke="#9aa3ad" stroke-dasharray="3,3"/>')
        parts.append(f'<text x="{cx:.1f}" y="{cy+4:.1f}" text-anchor="middle" {SMALL}>∅</text>')
    for n in nodes:
        k = n.key
        style = ("highlight" if k in highlight else "green" if k in green
                 else "red" if k in red else "ghost" if k in ghost else "default")
        fill, stroke, textc = STYLES[style]
        (x, y) = xy(pos[id(n)])
        dash = ' stroke-dasharray="4,3"' if style == "ghost" else ""
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{NODE_R}" fill="{fill}" '
                     f'stroke="{stroke}" stroke-width="1.8"{dash}/>')
        parts.append(f'<text x="{x:.1f}" y="{y+4.5:.1f}" text-anchor="middle" {FONT} '
                     f'font-weight="700" fill="{textc}">{_html.escape(str(k))}</text>')
        if k in badge:
            parts.append(f'<text x="{x+NODE_R+2:.1f}" y="{y-NODE_R+4:.1f}" {SMALL} '
                         f'fill="#b3541e">{_html.escape(str(badge[k]))}</text>')
    if note:
        parts.append(f'<text x="{w/2:.0f}" y="{h-4:.0f}" text-anchor="middle" {SMALL}>'
                     f'{_html.escape(note)}</text>')
    parts.append('</svg>')
    return "\n".join(parts)


def side_by_side(svgs, arrow=None, gap=18):
    """Wrap several SVG strings in a flex row, optionally with a labelled arrow
    between consecutive panels. Returns an HTML string for <figure>."""
    cells = []
    for i, s in enumerate(svgs):
        cells.append(f'<div style="flex:0 0 auto">{s}</div>')
        if arrow is not None and i < len(svgs) - 1:
            label = arrow if isinstance(arrow, str) else arrow[i]
            cells.append(
                '<div style="flex:0 0 auto;align-self:center;text-align:center;'
                'font-size:9px;color:#123a63;padding:0 4px">'
                f'<div style="font-size:20px;line-height:1">→</div>{_html.escape(label)}</div>')
    return (f'<div style="display:flex;gap:{gap}px;justify-content:center;'
            'align-items:flex-start;flex-wrap:wrap">' + "".join(cells) + '</div>')


if __name__ == "__main__":
    t = Tree.from_keys([50, 30, 70, 20, 40, 80])
    print(render(t, title="BST", highlight={40}, badge={50: "h=2", 30: "h=1"},
                 null_slots=[(70, "L")], note="inorder = 20 30 40 50 70 80"))
