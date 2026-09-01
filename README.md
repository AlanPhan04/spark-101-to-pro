# Spark Learning Journey — Zero to Advanced

A personal learning path through Apache Spark, focused on **SparkSQL query 
optimization** and the **Lakehouse (Apache Iceberg)** — since that's the 
production stack I work with daily.

## 🎯 Goal

Not just "which config to set", but understanding **why** it works — 
from the Catalyst optimizer, to the execution model, to the Iceberg 
metadata layer.

## 🗂️ Structure

Each learning/chat session maps to one Markdown file, capturing:
- Questions asked
- Concepts learned
- Real-world queries optimized
- Key learnings & pitfalls

## 📈 Roadmap

8 phases, ~83 hours total:

| Phase | Topic |
|-------|-------|
| 0 | Prerequisites (SQL, JVM, distributed systems, file formats) |
| 1 | Spark Fundamentals (execution model, Job/Stage/Task) |
| 2 | SparkSQL & Catalyst Optimizer |
| 3 | Query Optimization (Join, Skew, Partitioning, Shuffle) ⭐ |
| 4 | Lakehouse & Apache Iceberg ⭐ |
| 5 | Runtime Tuning & Config |
| 6 | Debugging & Profiling |
| 7 | Streaming (optional) |
| 8 | Advanced & Internals |

**Stack:** Spark 3.5.2 · Apache Iceberg v2 · Kyuubi · Hive Metastore · GCS · GKE

## 🛠️ Related project

Companion repo: [DQ monitoring system](#) for Iceberg tables on the 
Lakehouse — applying knowledge from this roadmap directly to production.
