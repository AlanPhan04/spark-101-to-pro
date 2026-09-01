# 06 — Outline

19 chapters, 5 parts, 5 appendices. Per-chapter section shape follows the
standard from `drafting.md` unless noted.

---

## Part I — How Spark Executes a Query

Arc: build the machinery that moves data and learn to see it in a plan and the UI.

### Ch 1 — The Shape of a Spark Application
- **Objective:** hold a correct picture of what runs where when a query executes,
  and run + observe a first query on the reference stack.
- **Prereq:** none (App. A for setup).
- **Payoff:** the reader runs a query against `trips`, opens the UI, and points
  at the driver, the executors, the one job, its stages, and its tasks.
- **Sections:** a query, end to end · driver, executors, cluster manager · deploy
  modes and Spark on Kubernetes · jobs, stages, tasks · narrow vs wide
  dependencies · reading the UI for the first time · Summary · Exercises.
- **Installs:** M2 (first half).
- **Figures:** `application-topology`, `job-stage-task`.
- **Exercise:** run two queries, one with a `GROUP BY` and one without; identify
  which produced a second stage and why.

### Ch 2 — From SQL to Execution: the Catalyst Pipeline
- **Objective:** trace a SQL string through parse → analyze → optimize → physical
  plan → codegen, and read `EXPLAIN FORMATTED`.
- **Prereq:** Ch 1.
- **Payoff:** the reader predicts the physical plan of a two-table join + filter
  before running it, then confirms with `EXPLAIN`.
- **Sections:** the pipeline overview · unresolved → resolved (the catalog) ·
  logical optimization (the rules that matter: pushdown, pruning, constant
  folding, join reorder) · physical planning and strategies · whole-stage code
  generation · reading `EXPLAIN` (parsed / analyzed / optimized / physical /
  formatted / cost) · Summary · Exercises.
- **Installs:** M1, M4 (first half).
- **Figures:** `catalyst-pipeline`, `explain-anatomy`.
- **Exercise:** given three query rewrites that are logically identical, predict
  which produce the same optimized plan.

### Ch 3 — How an Executor Uses Memory and CPU
- **Objective:** hold the executor memory map — which regions exist, which a
  query can use, which are consumed regardless — plus GC and serialization cost.
- **Prereq:** Ch 1.
- **Payoff:** the reader sizes a pod from `spark.executor.memory` + overhead,
  explains a container OOM with no Java error, and reads GC time in the UI.
- **Sections:** the JVM in one page (bytecode, JIT) · heap layout and object
  representation · **the executor memory model** (reserved / unified / user /
  off-heap / overhead / container limit / per-task) · garbage collection
  (Parallel, G1, ZGC) · serialization and its cost · Summary · Exercises.
- **Installs:** M3.
- **Figures:** `executor-memory-model` (**to render now**), `gc-pause-stall`.
- **Migrated:** the drafted §1.2 material moves here largely intact.
- **Exercise:** given a pod limit and a workload, propose `executor.memory` /
  `cores` / `memoryOverhead` and justify each from the map.

---

## Part II — Making Queries Fast

Arc: each chapter is one lever on data movement.

### Ch 4 — The Shuffle
- **Objective:** know the shuffle write and read path and size shuffle
  partitions from data volume.
- **Prereq:** Ch 1, Ch 3.
- **Payoff:** the reader counts the `Exchange` nodes in a plan, sizes
  `\conf{spark.sql.shuffle.partitions}`, and removes one unnecessary shuffle.
- **Sections:** what a partition is (input vs shuffle) · the write path
  (serialize, sort, spill, the map-side file) · the read path (fetch, merge) ·
  sizing partitions; why the default 200 is wrong · shuffle compression ·
  push-based shuffle · finding and removing unnecessary exchanges · Summary ·
  Exercises.
- **Installs:** M2 (completes).
- **Figures:** `shuffle-write-read-path`, `partition-sizing`.
- **Exercise:** from a stage's shuffle-read size, compute a target partition
  count; verify against the observed task sizes.

### Ch 5 — Joins
- **Objective:** predict the join strategy Spark picks and change it deliberately.
- **Prereq:** Ch 2, Ch 4.
- **Payoff:** the reader explains a `SortMergeJoin` that should have been a
  broadcast, and fixes it with stats or a hint.
- **Sections:** broadcast hash join · shuffle hash join · sort-merge join ·
  broadcast nested loop · how the planner chooses (the size estimate, the
  threshold, on-disk vs in-memory size) · forcing a strategy (hints, thresholds,
  `ANALYZE TABLE`) · storage-partitioned joins for bucketed Iceberg tables ·
  Summary · Exercises.
- **Installs:** M4 (completes).
- **Figures:** `join-strategies`, `broadcast-vs-smj`.
- **Exercise:** given table sizes and a threshold, predict each of four joins'
  strategies; then flip one with a config change.

### Ch 6 — Adaptive Query Execution
- **Objective:** know what AQE re-decides at runtime and from what evidence.
- **Prereq:** Ch 4, Ch 5.
- **Payoff:** the reader reads `AdaptiveSparkPlan isFinalPlan=true`, sees a
  coalesce and a skew split in the plan, and knows which planning-time decisions
  AQE can still override.
- **Sections:** why runtime beats planning time · coalescing shuffle partitions ·
  converting sort-merge to broadcast at runtime · the two broadcast thresholds ·
  skew-join handling (split + replicate) · `parallelismFirst` · reading an AQE
  plan · Summary · Exercises.
- **Figures:** `aqe-coalesce`, `aqe-skew-split`.
- **Exercise:** disable AQE, run a skewed join, record the straggler; re-enable,
  compare the plan and the task distribution.

### Ch 7 — Partitioning, Bucketing, and Pruning
- **Objective:** stop data from moving by skipping it: static and dynamic
  partition pruning, bucketing, `repartition` vs `coalesce`.
- **Prereq:** Ch 2, Ch 4.
- **Payoff:** the reader confirms `PartitionFilters` / `PushedFilters` in a scan,
  triggers dynamic partition pruning on a star join, and picks
  `repartition` vs `coalesce` correctly.
- **Sections:** partition pruning and the pushdown killers · dynamic partition
  pruning · bucketing to avoid a shuffle · `repartition` vs `coalesce` ·
  column pruning and `ReadSchema` · Summary · Exercises.
- **Installs:** M7 (first half — the Spark-side pushdown rules).
- **Figures:** `pruning-layers`, `dpp-flow`.
- **Exercise:** write a filter three ways (function on column, CAST, literal);
  check which keeps `PartitionFilters` populated.

### Ch 8 — Caching and Reuse
- **Objective:** keep what is expensive to recompute, and let Spark reuse what it
  can.
- **Prereq:** Ch 3, Ch 4.
- **Payoff:** the reader chooses a storage level from the GC budget, and spots
  exchange reuse vs a redundant recompute in a plan.
- **Sections:** when caching pays (reused, fits storage memory) · lazy `cache()`
  vs eager `CACHE TABLE` · storage levels and the GC trade-off · exchange and
  subquery reuse · unpersist and cache thrashing · Summary · Exercises.
- **Figures:** `storage-levels`.
- **Exercise:** build a query that reads one CTE twice; show the plan reusing the
  exchange, then break the reuse and measure.

---

## Part III — The Iceberg Lakehouse

Arc: extend the movement model below the file — metadata is data that moves too.

### Ch 9 — Table Formats and the Iceberg Spec
- **Objective:** hold the Iceberg metadata tree and the commit model.
- **Prereq:** Ch 1; App. A columnar-format primer.
- **Payoff:** the reader walks a real table's `metadata_log_entries`, `snapshots`,
  `manifests`, and `files` metadata tables and draws the tree.
- **Sections:** from Hive tables to table formats · the spec v2 (metadata file →
  manifest list → manifests → data / delete files) · snapshots and the metadata
  tree · position vs equality deletes · Iceberg vs Delta vs Hudi (one section) ·
  Summary · Exercises.
- **Installs:** M6.
- **Figures:** `iceberg-metadata-tree`, `iceberg-commit-swap`.
- **Exercise:** commit three appends, then inspect how many metadata files and
  manifests exist and why.

### Ch 10 — Catalogs and Commits
- **Objective:** know what a catalog resolves, how a commit becomes atomic, and
  how concurrent writers are handled.
- **Prereq:** Ch 9.
- **Payoff:** the reader explains an optimistic-concurrency retry storm and tunes
  `commit.retry.*`.
- **Sections:** what a catalog does (name → current metadata pointer) · Hive
  Metastore catalog · REST catalog · the atomic pointer swap · optimistic
  concurrency and retries · catalog config in Spark (`\conf{spark.sql.catalog.*}`)
  · Summary · Exercises.
- **Figures:** `catalog-pointer-swap`.
- **Exercise:** run two writers into the same table; observe the retry, then the
  win/lose commit in the snapshot log.

### Ch 11 — Iceberg Partitioning and Layout
- **Objective:** design a partition spec, sort order, and file size from the
  workload.
- **Prereq:** Ch 7, Ch 9.
- **Payoff:** the reader picks a transform (`day` vs `hour` vs `bucket`), evolves
  it without rewriting history, and sets a target file size.
- **Sections:** hidden partitioning and partition transforms · partition
  evolution · sort orders and Z-ordering · target file size and the small-files
  problem · write distribution modes (`none` / `hash` / `range`) · Summary ·
  Exercises.
- **Figures:** `hidden-partitioning`, `partition-evolution`.
- **Exercise:** given a daily volume and a query pattern, choose a partition
  spec; justify against the "128 MB–1 GB per partition per write" target.

### Ch 12 — Reading Iceberg Efficiently
- **Objective:** know the pruning layers the Iceberg reader applies before
  touching data, and keep each one working.
- **Prereq:** Ch 7, Ch 11.
- **Payoff:** the reader reads scan metrics (`skippedDataManifests`,
  `resultDataFiles`), enables a bloom filter for a point lookup, and tunes split
  size.
- **Sections:** manifest pruning and metadata filtering · column statistics and
  predicate pushdown into Iceberg · metrics modes (`full` / `truncate` /
  `counts` / `none`) · bloom filters · vectorized reads · split planning
  (`read.split.target-size`) · the metadata tables as a diagnostic · Summary ·
  Exercises.
- **Installs:** M7 (completes — the Iceberg-side layers).
- **Figures:** `pruning-layers-iceberg` (extends `pruning-layers`), `scan-metrics`.
- **Exercise:** run a selective query; from the scan report, compute the pruning
  ratio at each layer.

### Ch 13 — Writing and Maintaining Iceberg
- **Objective:** choose copy-on-write vs merge-on-read and the maintenance
  schedule it implies.
- **Prereq:** Ch 11, Ch 12.
- **Payoff:** the reader picks CoW/MoR per operation from the update rate,
  optimizes a `MERGE` with a partition predicate, and runs compaction /
  snapshot expiration / orphan cleanup in the right order.
- **Sections:** CoW vs MoR (where the cost goes) · `MERGE` / `UPDATE` / `DELETE`
  and partition pruning in the `ON` clause · write-distribution and skew on write
  · compaction (`rewrite_data_files`: binpack / sort / zorder) · `rewrite_manifests`
  · snapshot expiration and orphan files (and the order that matters) ·
  streaming-table metadata management · Summary · Exercises.
- **Installs:** M8.
- **Figures:** `cow-vs-mor`, `maintenance-order`.
- **Exercise:** measure a `MERGE` with and without the partition column in `ON`;
  explain the file-scan difference from the plan.

---

## Part IV — Operating Spark

Arc: the same model under real constraints.

### Ch 14 — Tuning Resources and Configuration
- **Objective:** size executors, cores, and memory from the mechanism, and know
  config precedence.
- **Prereq:** Ch 3, Ch 4.
- **Payoff:** the reader derives a starting executor shape for a workload and
  defends every number.
- **Sections:** executor sizing from the memory map and the shuffle · dynamic
  allocation · parallelism defaults · the external / push-based shuffle service
  on Kubernetes · configuration precedence and profiles · Kyuubi and
  multi-tenancy · Summary · Exercises.
- **Figures:** `config-precedence`.
- **Exercise:** take a job that spills; propose two different fixes (memory vs
  cores) and predict which the mechanism favours.
- **Note:** cross-references the standalone `spark_memory_tuning.md` in the repo
  root rather than duplicating its config tables.

### Ch 15 — Debugging and Profiling
- **Objective:** localize a slow or failing job from the UI, event logs, and a
  profiler.
- **Prereq:** Ch 1, Ch 4.
- **Payoff:** the reader takes a slow job and names the operator, the skew, or
  the failure signature in minutes.
- **Sections:** the Spark UI as a diagnostic (SQL / stages / executors / storage)
  · event logs and the history server · task-time breakdown, shuffle/spill/GC
  metrics · failure signatures (OOM and container kills, fetch failures and stage
  retries, stragglers) · async-profiler and flame graphs · debugging query plans
  · Summary · Exercises.
- **Figures:** `ui-diagnostic-map`, `failure-signatures`.
- **Exercise:** given three anonymized stage summaries, diagnose each (skew /
  under-partitioned / GC-bound).

### Ch 16 — Streaming into the Lakehouse
- **Objective:** apply the whole model to Structured Streaming writing Iceberg.
- **Prereq:** Ch 9, Ch 13.
- **Payoff:** the reader reasons about micro-batch commit cadence, watermark and
  state size, and the small-files pressure streaming puts on Iceberg.
- **Sections:** the micro-batch model and the unbounded table · sources and sinks
  · event time and watermarking · stateful operations and the state store
  (RocksDB) · output modes and triggers · exactly-once and the commit · writing
  to Iceberg: commit cadence, small files, metadata growth, maintenance · Summary
  · Exercises.
- **Figures:** `microbatch-commit`, `streaming-to-iceberg`.
- **Exercise:** given a trigger interval and an input rate, estimate files
  committed per hour and the compaction cadence needed.

---

## Part V — Internals (optional but rewarding)

Arc: one level deeper on the same machinery.

### Ch 17 — Tungsten and Code Generation
- **Objective:** know how a stage actually executes a row — off-heap memory,
  cache-aware layout, whole-stage codegen.
- **Prereq:** Ch 2, Ch 3.
- **Sections:** the Tungsten binary row format · off-heap memory management ·
  cache-aware computation · whole-stage codegen internals (the generated Java) ·
  expression codegen · columnar processing and vectorization · Summary.
- **Figures:** `tungsten-row`, `wholestage-codegen`.

### Ch 18 — The Shuffle Framework and the Scheduler
- **Objective:** know how the stage wall is actually built and scheduled.
- **Prereq:** Ch 4, Ch 15.
- **Sections:** the shuffle manager and shuffle writers · the map output tracker
  · the DAG scheduler and the task scheduler · RPC and block transfer · locality
  and speculation · Summary.
- **Figures:** `shuffle-framework`, `scheduler-flow`.

### Ch 19 — DataSource V2 and Extensions
- **Objective:** know how Iceberg plugs into the planner, and how to extend
  Catalyst.
- **Prereq:** Ch 2, Ch 9.
- **Sections:** the DSv2 read/write API · pushdown negotiation (filters, columns,
  aggregates) · how Iceberg reports splits and stats · custom Catalyst rules and
  SQL extensions · plugins · Summary.
- **Figures:** `dsv2-pushdown-negotiation`.

---

## Back matter

- **App. A — The Reference Environment and the Running Example.** The stack, the
  cluster shape, and the `trips` dataset + star schema every chapter uses.
- **App. B — Configuration Reference.** Keys used in the book, by subsystem, with
  default and the chapter that explains each.
- **App. C — Reading Query Plans.** A cheat-sheet: every physical operator, what
  it means, what precedes it.
- **App. D — Glossary.** Term → definition → first-use chapter.
- **App. E — Further Reading.** Papers, docs, and the comps, keyed to chapters.

---

## Dependency graph (chapter → depends on)

```
1  → (App A)
2  → 1
3  → 1
4  → 1, 3
5  → 2, 4
6  → 4, 5
7  → 2, 4
8  → 3, 4
9  → 1
10 → 9
11 → 7, 9
12 → 7, 11
13 → 11, 12
14 → 3, 4
15 → 1, 4
16 → 9, 13
17 → 2, 3
18 → 4, 15
19 → 2, 9
```

No forward dependency violations: every prerequisite chapter has a lower number.

## Where the drafted material lands

The current `book/chapters/01-prerequisites.tex` §1.2 ("The JVM and Executor
Memory", including the executor memory model, GC, serialization) → **Ch 3**. The
relational-model / file-format / distributed-systems primers from the old Ch 1 →
**App. A** (as prerequisites, not a chapter). The rest of the old skeleton is
superseded by this outline.
