# Assumptions

Every value here was inferred, not stated by the user. Correct any that are wrong.

## From Intake

- **Language**: English. (User writes in Vietnamese but asked for an English book,
  "cách viết và cấu trúc của một cuốn sách IT nước ngoài" — a Western IT book.)
- **Reader**: a working data engineer who uses Spark SQL daily on a lakehouse and
  can read a query, but treats the optimizer and Iceberg metadata as a black box.
  Comfortable with SQL, the JVM at a distance, and Kubernetes as an operator.
- **Current level → target level**: "can write Spark SQL and set configs from
  Stack Overflow" → "can predict a query's plan, read why it is slow from the UI
  and metadata, and change the physical execution on purpose."
- **Transformation promise**: *understand why a Spark query runs the way it does,
  from Catalyst to the shuffle to the Iceberg metadata layer, and change it.*
- **Positioning**: deep-dive (mechanism-first), not a tutorial or a cookbook.
- **Sub-genre**: practitioner deep-dive in the O'Reilly / *High Performance
  Spark* tradition.
- **Reference environment**: the user's production stack — Spark 3.5.2, Iceberg
  format v2, Kyuubi, Hive Metastore + Iceberg REST catalog, GCS, GKE, Parquet,
  JVM 17. Assumed from `README.md` / `CLAUDE.md`.
- **Scope IN**: Spark execution model; Catalyst/AQE; the shuffle; joins; skew;
  partitioning/bucketing/pruning; caching; Iceberg spec v2, catalogs, layout,
  read/write/maintenance; resource & config tuning; debugging/profiling;
  Structured Streaming into Iceberg; selected internals (Tungsten, codegen,
  shuffle framework, DSv2).
- **Scope OUT**: MLlib / GraphX / SparkR / pandas API; Spark Connect as a topic
  in itself; non-Iceberg table formats beyond comparison; cloud-vendor specifics
  beyond GCS/GKE; cluster provisioning and IaC; Scala/Java language teaching.
- **Length**: ~19 chapters / ~380 pages / heavy code. Inferred from "normal
  foreign IT book" + the scope above.

## From Foundation

- The through-line is *why it works* (from `CLAUDE.md`), not *which config to set*.
- Running example: one synthetic but realistic dataset — vehicle GPS telemetry
  landing in an Iceberg table (echoes the user's real domain) plus a small
  dimensional model built from it. Reused across every chapter.
- One cluster shape is assumed for all worked examples and stated once in the
  Reference Environment front matter.

## From Architecture

- 5 parts (Execution · Making Queries Fast · Iceberg · Operating · Internals).
- The drafted §1.2 content ("The JVM and Executor Memory") becomes the chapter
  *How an Executor Uses Memory and CPU* in Part I.
- Part V (Internals) is positioned as "optional but rewarding," not required for
  the promise.
- Exercises are included but lightweight (no solutions appendix in v1).
