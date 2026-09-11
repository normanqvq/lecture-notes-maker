# Cheatsheet mode — style rules

Settled during the CS2040C Quiz 1 build (Sep 2026). Apply unless the user says otherwise.

## Page
- A4 **landscape**, **double sided = exactly 2 sides**, margins 4mm / 4.5mm, **3 columns** (the GEA1000 model sheet used 4; 3 gives code room). 4 columns only if the sheet is prose-only.
- Numbered sections `1. …`, `2. …` with a rule under each `h1`; blue `h2` sub-headings.
- Header box: line 1 = course code + full course name, line 2 = "Quiz N Cheatsheet", line 3 = scope + colour legend.
- Body 5.5pt Times, code 5.0pt Consolas, tables 5.0pt. Smaller is unreadable on paper; bigger does not fit. If it does not fit, **cut content**, do not shrink further.

## Code
- Font Consolas (embedded from Word's DFonts when present), **normal weight**; keywords bold blue, types bold purple, **comments green italic**, strings red, numbers orange — "VS Code look".
- Every function complete and compilable (the user does not want a `main`). Blank line between functions so columns can break between them (one dashed box).
- Trailing comments aligned on one column (`align()` does it). Every code line **≤ `code_line_limit` chars (78 at 3 cols / 5pt)** or it is clipped at the column edge — the builder reports offenders.
- Key lines highlighted yellow (`!! ` prefix), fatal-mistake comments red (`//!`).
- Comments carry the exam point ("MUST be before 3", "O(n): no prev pointer"), not what the code obviously does.

## Prose
- **One item per line**: every definition, every T/F statement, every Big-O Step, every fact in an analysis list gets its own bullet / table row. No paragraph that mixes five facts — the user rejected that twice.
- T/F facts as a two-column table: statement | `T` (green) / `F` (red). Write the statement the way the quiz words it, with the correction in brackets.
- Complexity worked examples as a two-column table: code (mono) | `Step 1: … <br> Step 2: … <br> ⇒ O(…)`. One Step per line, conclusion on its own line. Add a `Note:` line when a rule generalises ("base is a constant ⇒ never compute it").
- Red bold (`<r>`) = exam point / trap / the answer F. Green bold (`<t>`) = the answer T. Yellow (`<y>`) = key line.
- English body (exam language); Chinese only for short signposts the user asked for (考点/陷阱, 「叫一次不能乘」).

## Figures
- Small inline SVG (40–58 mm wide) only where structure matters: the lecture's example tree with heights, a delete/rotation before-after, a recursion tree with per-level cost, a linked-list node diagram. Caption states the fact the figure proves.
- Traces (partition, merge) as plain-text blocks (`code(..., 'pl')`), ≤ 78 chars per line.

## What goes in (decided from past papers)
1. Read **all** past papers with answers first. Count marks per question type; the sheet's space follows the marks.
2. Everything that was ever asked as T/F goes into the T/F bank verbatim-ish.
3. Every code fill-in from past papers (searchMin, level order, missing badge, stack sort) appears as complete code with the paper cited in the comment.
4. Tables of rules (loop patterns, recurrences, sort properties) beat prose; worked examples only for shapes the tables do not settle.
5. Out-of-scope topics (e.g. AVL when told so) are excluded entirely, not "just mentioned".

## Cutting order when a side overflows (least exam value first)
duplicate examples already covered by a rules table → decorative figure size → helper functions not asked in any paper (removeTail, destroy) → long analogies → table columns that are all the same value. Never cut a T/F fact, a past-paper code fill-in, or a rule table row.
