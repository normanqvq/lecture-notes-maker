---
name: lecture-notes-maker
description: Turn lecture slides, textbook chapters, or course PDFs into a dense, print-ready study-notes PDF with syntax-highlighted code, hand-authored SVG diagrams, worked-example traces, and margin tags for gaps/traps/exam-points/errata. Use when the user asks for study notes, revision notes, or a "notes PDF" from uploaded course material. Not for exam cheatsheets — see cheatsheet-style skills for that.
---

# Lecture Notes Maker

Produces an A4 study-notes PDF from source course material. Optimizes for
**understanding**, not for cramming density — dense, but every line readable.

## Non-negotiable rules

1. **Never generate notes from memory.** If the user has not supplied the
   lecture material, stop and ask for it. A confident-looking PDF full of
   plausible-but-wrong content is worse than no PDF.
2. **Verify every claim against the source before writing it.** Read the actual
   slides. Quote-check numbers, register names, addresses, and code.
3. **Rasterize and visually inspect the output before delivering.** Layout bugs
   (overlapping SVG labels, text overflowing boxes, orphaned headings) are
   invisible in HTML and obvious in the rendered page.

## Output language

Default: **English**.

If the user writes in another language or explicitly requests one, switch to
**bilingual mode**: explanation in the target language, technical terms kept in
the source language on first use, e.g. `有效地址 (Effective Address, EA)`.
Never translate mnemonics, API names, or code.

## Workflow

### Step 1 — Inventory the source

Read the material end to end before writing anything. Produce (internally) a
map of: section numbers, slide/page ranges, worked examples, and figures.

Then check for **gaps**:

- Slide numbering that jumps (e.g. 28 → 30) usually means the instructor
  removed answer pages from the student handout.
- Look for the missing pages in sibling files — decks that share continuous
  page numbering often carry the previous deck's answers at the front.
- If genuinely unavailable, solve the exercise yourself and mark it clearly as
  a derived answer, not the official one.

### Step 2 — Separate the two layers

Every section splits into:

- **What the slides say** — goes in the body. Follow the source's own section
  numbering so the reader can cross-reference.
- **What the slides omit but the reader will hit anyway** — goes in a tagged
  callout box, never silently merged into the body.

Keeping these visually distinct is the single biggest quality lever. A reader
studying for a closed-book exam needs to know which parts are examinable
material and which are your additions.

### Step 3 — Tag the callouts

Four types. See `references/content-rules.md` for the full criteria and
worked examples of each.

| Tag | Meaning | Use when |
|---|---|---|
| **SUPP** | Supplementary | Real-world detail the slides simplified away |
| **TRAP** | Common mistake | A specific way readers get this wrong |
| **EXAM** | Likely assessed | Phrasing or fact that shows up in questions |
| **ERRATUM** | Source error | The slides are factually wrong or have a typo |

Discipline matters more than volume. A TRAP box that just restates the body
text trains the reader to skip all the boxes.

### Step 4 — Trace every worked example

Do not present only the final answer. For each example, produce a table with
one row per step showing the **full intermediate state** — registers, memory,
flags, variables, whichever applies.

Where the source gives an official answer, reproduce it and mark it as such.
Then, separately, explain *why* — including which step is the one people get
wrong.

### Step 5 — Choose the presentation, then draw it

Before drawing anything, identify what **shape** the content has — a sequence,
a state evolution, a packed bit-field, a comparison, a hierarchy, a state
machine, a layered stack. `references/patterns.md` maps each shape to the
layout that serves it. Match the shape of the content, not the name of the
subject.

Most content is better served by a table than a figure. A figure earns its
space only when the content has spatial, sequential, or topological structure
that a table would flatten.

When a figure is warranted, hand-author inline SVG. Do not use chart libraries
or clip art.

Rules that prevent the most common defects:

- Give every text label its own reserved rectangle; never let a connector line
  pass through a label.
- Prefer short straight connectors between adjacent boxes over long curved
  paths that cross the figure.
- Keep labels under ~14 characters, or widen the box.
- Use a single arrowhead marker definition and reuse it.
- Solid arrows for "points to"; dashed for "copies into".

See `references/layout.md` for figure sizing and placement conventions.

### Step 6 — Build

Write the notes as HTML fragments (`parts/part1.html`, `part2.html`, …), then:

```bash
python assets/build.py --parts parts --css assets/notes.css --out notes.pdf
```

`build.py` concatenates the parts, runs the code-block syntax highlighter,
injects the stylesheet, and renders with WeasyPrint.

Mark up code as:

```html
<pre class="code" data-lang="python">…</pre>
<pre class="plain">…</pre>          <!-- no highlighting -->
```

Run `python assets/build.py --list-langs` for the available profiles
(currently arm, c, python, sql, verilog, generic). An unknown or omitted `data-lang`
falls back to `generic`, which still colours comments, strings and numbers, so
an unsupported language degrades gracefully rather than breaking.

To add a language properly, append one entry to `PROFILES` at the top of
`build.py`. Nothing else needs changing.

### Step 7 — Verify visually

```bash
python assets/build.py --parts parts --css assets/notes.css --out notes.pdf --check
```

This writes page rasters and contact sheets next to the PDF. **Look at them.**
Fix any overlapping labels, boxes with text spilling out, or headings stranded
at a page bottom, then rebuild.

Only deliver after the contact sheets look clean.

`--check` requires **poppler** (`pdftoppm`) in addition to the pip packages. It
is a hard dependency, not an optional extra: if `pdftoppm` is missing, the build
exits non-zero with an install hint instead of quietly skipping the check. A
build that cannot be inspected is not a build that can be delivered.

```bash
winget install oschwartz10612.Poppler   # Windows
brew install poppler                    # macOS
apt install poppler-utils               # Linux
```

## Structure of the finished document

1. **Cover** — course, lecture number, coverage (state explicitly which pages,
   and whether any were reconstructed), and what conventions the notes use.
2. **The Big Picture** — one page. What questions does this lecture answer?
   A map figure showing how the sections connect and where they get used later.
3. **Body** — mirrors the source's section numbering.
4. **Worked examples** — every exercise, fully traced.
5. **Supplement** — the omissions collected: adjacent material, common build
   errors, a minimal working template if the subject involves code.
6. **One-page reference + self-test** — a "you want to do X, write Y" table,
   then 10–15 questions with answers.

## Scope

This skill makes **study notes**. If the user wants a compressed exam
cheatsheet — maximum density, formulas only, multi-column landscape — that is a
different artifact with different rules. Say so and ask which they want.
