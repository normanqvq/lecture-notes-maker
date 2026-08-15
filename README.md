<a id="readme-top"></a>

<div align="center">
  <img src=".github/logo.svg" alt="logo" width="100" height="100">
</div>

<h1 align="center">lecture-notes-maker</h1>

<p align="center">
  A Claude skill that turns lecture slides, course PDFs, and lecture recordings into a dense, print-ready study-notes PDF — the kind you read during the semester, not the one-page cheatsheet you smuggle into the exam hall.
</p>

<p align="center">
  <a href="SKILL.md"><strong>Explore the workflow</strong></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3-3776AB?logo=python&logoColor=white" alt="Python 3">
  <img src="https://img.shields.io/badge/WeasyPrint-PDF-663399" alt="WeasyPrint">
  <img src="https://img.shields.io/badge/FFmpeg-frames-007808?logo=ffmpeg&logoColor=white" alt="FFmpeg">
  <img src="https://img.shields.io/badge/whisper.cpp-large--v3--turbo-4B8BBE" alt="whisper.cpp">
  <img src="https://img.shields.io/badge/license-MIT-97CA00" alt="MIT license">
</p>

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#about-the-project">About The Project</a></li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#repository-layout">Repository Layout</a></li>
    <li><a href="#not-what-you-want">Not What You Want?</a></li>
    <li><a href="#note-on-source-material">Note on Source Material</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

## About The Project

- **Default output**: A4 portrait PDF, single column, ~9.4 pt, dark
  syntax-highlighted code blocks, hand-authored inline SVG diagrams
- **Subject-agnostic**: a catalogue of presentation patterns maps content
  *shapes* (sequences, state traces, bit-fields, taxonomies, state machines,
  layered stacks) to the layout that serves each one — so it works the same for
  a computer-architecture deck, an organic-chemistry deck, or a finance deck
- **Eats recordings too**: `assets/extract_video.py` flattens a lecture video
  into timestamped slide frames + a whisper transcript, aligned so the notes
  can cite what the lecturer *said* but never wrote — with a timestamp to jump
  back to (needs `ffmpeg` + `whisper-cpp`, runs fully locally)
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
- **Self-checks the layout**: rasterises the PDF into full-size page images
  plus small contact sheets, so overlapping labels and stranded headings get
  caught before delivery
- Ends with a one-page quick-reference table and a self-test

### Output language

English by default. Ask for another language and it switches to bilingual mode —
explanation in your language, technical terms kept in the original.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Getting Started

### Prerequisites

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

Video sources additionally need **ffmpeg** and **whisper-cpp** plus a ggml
model (about 3 GB total, one-time; transcription runs locally — the recording
never leaves your machine):

```bash
brew install ffmpeg whisper-cpp
mkdir -p ~/.local/share/whisper-cpp
curl -L -o ~/.local/share/whisper-cpp/ggml-large-v3-turbo.bin \
  https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo.bin
```

### Installation

```bash
git clone https://github.com/normanqvq/lecture-notes-maker
cp -r lecture-notes-maker ~/.claude/skills/
```

Then just upload your lecture PDF — or point it at a lecture recording — and
ask for notes.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Usage

The build script works standalone if you want to write the HTML yourself:

```bash
python assets/build.py \
  --parts parts/ \
  --css assets/notes.css \
  --out notes.pdf \
  --footer "CG2028 · Lecture 2" \
  --check
```

`--check` writes `_check/pg-NN.png` (one image per page, at `--check-dpi`,
default 120) and `_check/sheetNN.png` (six pages tiled per sheet). Skim the
sheets, then open the individual pages — small text and SVG labels cannot be
judged at thumbnail size.

Code blocks are marked `<pre class="code" data-lang="python">`. Run
`python assets/build.py --list-langs` to see the available profiles (arm, c,
python, sql, verilog, generic). An unknown language falls back to `generic`, which still
colours comments, strings and numbers. Adding a language means appending one
entry to `PROFILES` at the top of `build.py`.

Lecture recordings get flattened first — one PNG per distinct slide state,
a timestamped transcript, and an index aligning each frame with everything
spoken while it was on screen:

```bash
python assets/extract_video.py lecture.mp4
python assets/extract_video.py slides.mp4 --audio-from camera.mp4   # dual-stream (Panopto)
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Repository Layout

```
SKILL.md                    the workflow and the non-negotiable rules
references/
  content-rules.md          when each tag applies, with worked examples
  patterns.md               content shape -> presentation pattern catalogue
  layout.md                 page, figure, and table conventions
assets/
  notes.css                 stylesheet
  build.py                  highlighter + WeasyPrint renderer + visual check
  extract_video.py          recording -> frames + transcript + alignment index
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Not What You Want?

If you need a **compressed exam cheatsheet** — formulas only, multi-column
landscape, maximum density — that's a different artifact with different rules.
This skill optimises for reading and understanding, and will tell you so.

## Note on Source Material

The skill reads your course material to produce your notes. Both the input and
the output are your instructor's intellectual property — keep them out of public
repositories.

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact

Norman — [@normanqvq](https://github.com/normanqvq)

Project Link: [https://github.com/normanqvq/lecture-notes-maker](https://github.com/normanqvq/lecture-notes-maker)

<p align="right">(<a href="#readme-top">back to top</a>)</p>
