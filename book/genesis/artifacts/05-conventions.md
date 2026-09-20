# 05 — Conventions (also the LaTeX style contract)

## Reference environment and the version-pinning rule

Every behavioural claim is written against the stack in `00-brief.md`. Rules:

- State a behaviour as fact only if it holds on Spark 3.5.2 / Iceberg v2.
- When behaviour changed across versions, use a `\begin{note}` naming the version
  ("AQE coalescing is on by default since Spark 3.2; before that, ...").
- Defaults are quoted as of 3.5.2. A default that is likely to change gets a
  note.
- Never state a number (a threshold, a size, a speedup) without either a source
  or "measured on the reference cluster (App. A)".

## Running example

One dataset, reused everywhere: **`orders`** — an online marketplace's order
history landing in an Iceberg table, partitioned by `day(order_ts)`, plus a
small star schema (`orders`, `dim_product`, `dim_customer`, `dim_date`) built
from it. Introduced in App. A and Ch. 1; every later chapter queries these
tables, not a new toy. (Replaced the original `trips`/bus-route specimen for
being less immediately intuitive; see the git history for the migration.)

## Code, command, and query listings

- Language tag on every listing: `sql`, `scala`, `text` (for plans / UI / shell).
- Query plans are shown as `text` listings, lightly trimmed, with an ellipsis
  comment where lines are cut: `-- ... 3 Filter nodes elided`.
- Config keys inline use `\conf{...}` (breakable monospace).
- Scala is used for the few things SQL cannot express; kept to <15 lines.
- Every listing that produces output shows the output, in a second listing or
  inline, labelled.

## Callout taxonomy

| Callout | Use for | Not for |
|---|---|---|
| `\begin{note}` | a version gotcha, a clarification, a pointer to a later chapter | the main point of a paragraph |
| `\begin{warning}` | a default or pattern that silently costs money / correctness / data | mild inefficiency |
| `\begin{tip}` | a diagnostic shortcut, a UI panel to check, a one-liner | restating the summary |

At most one callout per page in normal flow.

## Figures

Required wherever prose describes a structure, a flow, or a layout the reader
would otherwise rebuild mentally (the plan pipeline, the executor memory map, the
Iceberg metadata tree, the shuffle write/read path, a skew split). Authored per
`references/prompts/diagramming.md`: `book/figures/<slug>.drawio` +
`<slug>_render.py` → `book/images/<slug>.pdf`, included with `\includegraphics`.

## Terminology

Defined once at first use, in italics, then used plainly. Canonical choices:

- *stage boundary* not "shuffle boundary" (they are the same; pick one)
- *unified memory* not "managed memory"
- *manifest list* / *manifest* / *data file* — the Iceberg spec's names, exactly
- *executor* is a process; *task* is a thread; *slot* = one core

Full term → chapter table lives in the book's back-matter glossary; keep it in
sync as chapters are drafted.

## Cross-references

`\Cref{...}` for everything, with labels: `ch:<slug>`, `sec:<slug>`,
`fig:<slug>`, `lst:<slug>`. Forward references are fine; every one must resolve.

## Source material

- `spark_memory_tuning.md` (repo root) — memory / shuffle / AQE / Iceberg tuning,
  by impact level. Feeds Ch. 3, 4, 6, 13, 14.
- `Spark Optimization Concepts.pdf` (repo root) — the owner's notes on the
  Catalyst pipeline, the six EXPLAIN modes, and every physical-plan operator
  (scan / exchange / sort / join / aggregate / codegen / AQE). Feeds Ch. 2 and is
  the backbone of App. C "Reading Query Plans".

## Show vs tell

Default to show: the `EXPLAIN`, the UI screenshot-as-figure or metric table, the
before/after timing, the file listing from `.files` metadata table. A claim that
cannot be shown is marked "(claim — verify on your cluster)" rather than smoothed
over.
