# Lessons log

One dated entry per mistake that cost a rebuild or a wrong deliverable, with
the fix that was adopted. Newest first. When a fix becomes a rule, it lives in
SKILL.md or the references; this file keeps the history.

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
