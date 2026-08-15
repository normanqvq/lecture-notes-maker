# Content rules: the four callout types

Callouts exist to keep "what the slides said" separate from "what you need to
know anyway". If a box could be deleted without loss, delete it.

---

## SUPP — Supplementary

**Use when:** the slides simplified something, and the simplification will
mislead the reader the first time they write real code or read the real spec.

**Do not use for:** trivia, history, or "fun facts". If it never affects what
the reader does, leave it out.

**Example.** The slides state that an immediate operand "must be `<imm8>`,
range 0–255". That is a teaching simplification. The architecture actually
encodes a *modified immediate constant*, which also admits byte-replicated
patterns and shifted 8-bit values. A student who takes the slide literally will
be confused when `#0xFF000000` assembles fine.

The box should: state the real rule, give a table of what does and does not
encode, and end with **"answer the slide's version in the exam"** so the reader
knows the supplement is for understanding, not for the answer sheet.

---

## TRAP — Common mistake

**Use when:** there is a *specific, nameable* way to get this wrong, and the
failure is not obvious from the symptom.

The strongest traps are ones where two plausible mental models give different
answers. Show the case that distinguishes them.

**Example.** For subtraction, the carry flag means *no borrow*, i.e. unsigned
`A ≥ B`. Readers reasonably but wrongly guess "C = 1 when the result looks
positive", i.e. read it off the N flag.

A box that just asserts the rule teaches nothing. The box must contain the
counter-example that breaks the wrong model:

```
0xFFFFFFFF − 0x00000001 = 0xFFFFFFFE   →   N = 1  but  C = 1
```

N and C disagree here, which proves N cannot be used to infer C.

**Test for a good TRAP box:** does it contain a concrete case where the naive
model produces the wrong answer? If not, it is just emphasis — fold it into the
body as bold text instead.

---

## EXAM — Likely assessed

**Use when:** the source telegraphs that something is examinable — a "Note:"
line on a slide, a definition stated in unusually precise wording, or a
distinction that an exercise turns on.

When the source is a recording, the strongest signals are spoken, not written:
"this will be on the exam" said outright, the same point repeated across
minutes, or the lecturer parking the spotlight on one region of a slide while
talking through it. Cite the timestamp (`▶ 37:17`) so the reader can hear the
emphasis themselves — and quote the *slide's* wording, not the transcript's,
whenever both exist (speech recognition mangles technical terms).

Where possible, quote the phrasing the source uses, because that is the
phrasing the marking scheme will use.

**Example.** A slide's closing note reads: *most instructions do not distinguish
between signed and unsigned operands; the programmer must know which flag to
check*. That sentence is the answer to a whole class of questions. Reproduce it,
then add the practical mapping (unsigned comparisons read C and Z; signed
comparisons read N, V, Z).

---

## ERRATUM — Source error

**Use when:** the slides are factually wrong, internally inconsistent, or have a
typo that changes meaning.

Be specific and be fair. Cite the slide number, state what it says, state what
is correct, and — where it is a defensible simplification rather than a mistake
— say so.

**Example.** A block diagram labelled as a specific MCU shows 80 MHz / 1 MB
Flash, which are the generic family figures; the part in question is
120 MHz / 2 MB Flash / 640 KB SRAM. Worth flagging because students quote these
numbers in reports.

**Counter-example — do not raise:** a slide writes a constant as `314` for π.
That is fixed-point notation (π × 100), not an error. Explaining it belongs in a
SUPP box, not an ERRATUM.

**When unsure whether it is an error or a convention you do not know: leave it
out.** A wrong erratum destroys trust in every other box.

---

## Density calibration

The target reader is studying alone from these notes without the lecture.

- Body prose: complete sentences, but no throat-clearing. Cut "It is important
  to note that".
- Prefer a table over a bulleted list whenever there are ≥ 3 parallel items with
  ≥ 2 attributes each.
- Every worked example gets a full state trace. This is where the page budget
  should go.
- If a section has no callouts at all, that is fine. Do not manufacture them.
