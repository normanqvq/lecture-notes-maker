# lecture-notes-maker

A Claude skill that turns lecture slides and course PDFs into a dense,
print-ready **study-notes PDF** — the kind you read during the semester, not the
one-page cheatsheet you smuggle into the exam hall.

## What it does

- **Default output**: A4 portrait PDF, single column, ~9.4 pt, dark
  syntax-highlighted code blocks, hand-authored inline SVG diagrams
- **Subject-agnostic**: a catalogue of presentation patterns maps content
  *shapes* (sequences, state traces, bit-fields, taxonomies, state machines,
  layered stacks) to the layout that serves each one — so it works the same for
  a computer-architecture deck, an organic-chemistry deck, or a finance deck
- **Verifies before writing**: reads the actual source material and refuses to
  generate from memory — no source, no notes
- **Finds the gaps**: detects removed answer pages (slide numbering that jumps)
  and hunts them down in sibling decks before falling back to solving them
- **Four margin tags**, kept visually distinct from the body so you always know
  what came from the slides and what didn't:
  - `SUPP` — what the slides simplified away
  - `TRAP` — the specific way people get this wrong, with the counter-example
    that breaks the wrong mental model
  - `EXAM` — phrasing the marking scheme is likely to use
  - `ERRATUM` — the slides are wrong, here's what's correct
- **Traces every worked example** step by step with full intermediate state,
  not just the final answer
- **Self-checks the layout**: rasterises the PDF into contact sheets so
  overlapping labels and stranded headings get caught before delivery
- Ends with a one-page quick-reference table and a self-test

## Output language

English by default. Ask for another language and it switches to bilingual mode —
explanation in your language, technical terms kept in the original.

## Install

```bash
git clone https://github.com/<you>/lecture-notes-maker
cp -r lecture-notes-maker ~/.claude/skills/
```

Then just upload your lecture PDF and ask for notes.

## Requirements

```bash
pip install weasyprint pillow
```

On Windows, WeasyPrint also needs the GTK3 runtime
(`winget install tschoonj.GTKForWindows`), otherwise importing it fails with
`cannot load library 'libgobject-2.0-0'`.

`--check` (the visual verification step) requires **poppler** for `pdftoppm`.
This is a hard dependency of `--check`, not an optional extra — without it the
build exits non-zero rather than skipping the inspection:

```bash
winget install oschwartz10612.Poppler   # Windows
brew install poppler                    # macOS
apt install poppler-utils               # Linux
```

## Manual use

The build script works standalone if you want to write the HTML yourself:

```bash
python assets/build.py \
  --parts parts/ \
  --css assets/notes.css \
  --out notes.pdf \
  --footer "CG2028 · Lecture 2" \
  --check
```

Code blocks are marked `<pre class="code" data-lang="python">`. Run
`python assets/build.py --list-langs` to see the available profiles (arm, c,
python, sql, verilog, generic). An unknown language falls back to `generic`, which still
colours comments, strings and numbers. Adding a language means appending one
entry to `PROFILES` at the top of `build.py`.

## Layout

```
SKILL.md                    the workflow and the non-negotiable rules
references/
  content-rules.md          when each tag applies, with worked examples
  patterns.md               content shape -> presentation pattern catalogue
  layout.md                 page, figure, and table conventions
assets/
  notes.css                 stylesheet
  build.py                  highlighter + WeasyPrint renderer + visual check
```

## Not what you want?

If you need a **compressed exam cheatsheet** — formulas only, multi-column
landscape, maximum density — that's a different artifact with different rules.
This skill optimises for reading and understanding, and will tell you so.

## Note on source material

The skill reads your course material to produce your notes. Both the input and
the output are your instructor's intellectual property — keep them out of public
repositories.

## License

MIT
