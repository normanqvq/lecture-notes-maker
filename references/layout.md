# Layout conventions

## Page

A4 portrait, single column, ~13 mm margins, base font ~9.4 pt. Running footer
carries the course and lecture identifier plus `page / total`; suppressed on the
cover.

CJK text is set in Noto Sans CJK SC embedded from `assets/fonts/` (see
SKILL.md Step 6); Latin text falls back to Helvetica Neue / DejaVu Sans.

Single column is deliberate. Multi-column looks denser but breaks wide tables
and forces figures to postage-stamp size, and study notes are read linearly.

## Headings

- `h2` — numbered section, full-width dark bar. Matches the source's own
  numbering so the reader can cross-reference the slides.
- `h3` — subsection, orange left rule.
- `h4` — minor heading inside a subsection.

Every heading carries `page-break-after: avoid` so it never strands at a page
bottom.

Add `class="pb"` to force a page break before a major section. Use sparingly —
each one costs whitespace. After the first full build, check the rasters and
remove any `pb` that produced more than about a third of a page of blank space.

## Code blocks

```html
<pre class="asm">…</pre>     <!-- syntax highlighted -->
<pre class="asm sm">…</pre>  <!-- one step smaller, for wide listings -->
<pre class="plain">…</pre>   <!-- no highlighting -->
```

`asm` is shorthand for `class="code" data-lang="arm"` — the general form in
SKILL.md Step 6. Other languages use that form: `<pre class="code"
data-lang="c">`, etc.

Dark background, orange left rule, `page-break-inside: avoid`.

Always comment the listing line by line in the target language. An
uncommented listing is decoration.

## Tables

`class="tight"` reduces cell padding for dense reference tables.

Add `class="mono"` to cells holding code, addresses, or register names.

Tables are `page-break-inside: avoid`, so a table taller than the space left on
the page jumps to the next one whole and strands what it left behind. For a long
reference table add `class="flow"` and put the header row in `<thead>`: it then
breaks normally and the header repeats on each page. Check the rasters — a table
short enough to fit does not need it.

Use `<span class="ok">✔</span>` / `<span class="no">✘</span>` for yes/no
columns rather than the words.

## Callout boxes

```html
<div class="box ana"><b>类比：</b>…</div>                       <!-- yellow: analogy -->
<div class="box key"><span class="tag">KEY</span> …</div>       <!-- green: rule to memorise -->
<div class="box trap"><span class="tag">TRAP</span> …</div>     <!-- red: common mistake -->
<div class="box exam"><span class="tag">EXAM</span> …</div>     <!-- amber: source-flagged, may carry ▶ timestamp -->
<div class="box supp"><span class="tag">SUPP</span> …</div>     <!-- blue: rare -->
<div class="box err"><span class="tag">ERRATUM</span> …</div>   <!-- purple: rare -->
```

The analogy box carries no tag chip — a bold `类比：` / `Analogy:` lead-in is
enough, and the yellow is its identity. The three colours the reader is told
to rely on are yellow = picture it, green = memorise it, red = do not do this;
put that legend in one line on the cover strip.

Boxes may contain tables and code blocks. They are `page-break-inside: avoid`,
so a box longer than about a third of a page will force an awkward break —
split it or move it into the body.

## Section openers

Each `h2`/`h3` is followed by one sentence stating the question the section
answers, before any definition. The `h3` may carry the slide reference in its
`<span class="sub">` (`§3.3 · p.23`). Definitions are plain paragraphs that
begin with `<b>定义：</b>`; do not box them.

## Dialogue tables

Worked examples use a three-column `table.tight`: what is on the wire (mono),
who, what it means (the spoken line). Bold the step people get wrong. Keep
one such table per example; do not add a byte-by-byte trace of the same
sequence.

## Figures

Inline SVG inside `<figure>`, with a `<figcaption>` stating what the figure
shows — not repeating its title.

**Sizing.** `viewBox="0 0 700 H"` with `style="width:98%;height:auto"`. Pick H
so the aspect ratio matches the content; do not pad with empty space.

**Preventing the two defects that actually occur:**

1. *Connector lines crossing labels.* Reserve a rectangle for every text label
   and route connectors around it. If a connector must span the figure, run it
   through a lane that contains no text.
2. *Text overflowing its box.* SVG does not wrap or clip by default. Count
   characters: at 9.5 px, roughly 5.5 px per Latin character and 9.5 px per CJK
   character. Widen the box or shorten the label.

**Preferred idiom.** Instead of one figure with many curved arrows, use a row of
numbered step cards, each self-contained. Easier to read and structurally
impossible to overlap.

**Colour roles.** Blue = neutral/structural. Amber = the element under
discussion. Green = result or "unchanged". Red = the address or value that
changed. Keep this consistent across all figures in one document.

## Rhythm

Alternate prose → table → figure → code. Three consecutive tables read as a
spec sheet; three consecutive prose paragraphs get skipped.

Roughly one figure per major subsection. A subsection with no spatial,
sequential, or state-transition content does not need one.
