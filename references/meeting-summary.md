# Meeting summary (minutes) — structure and rules

Used by **Meeting mode** in `SKILL.md`. The source is the `index.md` and
`transcript.srt` that `assets/extract_video.py --transcript-only` produced
from a meeting recording. The deliverable is `minutes.md` (Markdown); build a
PDF only when the user asks for one.

Write in the user's language. Keep names of products, tickets, and code in
their original form.

## Template

```markdown
# <Meeting name> — <date if known>

**Source:** `<file>.mp4`, <duration>, <n> participants heard.
**Language of the recording:** <en / zh / mixed>.

## TL;DR
Three sentences at most: what the meeting was about, what was decided,
what happens next.

## Decisions
- [▶12:40] <decision, one line>. Why: <reason given, one line>.
- [▶31:05] …

## Action items
| who | what | by when | ▶ |
|-----|------|---------|---|
| Alice | finish the login page | Wed | 05:12 |
| not assigned | check the vendor quote | not said | 18:40 |

## Open questions / parked
- [▶22:10] <question raised and not answered>.

## Topics in order
1. **[00:00–08:30] <topic>** — two or three lines on what was said and
   where it landed.
2. **[08:30–20:15] <topic>** — …

## Things to double-check
- Speech recognition may have misheard: <term at ▶mm:ss>, <name>.
```

## PDF markup (only when the user asks for a PDF)

Build with `--css assets/minutes.css`. The stylesheet is black on white with
red as the only accent, so the HTML needs very few classes:

| Content | Markup |
|---------|--------|
| title | `<h1>` |
| source / duration / participants line | `<p class="meta">` |
| section headings | `<h2>` (black rule underneath; no `.sub`, no badges) |
| a decision, a deadline, `not assigned`, `not said` | `<span class="red">…</span>` |
| `▶` timestamp | `<span class="t">▶12:40</span>` |
| action items | a plain `<table>` with `<thead>` |
| a verbatim transcript line worth quoting | `<pre class="plain">` |
| the *things to double-check* list, if boxed | `<div class="box"><span class="tag">check</span> …</div>` |

Do not use `class="box supp/trap/exam/key/ana"`, `h2 .sub`, `.cover`, or
`data-lang` code highlighting; none of them is styled in `minutes.css`, and
the point of the plain look is that red means "this is a decision or a
deadline" and nothing else.

## Rules

1. **Every decision and action item carries a timestamp.** The reader uses
   it to check the recording; a line without one cannot be checked and
   should not be in the minutes.
2. **Never invent an owner or a deadline.** If nobody was named, write
   `not assigned`; if no date was said, write `not said`. Do not turn
   "someone should look at this" into an action item with a name on it.
3. **Speaker names only when the transcript says them.** Whisper does not
   diarise. "Alice will do X" is attributable; "I'll do X" is not, unless
   the speaker was addressed by name in the same minute. Otherwise write
   "a participant".
4. **A decision is something the group agreed to, not something one person
   proposed.** Proposals that got no answer go under *Open questions*.
5. **Length.** One page of Markdown for a 30-minute meeting, two for an
   hour. The *Topics in order* section is the only place for narrative;
   everything else is lists and the table.
6. **Whisper hygiene**, same as Step 1 of the lecture workflow: a line
   repeated dozens of times is silence, not content; technical terms and
   names are never trusted as spelled — list the doubtful ones under
   *Things to double-check* instead of silently correcting them.
7. **Mixed-language meetings** (Chinese with English product names, or the
   reverse) transcribe best with `--lang auto`; if the output is garbage in
   one language, re-run with that language forced (`--lang zh`).
8. **Screen-shared meetings.** If the recording shows slides or a document
   for a good part of it, drop `--transcript-only` so the frames are kept,
   and read the shared material from the frames the same way as lecture
   slides. Numbers on a shared spreadsheet beat numbers in the transcript.
