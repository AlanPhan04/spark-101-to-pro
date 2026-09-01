# 03 — Mental models the book installs

In dependency order. Each is a picture the reader should be able to draw from
memory by the chapter that installs it.

## M1 — A query is a tree that gets rewritten, then compiled

Replaces: "Spark runs my SQL." A Spark SQL query becomes an unresolved logical
plan, is resolved and optimized by rule-based tree rewrites (and some cost-based
ones), is turned into a physical plan by picking strategies, and is compiled to
JVM bytecode. Everything you can change is a change to one of those stages.
*Installed: Ch. "From SQL to Execution".*

## M2 — Work is partitions flowing through stages; a shuffle is the wall between stages

Replaces: "Spark distributes the work." Data is partitions. Operators that need
all rows for a key in one place force a shuffle, which writes every partition to
disk, moves it over the network, and re-reads it. Stage boundaries are exactly
the shuffles. Cost lives at stage boundaries.
*Installed: Ch. "The Shape of a Spark Application" + Ch. "The Shuffle".*

## M3 — An executor is one JVM process with a carved-up memory budget

Replaces: "give it more memory." The process is heap + off-heap pool + overhead;
the heap is reserved / unified (execution ↔ storage) / user; only unified memory
spills; user memory OOMs; overhead is consumed regardless; the container limit is
the sum. Cores divide the execution pool per task.
*Installed: Ch. "How an Executor Uses Memory and CPU". (Drafted material.)*

## M4 — The planner decides from statistics; wrong statistics, wrong plan

Replaces: "the optimizer is smart." Join strategy, join order, and broadcast
decisions come from size estimates. Iceberg tables often lack the stats Spark's
CBO wants. AQE re-decides at runtime from real sizes. Knowing where the estimate
comes from tells you when to override it.
*Installed: Ch. "Joins" + Ch. "Adaptive Query Execution".*

## M5 — Skew is one partition doing most of the work

Replaces: "the job is slow." When one key holds most of the rows, one task runs
while hundreds idle. No amount of memory fixes it; you redistribute the key or
let AQE split it. Max-vs-median task time is the tell.
*Installed: Ch. "Data Skew".*

## M6 — An Iceberg table is a tree of metadata pointing at immutable files

Replaces: "Iceberg is Parquet with time travel." A catalog pointer → a metadata
file → a manifest list → manifests → data and delete files. A commit swaps the
pointer atomically. Reads prune by consulting metadata before touching data.
Writes add files and a snapshot; they never mutate.
*Installed: Ch. "Table Formats and the Iceberg Spec".*

## M7 — Pruning happens in layers, before any data is read

Replaces: "add a WHERE clause." Partition pruning (skip whole partitions) →
manifest pruning (skip file groups) → file/row-group skipping via column stats →
optional bloom filters. Each layer needs the filter in a form it understands. A
`SELECT *` or a function on the partition column defeats a layer.
*Installed: Ch. "Reading Iceberg Efficiently" (builds on M1's pushdown rules).*

## M8 — Copy-on-write and merge-on-read move the cost between the writer and the reader

Replaces: "just use MERGE." CoW rewrites whole files on update (slow write, fast
read); MoR writes delete files (fast write, slow read until compaction). The
right choice is a function of the update rate and the read latency budget, and it
implies a maintenance schedule.
*Installed: Ch. "Writing and Maintaining Iceberg".*

## Dependency order

```
M1 ─┬─ M4 ── M5
    │
M2 ─┴─────────────── M7
M3 (independent, Part I)
M6 ── M7 ── M8
```
