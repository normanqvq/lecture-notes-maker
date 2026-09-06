<a id="readme-top"></a>

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
  <img src="https://img.shields.io/badge/Claude_Code-skill-D97757?logo=claude&logoColor=white" alt="Claude Code">
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

- **Default output**: a short A4 revision-notes PDF — one lecture in roughly
  5–7 pages, not a slide-by-slide transcription
- **Three layers per key point**: a formal definition (what you write in the
  exam), an everyday analogy in a yellow box (how to picture it), and the rule
  or trap that follows in a green or red box (what to memorise / avoid).
  Delete the yellow boxes and a formal revision sheet remains; delete the
  prose and the green/red boxes are a five-minute reminder card
- **Worked examples as dialogues**: the source's own examples rewritten step
  by step — what is on the wire, who does it, what it means
- **Eats recordings too**: `assets/extract_video.py` flattens a lecture video
  into timestamped slide frames + a whisper transcript, so the notes can tag
  what the lecturer *stressed* (EXAM / TRAP boxes carry a `▶` timestamp)
- **Verifies before writing**: reads the actual source material and refuses to
  generate from memory — no source, no notes
- **Self-checks the layout** with poppler rasters, and asks for a second
  renderer (Quartz / PDFium) before delivery because font-embedding bugs do
  not show in poppler
- Ends with a 5–8 question self-check, no cheat-sheet appendix

### Output language

English by default. Ask for another language and it switches to bilingual mode —
explanation in your language, technical terms kept in the original.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Getting Started

### Prerequisites

```bash
pip install weasyprint pillow
```

Chinese (or any CJK) output needs the bundled Noto Sans CJK fonts in
`assets/fonts/` (about 33 MB, git-ignored):

```bash
python assets/get_fonts.py
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

Video sources additionally need **ffmpeg** and **whisper.cpp** plus a ggml
model (about 3 GB total, one-time; transcription runs locally — the recording
never leaves your machine):

```bash
# macOS
brew install ffmpeg whisper-cpp
# Windows (PowerShell)
winget install Gyan.FFmpeg
#   then download whisper-bin-x64.zip from
#   https://github.com/ggml-org/whisper.cpp/releases, unzip it, and either add
#   the folder to PATH or set  $env:WHISPER_CLI = "C:\\path\\whisper-cli.exe"
```

`extract_video.py` prints the model download command for your OS the first
time it runs without one (`~/.local/share/whisper-cpp/ggml-large-v3-turbo.bin`).

For the second-renderer check (`assets/render_check.py`):

```bash
pip install pypdfium2
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
