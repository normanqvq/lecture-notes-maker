# lecture-notes-maker from zero (step-by-step guide)

This guide is for someone who has **never used Claude Code and has never run
this pipeline**. Work through it section by section.

The tool does two things:

| You give it | You get | Mode |
|-------------|---------|------|
| Lecture slides PDF / lecture recording | A 5–7 page A4 revision-notes PDF (definition → analogy → rule/trap) | Notes mode (default) |
| A meeting recording (mp4 etc.) | Meeting minutes `minutes.md` (TL;DR, decisions, action items, all with timestamps) | Meeting mode |

There are three layers: **Claude Code** (the command-line tool that runs the
AI) → **this skill** (tells the AI how to write the notes) → **local
dependencies** (ffmpeg, whisper, etc., which turn the video into text and
screenshots). Speech-to-text runs **entirely on your own machine**; the
recording is never uploaded anywhere. Only the extracted text and frames go
to the model you chose.

---

## Step 0: install Claude Code

Claude Code is Anthropic's official terminal tool. The install command
differs by OS:

```bash
# macOS / Linux / WSL (open Terminal, paste, Enter)
curl -fsSL https://claude.ai/install.sh | bash

# Windows: open PowerShell (not CMD), paste, Enter
irm https://claude.ai/install.ps1 | iex
```

Close and reopen the terminal, then run `claude --version`. A version number
means it is installed.

> On Windows, installing [Git for Windows](https://git-scm.com/downloads/win)
> is recommended so Claude Code can run scripts through bash. Without it,
> it falls back to PowerShell, which also works.

### Log in: pick one of three

The first `claude` run asks you to log in. Three options; pick one:

**Option A: a Claude subscription (easiest)**
With a Claude Pro / Max account, run `claude` and follow the browser login.
The free Claude plan does **not** include Claude Code.

**Option B: an Anthropic API key**
Create a key at https://console.anthropic.com, set the environment variable,
then run `claude`. It asks once whether to use that key:

```bash
# macOS / Linux: put this in ~/.zshrc or ~/.bashrc
export ANTHROPIC_API_KEY=sk-ant-xxxxxxxx

# Windows PowerShell (current window only; for permanent use, add it under
# "Edit the system environment variables")
$env:ANTHROPIC_API_KEY="sk-ant-xxxxxxxx"
```

**Option C: another provider's API (DeepSeek / Kimi / Zhipu GLM, …)**
These providers offer an "Anthropic-compatible endpoint". Claude Code only
needs two environment variables changed to send its requests there. The
cleanest way is Claude Code's settings file: `~/.claude/settings.json` on
macOS/Linux, `C:\Users\<you>\.claude\settings.json` on Windows (create it
if missing):

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
    "ANTHROPIC_AUTH_TOKEN": "your DeepSeek API key",
    "ANTHROPIC_MODEL": "deepseek-v4-pro",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "deepseek-v4-pro",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "deepseek-v4-pro",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "deepseek-flash"
  }
}
```

For a different provider, change `ANTHROPIC_BASE_URL`, the key, and the
model names:

| Provider | ANTHROPIC_BASE_URL | Where the model names are |
|----------|-------------------|---------------------------|
| DeepSeek | `https://api.deepseek.com/anthropic` | https://api-docs.deepseek.com/quick_start/agent_integrations/claude_code/ |
| Kimi (Moonshot) | `https://api.moonshot.ai/anthropic` (global) / `https://api.moonshot.cn/anthropic` (China) | https://platform.moonshot.ai/docs |
| Zhipu GLM | `https://open.bigmodel.cn/api/anthropic` | https://docs.bigmodel.cn/cn/guide/develop/claude |

Model names change often, so **trust the provider's own docs**. Two things
to keep in mind with option C:

- **Notes from slides need a model that can see images** (frames, contact
  sheets, figures inside the PDF). Pick a model with image input, otherwise
  the slides in a recording cannot be read. Meeting minutes only use text,
  so any model works.
- If you set `ANTHROPIC_AUTH_TOKEN`, do not also set `ANTHROPIC_API_KEY`;
  the two conflict.

After changing the settings, restart `claude` and type `/status` to see
which endpoint and model are in use.

---

## Step 1: install the skill

A skill is just a folder. Put it under Claude Code's skills directory and it
is picked up automatically:

```bash
# macOS / Linux
git clone https://github.com/normanqvq/lecture-notes-maker ~/.claude/skills/lecture-notes-maker

# Windows PowerShell
git clone https://github.com/normanqvq/lecture-notes-maker "$env:USERPROFILE\.claude\skills\lecture-notes-maker"
```

Without git: on the GitHub page click the green **Code → Download ZIP**,
unzip, rename the folder to `lecture-notes-maker`, and move it into that
`skills` directory.

Check: run `claude`, type `/skills`, and `lecture-notes-maker` should be in
the list.

---

## Step 2: install local dependencies

Grouped by the feature you want. First make sure Python 3 is installed
(macOS ships with it; on Windows install from python.org and tick
*Add to PATH*). The guide writes `python`; if your machine only has
`python3` (common on macOS), use `python3` and `pip3` instead.

### 2a. Building the notes PDF (required for notes mode)

```bash
pip install weasyprint pillow pypdfium2
```

Windows also needs the GTK runtime, otherwise weasyprint fails with
`cannot load library 'libgobject-2.0-0'`:

```powershell
winget install tschoonj.GTKForWindows
```

Page inspection uses poppler (optional but recommended; without it the
check falls back to pypdfium2):

```bash
brew install poppler                     # macOS
winget install oschwartz10612.Poppler    # Windows
sudo apt install poppler-utils           # Linux
```

Chinese (or any CJK) notes need the fonts (about 33 MB, downloaded once):

```bash
cd ~/.claude/skills/lecture-notes-maker
python assets/get_fonts.py
```

### 2b. Reading video (lecture recordings and meetings)

You need ffmpeg (audio extraction, frame capture) and whisper.cpp (local
speech-to-text):

```bash
# macOS
brew install ffmpeg whisper-cpp

# Windows PowerShell
winget install Gyan.FFmpeg
#   whisper: download whisper-bin-x64.zip from
#   https://github.com/ggml-org/whisper.cpp/releases, unzip it, then either
#   add the unzipped folder to PATH or set:
#   $env:WHISPER_CLI = "C:\path\to\whisper-cli.exe"

# Linux
sudo apt install ffmpeg
#   build whisper.cpp yourself and put whisper-cli on PATH
```

Then download the whisper model (about 1.6 GB, once). The first time the
script runs without it, it prints the download command for your OS; copy
and run that. On macOS/Linux it is:

```bash
mkdir -p ~/.local/share/whisper-cpp && curl -L -o ~/.local/share/whisper-cpp/ggml-large-v3-turbo.bin \
  https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo.bin
```

Self-check:

```bash
ffmpeg -version
whisper-cli --help
```

Both printing something means you are set.

---

## Step 3: use it

**Key habit: start `claude` inside the folder that holds your material.**
It only sees the current folder and its subfolders.

### Slides → notes

```bash
cd ~/Desktop/CG2028_Lec5     # contains Lec5.pdf
claude
```

Then say, in English or Chinese:

> Make me a revision-notes PDF from Lec5.pdf.

It reads the PDF, writes the HTML, builds `notes.pdf`, and renders the pages
to images to check the layout. Along the way it asks a few times whether it
may run a command; glance and allow.

### Lecture recording → notes

Put the recording in the same folder and say:

> This is the lecture 5 recording, lecture.mp4. Turn it into revision notes.

It first runs `assets/extract_video.py` (speech-to-text plus slide frames),
then writes the notes. An hour of video takes roughly 15–20 minutes to
transcribe, so be patient. If you have both the slides PDF and the recording,
put both in: the slides are the content source, the recording only marks
what the lecturer stressed.

### Meeting recording → minutes

```bash
cd ~/Desktop/weekly_sync     # contains meeting.mp4
claude
```

> This is our weekly sync, meeting.mp4. Summarise it into meeting minutes.

It switches to meeting mode:

1. Runs `python assets/extract_video.py meeting.mp4 --transcript-only --lang auto`
   (`--transcript-only` skips frames, since a meeting picture is mostly
   faces; `--lang auto` detects the spoken language).
2. Reads the extracted `meeting_extracted/index.md` end to end.
3. Writes `minutes.md`: a three-sentence TL;DR, the decisions, an
   action-items table (who / what / by when / timestamp in the recording),
   open questions, and the topics in order. **It does not invent owners or
   deadlines that were never said**; those are marked "not assigned".

Ask "export it as a PDF" if you want one. If the meeting had a screen share
(slides or a document), tell it "there was a screen share, look at the
frames too" and it will drop `--transcript-only`.

### Just the transcript, no AI summary

This step needs no AI; the script runs on its own:

```bash
python ~/.claude/skills/lecture-notes-maker/assets/extract_video.py meeting.mp4 --transcript-only --lang en
```

Output lands in `meeting_extracted/`: `transcript.srt` (timestamped subtitle
file) and `index.md` (a readable version in five-minute blocks).

---

## Using it without Claude Code

The skill is essentially `SKILL.md` (the instructions) plus a few Python
scripts. It is not tied to Claude Code:

- **OpenAI Codex CLI** uses the same SKILL.md format. Put the folder at
  `~/.codex/skills/lecture-notes-maker` and call it with
  `$lecture-notes-maker` or `/skills` inside Codex.
- **Cursor or any other agent that can read files and run commands**: drop
  the whole repository into the project and say "read SKILL.md first, then
  follow its workflow to make notes from lecture.mp4".
- **Only a web chat (ChatGPT / Claude / Kimi)**: run the "just the
  transcript" step above yourself, then paste `index.md` together with
  `references/meeting-summary.md` (the minutes template and rules) into the
  chat and say "summarise following this template". For slide notes, give
  it Steps 2–4 of `SKILL.md` along with the slides; you just will not have
  the build script, so the final PDF is on you.

---

## FAQ

**`claude: command not found`**: the terminal was not reopened after
install, or PATH is missing the entry. Reopen the terminal; on Windows check
that `%USERPROFILE%\.local\bin` is on PATH.

**`whisper-cli not found`**: on Windows the unzipped folder is not on PATH.
Easiest fix is setting the `WHISPER_CLI` environment variable to the full
path of `whisper-cli.exe`.

**`whisper model not found at …`**: the model is not downloaded. Copy the
command printed under the error and run it.

**The transcript came out in the wrong language**: force it with
`--lang zh` or `--lang en`. Mixed-language speech works best with
`--lang auto`.

**A 20-minute recording only produced five or six slides**: white slides
with soft fades slip under the default threshold. Ask Claude to re-run with
`--scene 0.012`.

**Chinese PDF shows garbage or boxes**: the fonts are missing. Run
`python assets/get_fonts.py`.

**With a third-party API, reading frames errors out or gives nonsense**:
that model has no image input. Switch to a vision-capable model, or use only
the meeting-minutes feature.

**An hour-long recording stopped after 10 minutes**: ask Claude to run it in
the background with `nohup … &` (SKILL.md tells it to). It does this by
default; if not, remind it.

---

## One-line version

```
install Claude Code → log in (subscription / API key / third-party endpoint)
→ git clone into ~/.claude/skills/
→ pip install weasyprint pillow pypdfium2; brew install ffmpeg whisper-cpp poppler; download the model
→ cd into the folder with your material, run claude, ask for notes or a meeting summary
```
