# Presentation patterns

A catalogue of recurring content shapes and the layout that serves each one.
Match the shape of the content, not the name of the subject.

Consult this when you are unsure how to render a section. If nothing here
fits, prefer prose plus a table over inventing an elaborate figure.

---

## 1. Sequential process — steps that must happen in order

*Fetch–execute cycles, protocol handshakes, lab procedures, algorithms,
derivations, historical causal chains.*

**Render as** a row of numbered step cards, or a table with one row per step.
Where the process mutates state, show the state after every step (see §2).

Avoid one large figure with many curved arrows. A row of self-contained cards
is easier to read and structurally cannot overlap.

If the process loops, draw the return path as a single connector running
through a lane that contains no text, and label the exit condition.

---

## 2. State evolution — something changes over time

*Register/memory traces, stack frames, variable tracking, accounting entries,
titration progress, population models.*

**Render as** a trace table: one row per step, one column per tracked quantity,
plus a final column explaining *why* that step does what it does.

Show every intermediate value. Bold or colour the cell that changed on each
row. This is where the page budget should go — a fully traced example is worth
three paragraphs of explanation.

Where a source supplies an official answer, reproduce it verbatim and label it
as official, then explain the reasoning separately.

---

## 3. Bit-field / packed structure — one container, many named sub-fields

*Peripheral control registers, status words, instruction encodings, network
packet headers, file format layouts, flag bytes.*

**Render as** a horizontal lane strip: one rectangle per field, width roughly
proportional to bit width, bit indices above, field names inside. Below it, a
table with columns: `Bits | Name | Values | Meaning`.

Rules that matter here:

- Always state the bit ordering convention explicitly (MSB-left is usual).
- Mark reserved fields visibly and say what to write to them.
- If the container has more than about 12 fields, split the strip in two rows
  rather than shrinking the labels below legibility.
- Follow with a worked read/write example showing the actual mask and shift.

---

## 4. Taxonomy / comparison — several items sharing attributes

*Instruction classes, memory technologies, protocol families, cell types,
asset classes, competing theories.*

**Render as** a matrix table: items as rows, attributes as columns. Use the
*same* attribute set for every item — if one item needs a column the others
don't, that column probably belongs in prose.

Use `✔` / `✘` glyphs rather than "yes"/"no" so the column scans vertically.

A comparison of exactly two things with more than about six attributes reads
better as a two-column table than as prose.

---

## 5. Hierarchy / containment — things inside other things

*Memory maps, class hierarchies, org structures, directory layouts,
taxonomies, geological strata.*

**Render as** nested boxes when depth ≤ 3, or an indented table when deeper.

For address or offset ranges, always use a table with an explicit range
column — a to-scale figure lies about the proportions when ranges differ by
orders of magnitude.

---

## 6. State machine / graph — nodes and labelled transitions

*Protocol states, parser states, lifecycle diagrams, reaction pathways,
decision procedures.*

**Render as** nodes in a row or ring, with transitions as connectors labelled
with the triggering condition.

Keep it to about seven nodes. Beyond that, split into sub-machines or use a
transition table (`From | Event | To | Action`), which stays readable at any
size.

---

## 7. Layered architecture — stack of abstraction levels

*Network models, OS layers, toolchain stages, hardware/firmware/application
splits, supply chains.*

**Render as** stacked full-width bars, top to bottom, with a short annotation
to the right of each. Mark clearly which layer the reader is currently working
at — that is usually the point of the figure.

---

## 8. Quantitative relationship — numbers that have a shape

*Growth curves, distributions, trade-off frontiers, measurement series.*

**Render as** a chart only when the shape carries the meaning. Four data points
belong in a table, not a bar chart.

Label axes with units. If the source gives specific figures, put them in a
table alongside the chart — readers quote numbers, and they cannot read exact
values off a plot.

---

## 9. Correspondence — two representations of the same thing

*Source and compiled output, formula and its code, notation and its meaning,
before and after a transformation.*

**Render as** two side-by-side columns with aligned rows, so the eye can match
line to line. Use the `.two` container.

State explicitly which direction the transformation goes, and who performs it
(you, the compiler, the hardware, nature).

---

## 10. Definition cluster — several terms introduced together

*Glossaries, notation conventions, symbol tables.*

**Render as** a table with columns `Term | Meaning | Where it appears`. The
third column is what makes it useful — a definition without a use site does not
stick.

If the source introduces terms as a numbered list (i, ii, iii…), keep that
numbering so the reader can cross-reference.

---

## Choosing between a figure and a table

A figure earns its space when the content has **spatial, sequential, or
topological structure** that a table would flatten. Otherwise use a table:
tables are denser, never overlap, reflow across page breaks, and are faster to
author.

Roughly one figure per major subsection is a healthy rate. A subsection with no
structural content does not need one.
