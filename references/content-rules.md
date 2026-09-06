# Content rules: layers and callouts

The notes separate three things the reader must be able to tell apart at a
glance: **what to write in the exam** (definition, plain text), **how to
picture it** (analogy, yellow box), and **what to remember or avoid** (rule in
green, trap in red). If a box could be deleted without loss, delete it.

---

## Definition (no box)

The slide's own wording, or a formal statement that stays close to it. English
technical terms kept; in bilingual mode the English term is bracketed at first
use in each section. Lead with `定义：` / `Definition:` so the reader can find
the answer-sheet sentence instantly.

A definition should be complete enough that the reader could write it as the
answer to "define X". It should not contain the analogy, the consequences, or
the traps — those are the other layers.

---

## ANALOGY (yellow box, `class="box ana"`)

**Use when:** the point is a *mechanism* — why something is designed the way it
is, or what physically happens on the wire / in the register / in memory.

**Do not use for:** pure facts (speed grades, part numbers, bit positions),
or when the definition is already self-evident.

What makes an analogy work here:

- One everyday situation the reader has actually been in (a phone call, a
  group chat, a rope on a spring, a metronome, a choir with or without a
  conductor).
- Every element of the mechanism maps to one element of the analogy, and the
  mapping is stated explicitly: *"SDA is the rope, the pull-up resistor is the
  spring holding it up, pulling down = driving 0, letting go = high-Z."*
- The analogy predicts the consequence in the next layer. If the rope model
  does not explain why START must be a falling edge, it is the wrong analogy.
- Lead with `类比：` / `Analogy:`.

**Example.** Open-drain: *a rope hung from a spring. Every chip can grab the
rope and pull it down (drive 0) but nobody can push it up — to raise it you
let go (high-Z) and the spring lifts it. Several people pulling at once cannot
break anything; the rope is simply down.* From this the reader can derive
wired-AND, the idle-high bus, why START is a falling edge, and why a slave can
stretch the clock.

---

## KEY (green box, `class="box key"`)

**Use when:** a rule follows directly from the definition and the reader must
be able to reproduce it verbatim. Keep to one to three sentences. This is the
layer that survives the "delete all prose" self-check and becomes the exam-hall
reminder card, so every green box must stand on its own.

**Example.** *Data bits change only while SCL is low; SDA is sampled while SCL
is high. Therefore a change of SDA while SCL is high can be reserved as a
signal: falling = START, rising = STOP.*

---

## TRAP (red box, `class="box trap"`)

**Use when:** there is a *specific, nameable* way to get this wrong, and the
failure is not obvious from the symptom.

The strongest traps are ones where two plausible mental models give different
answers. Show the case that distinguishes them.

**Example.** *Sending the 7-bit address 0x5F as-is puts 0101 1111 on the wire,
which the slave reads as "address 0x2F, READ" — nobody answers, and the 9th
clock shows NACK. The 8-bit write address is 0x5F << 1 = 0xBE.*

**Test for a good TRAP box:** does it contain a concrete case where the naive
model produces the wrong answer? If not, it is just emphasis — fold it into
the green box or the body.

TRAP is one of only two boxes allowed to carry a video timestamp.

---

## EXAM (amber box, `class="box exam"`)

**Use when:** the source telegraphs that something is examinable — a "Note:"
line on a slide, a definition stated in unusually precise wording, a question
the slide poses, or (from a recording) the lecturer saying "this will be on the
exam", repeating a point, or parking the spotlight on it.

Quote the *slide's* wording, not the transcript's. Cite the timestamp
(`▶V2 20:25`) so the reader can hear the emphasis — this is the other box
allowed to carry one, and one per key point is the maximum.

**Example.** *p.5 Note: "data processing and storage (ALU, registers,
memories) deal with data in a parallel manner even when data transfer is
serial" → a serial link needs a parallel-to-serial converter at the transmitter
and a serial-to-parallel converter at the receiver. ▶V1 05:48*

---

## SUPP (blue box, `class="box supp"`) — rare

**Use when:** the slides simplified something and the simplification will
mislead the reader the first time they write real code or read the datasheet.
Not for trivia, history, or anything the slides declare out of scope. Under the
short-notes rules most former SUPP material is cut; what survives is one or two
lines, and ends with "answer the slide's version in the exam".

---

## ERRATUM (purple box, `class="box err"`) — rare

**Use when:** the slides are factually wrong, internally inconsistent, or have
a typo that changes meaning. Cite the page, state what it says, state what is
correct. When unsure whether it is an error or a convention you do not know:
leave it out. A wrong erratum destroys trust in every other box.

---

## Density calibration

The target reader is studying alone from these notes without the lecture, in
about twenty minutes.

- Body prose: complete sentences, no throat-clearing.
- Prefer a table over a bulleted list whenever there are ≥ 3 parallel items
  with ≥ 2 attributes each; prefer a dialogue table over a byte table for
  protocol examples.
- One representation per example.
- If a section has no boxes at all, that is fine. Do not manufacture them.
- Long lists from the slides become one index line pointing at the page.
