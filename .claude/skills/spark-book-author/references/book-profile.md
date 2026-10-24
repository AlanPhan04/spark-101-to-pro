# Book Profile — *Spark Query Optimization and the Iceberg Lakehouse*

Snapshot of the manuscript at `github.com/AlanPhan04/spark-101-to-pro`
(commit `59a8307`, Oct 2026). **The repo is the source of truth**: if
`book/genesis/PROJECT_STATE.yaml` or `book/genesis/artifacts/*` disagree with
this file, trust the repo and update this file.

## Identity

| | |
|---|---|
| Working title | *Spark Query Optimization and the Iceberg Lakehouse* |
| Author | Alan Phan (Phan Hồng Quân) |
| Positioning | Practitioner **deep-dive**, mechanism-first — O'Reilly / *High Performance Spark* tradition |
| Language | English (author's working language with Claude is Vietnamese — reply in Vietnamese, write the book in English) |
| Size target | 19 chapters · 5 parts · 5 appendices · ~380 pages · heavy code |
| Format | LaTeX `book` class, XeLaTeX + biber, A4, Times New Roman 13 pt, 1.5 spacing |
| Planning pipeline | `book-genesis` (artifacts in `book/genesis/`) — phase **3-drafting** |

## Reader & promise

**Reader:** a data/analytics engineer, 2–6 years in, who writes Spark SQL most
days on an Iceberg lakehouse behind a gateway on Kubernetes; reads the Spark
UI like a dashboard, treats `spark.sql.*` configs as Stack Overflow spells,
thinks Iceberg is "Parquet with time travel".

**Promise:** *After this book you can read a Spark query's plan and its
runtime metrics, explain why it is slow, and change its physical execution on
purpose.* Replaces the trial-and-error config loop with a model.

**Through-line (every chapter serves it):**
> Every Spark performance decision is a choice about where and when data moves
> — between operators, across the network, and between metadata and storage —
> and you can predict and change those movements once you can see them.

**Anti-through-line:** never a list of `spark.sql.*` settings with
recommended values. A config appears only as the control surface of a
mechanism already explained, always with what it costs.

## The eight mental models (install in this order)

| # | Model | Replaces | Installed in |
|---|---|---|---|
| M1 | A query is a tree that gets rewritten, then compiled | "Spark runs my SQL" | Ch 2 |
| M2 | Work is partitions flowing through stages; a shuffle is the wall between stages | "Spark distributes the work" | Ch 1 + Ch 4 |
| M3 | An executor is one JVM with a carved-up memory budget | "give it more memory" | Ch 3 |
| M4 | The planner decides from statistics; wrong stats, wrong plan | "the optimizer is smart" | Ch 5 + Ch 6 |
| M5 | Skew is one partition doing most of the work | "the job is slow" | Ch 6 (AQE) |
| M6 | An Iceberg table is a tree of metadata pointing at immutable files | "Parquet with time travel" | Ch 9 |
| M7 | Pruning happens in layers, before any data is read | "add a WHERE clause" | Ch 7, Ch 12 |
| M8 | CoW vs MoR moves cost between writer and reader | "just use MERGE" | Ch 13 |

Each model should be drawable from memory by the end of its chapter — so
each has a **signature figure** (see `visual-system.md` §6).

## Reference environment (every behavioral claim is pinned to this)

Spark **3.5.2** · Iceberg **format v2** · Hive Metastore (+ Iceberg REST in
the genesis brief; App. A currently lists HMS only — reconcile) · Apache
**Kyuubi** gateway · **GKE** · **GCS** · OpenJDK **17** · Parquet.

**Cluster shape (App. A):** executors with 4 cores and 16 GB executor memory
each; 10 executors → **40 task slots**; GCS is remote (no data locality).

## Running example — `orders` star schema

`orders` — Iceberg, partitioned by `day(order_ts)`, a few hundred million rows/month:
`order_id string · order_ts timestamp · product_id string · customer_id string ·
promised_days int · delivery_days int · order_total double`.

Dimensions: `dim_product` (`product_id`, `category`, `list_price`, …) ·
`dim_customer` (`customer_id`, signup date, loyalty segment — large enough
not to broadcast) · `dim_date` (`date`, `year`, `month`, `day_of_week`).

**The specimen query** (Ch 1, `lst:shape-query`) — on-time delivery rate per
category for 1–7 March 2026, `orders ⋈ dim_product`, `GROUP BY category`.
On the reference cluster: **1 job · 3 stages · ~180 + a handful + 200 tasks ·
~4 minutes**, one skewed task in stage 2 (a viral discounted product). The
book keeps returning to *why four minutes* — reuse it, don't invent new toys.

> ⚠ Consistency to resolve: Ch 1 says the planner picks sort-merge because
> `dim_product` lacks stats; App. A says `dim_product` is small enough to
> broadcast under defaults. Both can be true (Iceberg reports file-size based
> `sizeInBytes`), but the text must say which happens for the specimen and why.

## Structure & status (lint_chapter.py --status, Oct 2026)

| Part | Ch | Slug | Words | Figs | Listings |
|---|---|---|---|---|---|
| I — How Spark Executes a Query | 1 | shape-of-a-spark-application | 2,611 | 4 | 1 |
| | 2 | sql-to-execution | 2,372 | 1 | 1 |
| | 3 | executor-memory-and-cpu | 2,484 | 2 | 1 |
| II — Making Queries Fast | 4 | the-shuffle | 2,358 | 2 | 4 |
| | 5 | joins | 1,872 | 1 | 2 |
| | 6 | adaptive-query-execution | 1,331 | 1 | 0 |
| | 7 | partitioning-bucketing-pruning | 1,257 | 1 | 2 |
| | 8 | caching-and-reuse | 1,516 | 1 | 1 |
| III — The Iceberg Lakehouse | 9 | table-formats-and-the-iceberg-spec | 1,602 | 1 | 0 |
| | 10 | catalogs-and-commits | 1,469 | 1 | 2 |
| | 11 | iceberg-partitioning-and-layout | 1,431 | 1 | 0 |
| | 12 | reading-iceberg-efficiently | 1,335 | 1 | 0 |
| | 13 | writing-and-maintaining-iceberg | 1,565 | 1 | 1 |
| IV — Operating Spark | 14 | tuning-resources-and-configuration | 1,808 | 0 | 0 |
| | 15 | debugging-and-profiling | 2,260 | 1 | 0 |
| | 16 | streaming-into-the-lakehouse | 1,997 | 1 | 1 |
| V — Internals (optional) | 17 | tungsten-and-code-generation | 1,829 | 1 | 1 |
| | 18 | shuffle-framework-and-scheduler | 1,382 | 1 | 0 |
| | 19 | datasource-v2-and-extensions | 1,352 | 1 | 2 |

Every chapter has a complete first draft (no `\tbd` left), but at ~1.3–2.6k
words each the manuscript is **~35k words of a ~120–150k-word book**. The
work now is **deepening**, not outlining: worked examples, real `EXPLAIN`
output, UI readouts, and the second/third figure per chapter
(`drafting-playbook.md`). Re-run `--status` instead of trusting this table.

`PROJECT_STATE.yaml` still lists only Ch 1–4 as drafted and 9 figures — update
it when you touch a chapter or render a figure.

## Scope

**In:** execution model · executor memory/CPU · Catalyst · AQE · shuffle ·
joins · skew · partitioning/bucketing/pruning · caching · Iceberg spec v2,
catalogs & commits, layout, reads, writes & maintenance · resource tuning ·
debugging/profiling · Structured Streaming into Iceberg · Tungsten/codegen,
shuffle framework, DSv2.

**Out:** MLlib, GraphX, SparkR, pandas API · Spark Connect as a subject ·
Delta/Hudi beyond comparison · cloud services beyond GCS/GKE · cluster
provisioning/IaC · teaching Scala/Java.

## Source material the author named

- `spark_memory_tuning.md` (repo root, may not be committed) → Ch 3, 4, 6, 13, 14
- `Spark Optimization Concepts.pdf` (repo root, may not be committed) → Ch 2, App. C
- Comps: *High Performance Spark* 2e (2026), *Spark: The Definitive Guide*,
  *Learning Spark* 2e, *Apache Iceberg: The Definitive Guide*, *DDIA*;
  Jacek Laskowski's *Internals of Spark SQL*.
