# Lessons log

One dated entry per mistake that cost a rebuild or a wrong deliverable, with
the fix that was adopted. Newest first. When a fix becomes a rule, it lives in
SKILL.md or the references; this file keeps the history.

## 2026-09-11 — Cheatsheet mode: CS2040C Quiz 1 (two A4 sides, ~5 pt)

- **Chrome print silently shrank the whole document.** Content overflowed the
  3-column page box and "shrink-to-fit" scaled every page ~0.9×; the PDF
  looked fine but the fonts were smaller than the CSS said. Fix: `.page {
  overflow: hidden }` in `cheatsheet.py` — overflow is clipped and shows up in
  `--check` instead of being hidden by scaling.
- **A 90-line `<pre>` with `break-inside: avoid` jumped to the next column**
  and left two thirds of a column empty. Fix: `code()` splits a snippet at
  blank lines into one box per function (dashed separators); wrapping the
  pieces in a `<div>` made Chrome move the group as a unit again, so they are
  emitted as siblings.
- **Code lines vanished at the column edge without warning** (`white-space:
  pre` + clipping). Fix: `code_line_limit` (78 chars at 3 columns / Consolas
  5 pt; Menlo fits only ~74) enforced by `align()` and reported by the builder
  after every build.
- **Cutting "by eye" never converged.** Fix: `--measure` lays every fragment
  out in one real-width column and prints its height as a fraction of a
  column; a side holds 3.00 minus ~0.1 for break waste.
- **The user rejected cramped code and fact-paragraphs twice** ("代码挤在一起",
  five facts in one paragraph). Now rules in `cheatsheet-rules.md`: Consolas
  normal weight, italic green comments aligned in one column, one fact / T-F
  statement / Step per line, F red, T green.
- **Consolas is not a macOS system font**; it ships inside Microsoft Office
  (`…/Microsoft Word.app/Contents/Resources/DFonts/consola*.ttf`).
  `fonts_css()` embeds it as base64 when found (never commit the TTFs).
- **Every added line must come from somewhere.** A two-line title pushed the
  last worked example off the sheet; `<sup>` bumps line boxes (use ᵈ ⁿ ²);
  figure width is the cheapest space lever (58 → 46 mm freed a table row).
  After any edit look at the bottom of the last column of each side.

## 2026-09-11 — CG2028 Lecture 6 (Panopto, three recordings)

- **Whisper locked into a loop mid-file** ("the stop condition is detected
  on the bus" × 600) from 12:25 to the end of a 27-minute recording; the
  compact transcript silently jumped from 12:25 to 26:55. Fix: re-ran that
  span with `-mc 0 -et 2.4` and offset the timestamps; `extract_video.py`
  now passes `-mc 0`, and Step 1 says to check that a repeat does not run to
  the end of the file.
- **`python3` had no WeasyPrint** on this machine; the working recipe is
  `DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib uv run --with weasyprint
  --with pillow --with pypdfium2 python assets/build.py …` (brew pango/glib
  present, no venv). Not a skill rule, but it cost two false starts.
- **A six-row reference table jumped whole to the next page** and left a
  quarter of the page blank; `class="tight flow"` + `<thead>` fixed it. A
  table that follows a heading near a page bottom should get `flow` on the
  first build rather than after the raster.
- **Scene detection kept a single frame from the 6.1 video** even at
  `--scene 0.012`; the deck was the content source so nothing was lost, but
  a talking-head-plus-static-slide recording gives no frame timeline —
  timestamps then come from the transcript alone.

## 2026-09-06 — CS2040C L04b–L06a (seven YouTube lectures, 6.5 h of video)

- **Background task limit killed the transcription pipeline.** A `run_in_background`
  Bash task is capped at ten minutes like a foreground one, and killing it
  killed the whisper children. Fix: launch long extractions with `nohup … &`
  from a normal command and poll; documented in Step 1.
- **Seven whisper processes at once on a 24 GB machine** worked but pegged all
  cores for ~40 min. Fix: cap at three concurrent, budget a third of the
  recording length each.
- **Nested double quotes in generated captions** (`"slide "Search Max""`)
  broke the parts generator twice. Fix: captions quote slide titles with 「」;
  rule added to layout.md.
- **Side-by-side tree panels wrapped vertically** because two 11-node trees
  exceed the ~700 px column, leaving a third of the page empty. Fix: `scale=`
  parameter on `tree_svg.render`; width rule in Step 5.
- **Three-panel rotation figure** never fits one line. Fix: split into two
  before/after figures sharing the middle state; rule in patterns.md §5.
- **Height badge on the rightmost node clipped by the viewBox** — only visible
  in the detail pass at scale 1.6, not on contact sheets. Fix: `tree_svg`
  adds 36 px of right padding when badges are present; Step 7 now requires
  a high-resolution look at figure-heavy pages.
- **Three forced page breaks** (`class="pb"` on §1, §4, and the Big Picture
  heading) each stranded a third of a page. Fix: none of the section
  headings carry `pb` by default; add one only after seeing the raster.
- **`rank` as a C++ function name** collides with `std::rank` under
  `using namespace std`. Not a skill rule, but the generated code file now
  says why it is called `rankOf`.
- **Whisper hallucination loops** over quiz time ("Let's see what is going on
  here" × 40) inflated one transcript. Fix: note in Step 1 to skip repeated
  lines.

## 2026-09-05 — CG2028 Lecture 5 (Panopto, three recordings)

- **macOS system CJK fonts (PingFang / Hiragino) embed as garbage** in
  Quartz-based viewers while poppler renders them fine, so `--check` passed
  and the user saw 乱码. Fix: bundled Noto Sans CJK via `@font-face`,
  `build.py` refuses CJK content without the fonts, and a second renderer
  (`render_check.py`, PDFium) is mandatory before delivery.
- **Default scene threshold (0.08) kept 6 frames from a 24-minute deck** with
  white slides and soft transitions. Fix: re-run with `--scene 0.012`; hint
  in Step 1.
- **17-page slide-by-slide transcription** was rejected as too long. Fix: the
  whole skill was rewritten around 5–7 pages per lecture, definition →
  analogy → rule/trap, examples as dialogues, no glossary appendix.
- **Chinese-only terms** left the reader unable to map to the English exam
  vocabulary. Fix: bilingual mode brackets the English term at first use in
  every section.
