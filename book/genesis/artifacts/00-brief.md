# 00 — Brief

## Original user idea (verbatim, paraphrased across turns)

A thorough PDF guide covering everything about Spark, structured along the
README's 8-phase roadmap, emphasis on SparkSQL / Catalyst query optimization and
the Lakehouse (Apache Iceberg), written in LaTeX. Later: make it read and be
structured like a normal Western IT / reference book, not a thesis.

## Inferred direction

A single-author practitioner **deep-dive** on **why a Spark SQL query executes
the way it does** — from the Catalyst optimizer, through the shuffle and the
execution model, down to the Iceberg metadata layer — and how to change that
execution deliberately. Mechanism first, configuration second.

## Language

English.

## Reader (one line)

A working data engineer who runs Spark SQL on an Iceberg lakehouse daily and
wants to stop treating the optimizer and the table format as black boxes.

## Transformation promise (one line)

After this book you can read a Spark query's plan and its runtime metrics,
explain why it is slow, and change its physical execution on purpose.

## Scope

**In:** execution model (driver/executors, jobs/stages/tasks); memory and CPU on
an executor; Spark SQL and the Catalyst pipeline; Adaptive Query Execution; the
shuffle; join strategies; data skew; partitioning, bucketing, and pruning;
caching and reuse; the Iceberg table spec v2; catalogs and commits; Iceberg
partitioning and layout; reading Iceberg efficiently; writing and maintaining
Iceberg; resource and configuration tuning; debugging and profiling; Structured
Streaming into Iceberg; selected internals (Tungsten, code generation, the
shuffle framework, DataSource V2).

**Out:** MLlib, GraphX, SparkR, the pandas API on Spark; Spark Connect as a
subject; non-Iceberg table formats except for comparison; cloud-vendor services
beyond GCS/GKE; cluster provisioning / IaC; teaching Scala or Java.

## Reference environment

Spark 3.5.2 · Apache Iceberg format v2 · Hive Metastore + Iceberg REST catalog ·
Apache Kyuubi · Google Cloud Storage · Kubernetes (GKE) · JVM 17 · Apache
Parquet. Every behavioural claim in the book is written against this stack;
version-dependent behaviour is called out where it differs.

## Positioning

Deep-dive. Adjacent to *High Performance Spark* in spirit, but narrower and
mechanism-first, and it treats the Catalyst↔Iceberg seam as a first-class
subject rather than two separate books.

## Rough size

- chapters planned: 19 across 5 parts + 5 appendices
- pages planned: ~380
- code density: heavy (SQL, Scala snippets, query plans, UI/metric readouts)
