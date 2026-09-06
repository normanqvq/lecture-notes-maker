---
name: lecture-notes-maker
description: Turn lecture slides, course PDFs, or lecture recordings (video) into a short, print-ready revision-notes PDF — one lecture in roughly 5–7 A4 pages, each key point written as definition → everyday analogy → rule/trap, worked examples as step-by-step dialogues, ending with a self-check. Use when the user asks for study notes, revision notes, 重点笔记, or a "notes PDF" from uploaded course material. Not for exhaustive transcriptions of the slides and not for one-page exam cheatsheets.
---

# Lecture Notes Maker

Produces an A4 revision-notes PDF from source course material. The reader should
be able to grasp the whole lecture's key points in about **20 minutes**. This is
**not** a transcription of the slides: the deliverable is the third of the
material that the exam and the labs actually turn on, written so it sticks.

## Non-negotiable rules

1. **Never generate notes from memory.** If the user has not supplied the
   lecture material, stop and ask for it. A confident-looking PDF full of
   plausible-but-wrong content is worse than no PDF.
2. **Verify every claim against the source before writing it.** Read the actual
   slides. Quote-check numbers, register names, addresses, and code.
3. **Rasterize and visually inspect the output before delivering**, with two
   different renderers (Step 7). Layout bugs and font-embedding bugs are
   invisible in HTML and obvious in the rendered page.
4. **Short beats complete.** The test for every paragraph is: *if this were
   deleted, would the reader be missing something when solving a question or
   revising?* If not, it goes. Do not keep background material "for
   completeness".

## Output language

Default: **English**.

If the user writes in another language or explicitly requests one, switch to
**bilingual mode**: explanation in the target language, technical terms kept in
English on first use in each section, e.g. `上拉电阻 (pull-up resistor)`,
`第 9 拍 (9th clock pulse)`. Exams are in English, so every examinable term must
carry its English form where it is explained — a Chinese-only phrase the reader
cannot map back to the English term is useless in the exam hall. Never translate
mnemonics, API names, register names, or code.

## Length

- Target: **about 5–7 A4 pages per lecture** — roughly a third of a
  slide-by-slide transcription. This is a target, not a cap: do not delete
  something necessary to hit it, and do not pad to reach it.
- Every section opens with **one sentence saying what question this section
  answers** (e.g. *"Open-drain and pull-up — why several chips can share one
  wire without fighting"*). A section for which that sentence cannot be
  written is not a section; merge its content elsewhere.
- One representation per example. A dialogue trace **or** a byte-by-byte table,
  never both.

## Workflow

### Step 1 — Inventory the source

**If the source is a lecture recording, flatten it first.** A video cannot be
read directly — `assets/extract_video.py` turns it into things that can be:

```bash
python assets/extract_video.py lecture.mp4
python assets/extract_video.py slides.mp4 --audio-from camera.mp4
```

The second form is for dual-stream recordings (Panopto and similar store the
screen capture and the camera/audio as separate streams — the user downloads
both, e.g. `yt-dlp --cookies-from-browser chrome <viewer URL>`; downloading and
authentication stay on the user's side, never in this skill). It needs
`ffmpeg` + `whisper-cli` on PATH and a ggml model; the script prints the
platform-specific install and download commands for whatever is missing
(macOS: `brew install ffmpeg whisper-cpp`; Windows: `winget install
Gyan.FFmpeg` plus a whisper.cpp release zip, or `WHISPER_CLI=…\whisper-cli.exe`).

Getting the file: public YouTube lectures download directly with
`yt-dlp -f "bv*[height<=720][ext=mp4]+ba[ext=m4a]/b" <url>`; a Panopto viewer
URL the user pastes that carries `lti_stored_token=<jwt>` can be fetched with
`yt-dlp --add-headers "Authorization: Bearer <jwt>" <url>` (the token is the
user's own session; never ask for or store credentials). Several long
recordings: launch the extractions **detached** (`nohup … &`, at most three at
a time) and poll — a foreground command is capped at ten minutes and a
background Bash task is killed at the same limit, taking its children with
it. Budget roughly a third of the recording's length per video when three run
in parallel.

Output directory: `frames/` (one PNG per distinct slide state, timestamped
filenames), `sheets/` (contact sheets), `transcript.srt`, and `index.md` —
which aligns each frame with everything spoken while it was on screen. Then:

- **Triage on the contact sheets, not frame by frame.** Open individual frames
  only where the sheet shows content worth reading closely.
- **If the sheets show only a handful of frames for a 20-minute video, the
  scene threshold was too high** (slide decks with white backgrounds and soft
  transitions fall under the default). Re-run with `--scene 0.012` or lower
  before concluding that the video only has a few slides.
- **Expect junk frames** — desktops, lock screens, blank editors. Skip them;
  do not report them as gaps.
- **Expect several frames per slide when the lecturer uses a spotlight or
  pointer overlay.** Read content from the least-occluded frame. The
  spotlight's *position over time* marks what the lecturer dwelled on, which is
  an EXAM-tag signal.
- **A transcript line repeated dozens of times** ("Let's see what is going
  on here…") is a whisper hallucination over silence or an in-class quiz, not
  content. Skip it; the frames for that span still count.
- **Transcript spelling is never authoritative.** Speech recognition mangles
  register names, mnemonics, and symbols. Every technical term that reaches
  the notes must be verified against a frame or the slide PDF. If the user
  also supplied the slide deck, the deck is the content source and the video
  contributes only the spoken layer and the timing.

Read the material end to end before writing anything. Produce (internally) a
map of: section numbers, slide/page ranges, worked examples, figures, and
every sentence the slides mark as **Note**, a **question**, or **bold**.

**If the user already has notes for part of the source** (an earlier PDF in
the folder), do a coverage diff before writing: `pdftotext` the old notes,
then for each topic in the new source grep the old text for its terms. What
is already covered gets one line on the cover ("▶03a fully covered by
L03_L04a notes"); only the gaps go in, collected in a short `§0 补遗` at the
front, each item citing the timestamp. Do not re-explain covered material.

Then check for **gaps**: slide numbering that jumps (e.g. 28 → 30) usually
means the instructor removed answer pages from the student handout. Look for
them in sibling decks; if genuinely unavailable, solve the exercise yourself
and mark it as derived. Continuous numbering with no exercises at all is a
different finding — say so on the cover.

### Step 2 — Decide what goes in

**Must go in:**

- Sentences the slides mark as *Note*, pose as a *question*, or set in *bold*.
- Anything the video obviously stresses, repeats, or says in a "this will be
  tested" tone → tagged EXAM with a timestamp.
- Definitions, rules, sequence formats, conversion formulas.
- The source's own worked examples (e.g. "write register 0x20", "read
  TEMP_OUT_L"), rewritten as a **step-by-step dialogue** or trace with, for
  every step, *who does it* and *what it means* (Step 4).
- **One sentence for the whole lecture**: the core fact from which the rest
  can be derived (e.g. I²C: *two wires, many devices share them, one master*).
  It goes on the cover, right after the title.

**Stays out, or gets one index line:**

- Long list-type background: peripheral catalogues, history, vendor names.
  Replace with one line such as *"p.21 has a list of I²C peripherals — knowing
  that low-speed, small-data devices use I²C is enough."*
- A full bilingual glossary table. Bracketing the English term at first use in
  each section is enough.
- The same example in two representations.
- Content that only the video covers, the slides omit, and the slides declare
  out of scope (e.g. multi-master arbitration when the slides say "single
  master only"). At most one red box: *"the video covers X; not examinable."*
- Rows of a comparison matrix for protocols the slides never classify. A row
  that would be all "—" is deleted.
- "Quick reference", "cheat-sheet", or glossary appendices that duplicate the
  body. If the body is tight enough, no appendix is needed.

### Step 3 — Write each key point in three layers

Every key point has the same three layers, in this order:

1. **Definition** — the slide's own wording or a formal statement that stays
   close to it, English terms kept. Plain paragraph, **no box**. This is what
   the reader writes in the exam. Lead with `定义：` / `Definition:`.
2. **Analogy** — one everyday analogy that makes the mechanism easy to picture
   and recall. **Yellow box** (`class="box ana"`). Examples of the register
   this aims for: an I²C transfer is a phone call — the master dials, the slave
   answers; an open-drain line is a rope hung from a spring — anyone can pull
   it down, nobody can push it up; the clock line is a metronome telling you
   *when* to read the lamp and *how many* flashes there were.
3. **Consequence / trap** — the rule that follows directly from the
   definition, or the way people most often get it wrong. **Green box**
   (`class="box key"`) for a rule to memorise; **red box** (`class="box
   trap"`) for a mistake, with the concrete case that exposes it.

Not every point needs an analogy, but every **mechanism** point — anything
answering *why is it designed this way* or *what happens on the wire* — must
have one. Pure fact points (speed grades, part numbers, pin names) get none.

The original callout types still exist and keep their colours — SUPP (blue),
TRAP (red), EXAM (amber), ERRATUM (purple), KEY (green) — and ANALOGY (yellow)
is added. Under these rules SUPP and ERRATUM are rare; EXAM is for
source-flagged or video-stressed content. `references/content-rules.md` has
the criteria and the analogy guidelines; `references/layout.md` has the markup.

**Video timestamps** (`▶V2 14:51`) go only inside EXAM and TRAP boxes, never in
body text, and at most one per key point. The reader jumps back to the
recording for emphasis, not for every fact.

### Step 4 — Worked examples as dialogues

Rewrite each of the source's examples as a step table with three columns:
*what is on the wire* | *who* | *what it means* — the "what it means" column
written as the line each party would say (*拿起电话* / *拨 0x5F，方向「我说」* /
*「我在」*). Reproduce the source's official sequence exactly and label it
`official`; label anything you derived `derived`. Then one line saying which
step is the one people get wrong.

If the source contains no exercises at all, derive two or three from its own
listings and figures, label every one `derived`, and say so where they appear.
Do not invent drill questions.

### Step 5 — Figures: only where a table would lie

Most content is a definition, a table, or a dialogue. Draw a figure only when
the content has spatial, sequential, or topological structure a table would
flatten — a waveform, a frame format, a bus with pull-ups. Hand-author inline
SVG; no chart libraries. `references/patterns.md` maps content shapes to
layouts, `references/layout.md` gives sizing and the two defects to avoid
(connectors through labels, text overflowing boxes). Keep SVG labels short and
in English; put any explanation in the body text.

An ASCII waveform inside `<pre class="plain">` is acceptable for a two-line
timing sketch and is often clearer than SVG.

**Trees and array traces have generators** — do not hand-draw them:
`assets/tree_svg.py` (`Tree`, `Tree.from_keys`, `render`, `side_by_side`:
BST/AVL/decision trees with highlight colours, height/rank badges, dashed
NULL slots, edge labels) and `assets/array_svg.py` (`render_array`,
`stack_rows`: cells with pointers for partition/merge/binary-search traces).
Write the parts from a small Python script that imports them, so every
before/after pair in the notes is drawn from the same verified key list.
Width rule: the A4 text column is about 700 CSS px; a tree panel is
`slots × 40 + 20` px wide, so two 11-node trees side by side need
`scale=0.62`, two 8-node trees `scale=0.85`, and three panels never fit —
split a three-step rotation into two before/after figures that share the
middle state. Rendering the figure and looking at it is still mandatory: the
most recent defect was a height badge on the rightmost node clipped by the
viewBox.

### Step 6 — Build

Write the notes as HTML fragments (`parts/part1.html`, `part2.html`, …), then:

```bash
python assets/build.py --parts parts --css assets/notes.css --out notes.pdf \
                       --footer "CG2028 · Lecture 5"
```

`build.py` concatenates the parts, runs the code-block syntax highlighter,
injects the stylesheet, and renders with WeasyPrint. Always pass `--footer`.

**CJK text:** `assets/notes.css` embeds Noto Sans CJK SC from `assets/fonts/`
via `@font-face`. `build.py` refuses to build CJK content when those font
files are missing; `python assets/get_fonts.py` fetches them once on any OS. Never let WeasyPrint fall
back to the macOS system fonts (PingFang, Hiragino): their subsetted
embeddings render as missing or wrong glyphs in Quartz-based viewers
(Preview, Quick Look, the claude.ai panel), while poppler shows them fine —
which is exactly how the bug slips through.

Mark up code as:

```html
<pre class="code" data-lang="python">…</pre>
<pre class="plain">…</pre>          <!-- no highlighting -->
```

`<pre class="asm">` is shorthand for `class="code" data-lang="arm"`. Run
`python assets/build.py --list-langs` for the available profiles (arm, c,
python, sql, verilog, generic). To add a language, append one entry to
`PROFILES` at the top of `build.py` and update this list and `README.md`.

### Step 7 — Verify

```bash
python assets/build.py --parts parts --css assets/notes.css --out notes.pdf \
                       --footer "CG2028 · Lecture 5" --check
```

`--check` writes `_check/sheetNN.png` (contact sheets, six pages each — the
overview pass: page-break damage, a figure that blew up, a page more than a
third empty) and `_check/pg-NN.png` (one image per page — the detail pass:
overlapping SVG labels, text spilling out of a box, a heading stranded at a
page bottom). Fix, rebuild, look again. `--check` requires poppler
(`brew install poppler` / `winget install oschwartz10612.Poppler` /
`apt install poppler-utils`) and fails loudly without it.

**Second renderer, mandatory for CJK output.** poppler is not what the reader
uses. Before delivering, render the pages with PDFium (Chrome's engine) and
confirm every glyph is present:

```bash
pip install pypdfium2                          # once
python assets/render_check.py notes.pdf        # -> _check/pdfium-pg-NN.png + font list
```

It exits non-zero if a macOS system CJK font (PingFang, Hiragino) is embedded.
On macOS, `qlmanage -t -s 1400 -o _check notes.pdf` adds a Quartz rendering of
page 1; on Windows, opening the PDF in Edge is the equivalent eyeball check.
`--check` itself falls back to PDFium when poppler is absent, so a machine
with only `pip install pypdfium2` can still run the full check.

**Detail pass is not optional after the overview looks fine.** Contact sheets
hide clipped labels and 9 px edge text; render at least the figure-heavy
pages at scale 1.5 (`render_check.py notes.pdf --pages 8,12 --scale 1.6`)
before delivering.

**Content self-check, before delivering.** Two deletions, both must pass:

1. Delete every yellow (analogy) box. Is what remains a tight, formal revision
   sheet the reader could hand in as answers?
2. Delete all body text and keep only the green and red boxes. Is what remains
   a usable five-minute reminder card for the exam hall?

If either fails, the layering is wrong — definitions leaked into analogy boxes,
or rules were left in prose. Fix before delivering.

## Structure of the finished document

1. **Cover strip** (not a full page) — course, lecture, source coverage,
   box-colour legend in one line, then the **one-sentence core fact** of the
   lecture and, if the lecture has one, its **master analogy** (e.g. the phone
   call) that the later sections reuse.
2. **Body** — one numbered section per key point, each opening with its
   "what question does this answer" sentence, each point in the three layers.
   Order by dependency, not by slide order; cite slide sections in the heading
   (`§3.3`, `p.24`) so the reader can cross-reference.
3. **Worked examples** as dialogues, in the section where they belong rather
   than collected at the end.
4. **Self-check** — 5–8 questions, each tagged with the section that answers
   it, no answers (or answers folded onto the last page). No cheat-sheet, no
   glossary, no quick-reference appendix.

## Lessons log

`references/lessons.md` records what went wrong on previous runs and the fix
that was adopted, one dated entry each. Read it before starting; append to it
when a run surfaces a new mistake, then fold the fix into the step it belongs
to so the log stays a history, not a second rulebook.

## Calibration sample

`references/samples/CG2028_Lec5_analogy_edition.txt` is the text of a 6-page
lecture-5 notes PDF the user produced by hand as the target form: definition →
analogy → consequence per point, examples as phone-call dialogues, a summary
matrix kept only for the protocols the slides classify, five self-check
questions at the end. Match its density. (The PDF itself sits next to it
locally; it is git-ignored because of its size.)

## Scope

This skill makes **short revision notes**. If the user wants an exhaustive,
slide-by-slide study document, or a one-page maximum-density exam cheatsheet,
those are different artifacts — say so and ask which they want.
