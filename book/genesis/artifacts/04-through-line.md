# 04 — Through-line

## The one sentence the whole book serves

> Every Spark performance decision is a choice about where and when data moves —
> between operators, across the network, and between metadata and storage — and
> you can predict and change those movements once you can see them.

## How each part advances it

- **Part I — How Spark Executes a Query.** Establishes the machinery that moves
  data: the plan tree, stages and the shuffle wall, the executor's memory
  budget. The reader learns to *see* the movement in a plan and the UI.
- **Part II — Making Queries Fast.** Every chapter is one lever on data movement:
  the shuffle itself, join strategies (move the small side or move both),
  AQE (re-decide from real sizes), pruning and bucketing (don't move what you can
  skip), caching (don't recompute what you can keep).
- **Part III — The Iceberg Lakehouse.** Extends the movement model below the
  file: metadata is data that moves too, and the planner's first optimization is
  to read metadata instead of data. Layout, partitioning, and CoW/MoR are all
  choices about what the reader and writer have to move.
- **Part IV — Operating Spark.** Sizing, debugging, and streaming are the same
  model applied under real constraints: the executor budget from Part I, the
  shuffle from Part II, the commit from Part III.
- **Part V — Internals.** One level deeper on the same machinery: Tungsten and
  codegen (how a stage actually executes a row), the shuffle framework (how the
  wall is built), DataSource V2 (how Iceberg plugs into the planner).

## The anti-through-line

The book refuses to be *a list of `spark.sql.*` settings with recommended
values*. Configs appear only as the control surface for a mechanism that has
already been explained, and always with what the setting costs. A reader who
finishes the book should be able to derive most of the "recommended" configs
themselves, and know when the recommendation is wrong for their workload.
