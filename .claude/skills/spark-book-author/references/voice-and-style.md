# Voice & Style — match the book that already exists

Chapter 1 (`chapters/01-shape-of-a-spark-application.tex`) is the voice
reference. When in doubt, re-read its first two sections and write like that.
These rules describe what it already does well, plus the house fixes.

## 1. The voice in one paragraph

A senior engineer explaining a running system to a capable colleague.
Second person (**"you"**), present tense, active voice, concrete before
abstract. Confident but honest about limits ("You cannot fix it yet.
\Cref{ch:aqe} will."). Every chapter returns to the **specimen query** and
its four minutes; every claim either has a number, a plan excerpt, a UI
readout, or "(claim — verify on your cluster)".

## 2. Patterns the manuscript already uses — keep them

| Pattern | Example from the book | Use it for |
|---|---|---|
| **Specimen-first opener** | `chapterintro`: "A query you would actually write … runs in four minutes. This chapter does not make it faster." | Every chapter: a concrete symptom, then what the chapter will and won't do |
| **Role definitions in bold** | "The **driver** is the process that runs your program." | Defining the actors of a mechanism (driver, executor, cluster manager) |
| **New terms in `\emph{}` once** | "a \emph{physical plan}: a tree of operators…" | First use only, then plain |
| **"Put numbers on it"** | 2000 partitions × 3 MB = 6 GB → ÷ target size ≈ 47 tasks | After every mechanism: arithmetic on the reference cluster |
| **Numbered walk-through** | the 8-step submit → return sequence | A process with order; pair with a flow figure |
| **Comparison table** | narrow vs wide, by operation | Any "which one" decision — booktabs, `\footnotesize` |
| **Closing rule in bold** | "**cost lives at stage boundaries**" | Once per chapter, the sentence you want quoted |
| **Analogy box, bounded** | the restaurant kitchen — and where it breaks | Intuition only; always say where the analogy stops |
| **Forward pointers** | "\Cref{ch:aqe} and \Cref{ch:joins} will." | Name the gap honestly instead of half-explaining |
| **Summary as prose** | one paragraph restating the model | Then 1–2 sentences bridging to the next chapter |
| **Exercises on the specimen** | "count the Exchange nodes… match each to a stage boundary" | 3 per chapter: run-and-observe, read-a-plan, predict-then-check |

## 3. The five-beat explanation (for every new mechanism)

1. **Symptom** — what the reader sees on the specimen or in the UI.
2. **Picture** — `\Cref{fig:…}` + the figure; one sentence telling them where to look.
3. **Name it** — `\emph{term}` + a one-sentence definition.
4. **Prove it** — a listing (`EXPLAIN FORMATTED`, `SET`, a metadata-table query) and its real output, then the arithmetic.
5. **So what** — the lever: which config / rewrite / layout moves the cost, and what it costs in turn. A `tip` if it's a diagnostic shortcut.

## 4. Sentence & paragraph rules

- Sentences average 15–25 words; cap ~40. Vary rhythm — a short sentence after two long ones lands the point.
- Paragraphs: one idea, first sentence states it, **≤ 140 words** (`lint_chapter.py` flags longer). The current draft has ~46 paragraphs over that; the fix is usually *split + turn the enumeration into a table or numbered list*, not delete content.
- No more than ~900 words without a figure, table, or listing.
- Lead with the claim, then evidence, then implication.

## 5. Word-level house rules

**Cut or justify** (counts in the current draft: *just* ×37, *simply* ×21, *very* ×13):
simply · just (fine in "just as / just before") · very · easily · obviously ·
clearly · basically · of course · in order to (→ to) · note that · leverage (→ use) ·
utilize (→ use) · delve · seamless · robust · needless to say · let's.

"Simply" and "just" tell a struggling reader they're slow. Delete them; the
sentence almost always gets stronger.

**Canonical terms** (from `genesis/artifacts/05-conventions.md` — never alternate):

| Use | Not |
|---|---|
| stage boundary | shuffle boundary (same thing — pick one) |
| unified memory | managed memory |
| manifest list · manifest · data file · delete file | Iceberg's names exactly; never "manifest file list" |
| executor = process · task = thread · slot = one core | "worker" for executor |
| the specimen (query) | "our example", "the sample query" |
| Exchange (operator) / shuffle (the data movement) | interchangeably |
| copy-on-write (CoW) / merge-on-read (MoR) | COW/MOR |
| Spark UI tabs in bold: **SQL / DataFrame**, **Stages**, **Executors** | quotes |

## 6. Claims and numbers

- Every default is quoted **as of Spark 3.5.2** with `\conf{key}`; if it changed in 3.x/4.x, add a `note` naming the version.
- Every number is sourced: Spark/Iceberg docs, the source code, or "measured on the reference cluster (\Cref{app:refenv})".
- Can't verify? Write "(claim — verify on your cluster)" in the text — never smooth it over.
- Never invent `EXPLAIN` or UI output. If it wasn't run, say what shape it will have and mark it for capture: `% CAPTURE: EXPLAIN FORMATTED of lst:… on reference cluster`.

## 7. Before/after (house style)

> ✗ *It is important to note that AQE basically just simply merges partitions, which is very useful.*
>
> ✓ *After a shuffle, AQE knows the exact size of every partition — and merges adjacent small ones until each nears \conf{spark.sql.adaptive.advisoryPartitionSizeInBytes} (64 MB by default).*

> ✗ *In this section we will look at how Iceberg prunes files.*
>
> ✓ *A `WHERE order_ts >= '2026-03-01'` on `orders` never reaches most of its files. Iceberg discards them in three layers, before Spark opens a single Parquet footer (\Cref{fig:pruning-layers-funnel}).*

## 8. Never

- "the figure below/above", "as mentioned above" — floats move; use `\Cref`.
- Emoji, rhetorical exclamation marks, memes, "game-changer".
- A config without its default and cost.
- A chapter that ends without a Summary paragraph and a bridge sentence.
- Rewriting the author's sentences wholesale when polishing — show a diff-sized change and keep his voice.
