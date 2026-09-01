# 02 — Reader and promise

## Who the reader is

A data engineer or analytics engineer, 2–6 years in, who:

- writes Spark SQL (and some DataFrame code) most working days
- runs it on a lakehouse: Iceberg tables on object storage, queried through a
  gateway, on Kubernetes
- owns pipelines that are "fine until they aren't" — a job that doubled in
  runtime after data grew, a join that spills, a query that scans everything
- can read a SQL query and reason about relational logic
- has opened the Spark UI but reads it like a dashboard, not a diagnostic
- knows the JVM exists and that GC and memory matter, without a working model
- treats `spark.sql.*` configs as spells found on Stack Overflow
- thinks of Iceberg as "Parquet with time travel"

## What the reader already knows (assumed, not taught)

- SQL: joins, aggregation, window functions, subqueries
- the relational model and basic relational algebra
- columnar vs row storage at a high level; what Parquet is for
- Kubernetes as an operator: pods, resource limits, why a pod gets OOM-killed
- reading a stack trace; basic command-line and Git

## Current level → target level

| | Today | After the book |
|---|---|---|
| Query plans | "there's an EXPLAIN somewhere" | predicts the physical plan before running; reads `EXPLAIN FORMATTED` fluently |
| Slowness | guesses, adds memory, retries | localizes the cost to a stage/operator from the UI and metrics |
| The shuffle | "the slow part" | knows the write/read path, sizes partitions, removes unnecessary exchanges |
| Joins | lets Spark decide | predicts the strategy, forces it when the stats are wrong, fixes skew |
| Iceberg | "Parquet with snapshots" | reads the metadata tree, knows what the planner prunes and when |
| Config | copies snippets | knows which knob touches which mechanism, and what it costs |

## Transformation promise, expanded

By the end, the reader can:

1. Take a Spark SQL query and predict its physical plan and its shuffles.
2. Open the Spark UI on a slow job and name the operator that costs the time.
3. Explain why Spark chose a join strategy, and change it deliberately.
4. Detect and fix data skew instead of raising executor memory.
5. Read an Iceberg table's metadata and predict what a query will prune.
6. Choose copy-on-write vs merge-on-read, a partition spec, and a distribution
   mode from the workload, not from a default.
7. Size executors, cores, and memory from the mechanism, and defend the choice.

## The failure this book prevents

The reader currently fixes performance by trial and error: change a config,
rerun, keep it if it helped, never know why. That works until the query is big
enough that each trial costs an hour and money. This book replaces the trial
loop with a model.

## Non-goals for the reader

This book will not teach: Scala or Java as languages; MLlib / GraphX / streaming
ML; how to provision a cluster; how to administer Kubernetes; the pandas API on
Spark; or Delta Lake / Hudi beyond comparison.
