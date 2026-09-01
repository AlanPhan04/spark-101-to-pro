# 01 — Competing and adjacent titles

## Comps

### 1. *High Performance Spark*, 2nd ed. — Holden Karau, Adi Polak, Rachel Warren (O'Reilly, 2026)
- **Does well:** the canonical performance book; covers the shuffle, joins,
  serialization, key skew, and dips into the code base. Spark 3.x. Written by
  committers.
- **Gap this book fills:** broad across the whole engine (RDD, DataFrame, ML,
  streaming), so any one mechanism gets a section, not a chapter. Iceberg is not
  its subject. It is a "best practices" book more than a "trace one query all the
  way down" book.

### 2. *Spark: The Definitive Guide* — Bill Chambers, Matei Zaharia (O'Reilly, 2018)
- **Does well:** the standard on-ramp; complete tour of the DataFrame/SQL API,
  written by the creators.
- **Gap:** Spark 2.x era — pre-AQE, pre-modern Iceberg, pre-Kubernetes-default.
  API reference, not an optimizer or metadata book.

### 3. *Learning Spark*, 2nd ed. — Damji, Wenig, Das, Lee (O'Reilly, 2020)
- **Does well:** clearest beginner path; Spark 3.0; good on the DataFrame API and
  a first look at Catalyst and the Spark UI.
- **Gap:** foundational by design. Stops where this book starts: it shows that
  Catalyst exists; it does not teach you to predict or change a plan.

### 4. *Apache Iceberg: The Definitive Guide* — Shiran, Hughes, Merced (O'Reilly, 2024)
- **Does well:** the Iceberg reference — spec, metadata tree, partitioning,
  maintenance, catalogs.
- **Gap:** engine-agnostic with a Dremio lean. Spark is one of several readers.
  It explains Iceberg; it does not explain what Spark's planner does with Iceberg
  metadata, or how the two optimizers interact.

### 5. *Designing Data-Intensive Applications* — Martin Kleppmann (O'Reilly, 2017)
- **Does well:** the systems-thinking reference — storage engines, columnar
  formats, partitioning, consistency.
- **Gap:** not about Spark or Iceberg at all. It is the background this book
  assumes, not a competitor.

Adjacent free resource: Jacek Laskowski's *The Internals of Spark SQL* (online
gitbook) — deep but reference-structured and not version-anchored; a lookup, not
a book you read.

## Whitespace statement

No current book traces a single Spark SQL query from Catalyst, through physical
planning, the shuffle, and AQE, into the Iceberg metadata layer and back — on a
Kubernetes object-storage stack — and teaches the reader to predict and change
that path. *High Performance Spark* is the nearest neighbour but is broad and
Iceberg-silent; *Apache Iceberg: TDG* is deep on the format but engine-neutral.
This book owns the **Catalyst ↔ Iceberg seam**, mechanism-first, for the modern
lakehouse stack.
