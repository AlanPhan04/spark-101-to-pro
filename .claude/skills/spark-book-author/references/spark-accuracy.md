# Spark & Iceberg Accuracy — pinned to the reference stack

The book's credibility rests on every number being right *for Spark 3.5.2 /
Iceberg format v2*. Nothing here overrides the pinning rule in
`genesis/artifacts/05-conventions.md`; it operationalizes it.

## 1. Version rule

- State behavior as fact only if it holds on **Spark 3.5.2 / Iceberg v2**.
- Quote defaults **as of 3.5.2**. If a default changed across versions (3.0→3.2→3.5) or changes in **Spark 4.x**, add a `note` naming the version.
- Spark 3.5 reached end of community support in 2026 and Spark 4.0/4.1 are out. Readers *will* run 4.x. So every chapter should carry the 4.x differences that touch its topic, in a `note` — never by changing the pinned stack.

Spark 4.0 changes most likely to need a note (verify each in the 4.0 release notes / migration guide before writing it):
- `spark.sql.ansi.enabled` default **false → true** (overflow, invalid casts, divide-by-zero now throw).
- Java 17+ and Scala 2.13 only; Spark Connect matured.
- `VARIANT` type, SQL pipe syntax (`|>`), string collations, SQL UDFs — mention only where relevant (scope excludes Spark Connect as a subject).

## 2. Verification protocol

1. **Docs for the pinned version** — prefer `https://spark.apache.org/docs/3.5.x/…` (the exact 3.5.2 pages sometimes fail to fetch; any 3.5.x patch page has the same defaults): `configuration.html`, `sql-performance-tuning.html`, `sql-ref-ansi-compliance.html`, `running-on-kubernetes.html`, `tuning.html`. Iceberg: `iceberg.apache.org/spec/`, `/docs/latest/configuration/`, `/docs/latest/spark-*`.
2. **Source** when docs are vague: `sql/catalyst/.../SQLConf.scala` (defaults + `.version()`), `core/.../internal/config/package.scala`.
3. **Run it** on the reference cluster for every `EXPLAIN`, UI number, and timing; paste real output. If not yet run, leave `% CAPTURE: …` in the source and keep the prose honest ("the plan will contain…").
4. Performance numbers need setup (data size, cluster shape — App. A) or a citation.
5. Unverifiable → "(claim — verify on your cluster)". Never smooth it over.
6. After any config edit, `lint_chapter.py` cross-checks stated defaults against the table below.

## 3. Verified Spark 3.5.x defaults

Checked against the official 3.5.x performance-tuning page (Oct 2026):

| Key | 3.5 default |
|---|---|
| `spark.sql.shuffle.partitions` | 200 |
| `spark.sql.autoBroadcastJoinThreshold` | 10 MB (10485760) |
| `spark.sql.adaptive.autoBroadcastJoinThreshold` | (unset → same as above) |
| `spark.sql.adaptive.enabled` | true (since 3.2.0) |
| `spark.sql.adaptive.advisoryPartitionSizeInBytes` | **64 MB** |
| `spark.sql.adaptive.coalescePartitions.minPartitionSize` | 1 MB |
| `spark.sql.adaptive.coalescePartitions.parallelismFirst` | true |
| `spark.sql.adaptive.skewJoin.skewedPartitionFactor` | 5.0 |
| `spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes` | 256 MB |
| `spark.sql.adaptive.localShuffleReader.enabled` | true |
| `spark.sql.files.maxPartitionBytes` | 128 MB |

Widely documented core defaults (re-verify on `configuration.html` before
printing a new one): `spark.memory.fraction` 0.6 · `spark.memory.storageFraction`
0.5 · reserved memory 300 MB · `spark.executor.memoryOverhead` = max(384 MB,
`memoryOverheadFactor` 0.10 × executor memory) · `spark.sql.files.openCostInBytes`
4 MB · `spark.reducer.maxSizeInFlight` 48m · `spark.shuffle.file.buffer` 32k ·
`spark.executor.heartbeatInterval` 10s · `spark.network.timeout` 120s ·
`spark.sql.ansi.enabled` **false** on 3.5.

**`parallelismFirst` nuance:** with the default `true`, Spark *ignores*
`advisoryPartitionSizeInBytes` when coalescing and only respects
`minPartitionSize`, targeting the cluster's default parallelism. Any worked
example that coalesces "toward 64 MB" must either set `parallelismFirst=false`
or explain why the result differs.

## 4. Errata found in the current draft (fix these)

| Where | Says | Should be |
|---|---|---|
| Ch 6 `sec:aqe-coalesce` (line ~40) | advisory size "128 MB by default"; worked example coalesces 6 GB → ~47 partitions | 64 MB default; and under default `parallelismFirst=true` the merge doesn't aim at the advisory size — redo the example (≈ 94 at 64 MB with `parallelismFirst=false`, or show the parallelism-first result on 40 slots) |
| Ch 6 `sec:aqe-parallelism` | "smaller than the 128 MB advisory size" | 64 MB; and describe that parallelism-first *ignores* the advisory size rather than checking it second |
| Ch 4 line ~190 recommended settings | sets `advisoryPartitionSizeInBytes = 128 MB` | a deliberate override is fine, but say it doubles the 64 MB default, and add `parallelismFirst = false` — otherwise AQE ignores the advisory size and the listing doesn't do what the prose promises |
| App. B config table (line ~71) | 128 MB | 64 MB |
| Ch 1 vs App. A | specimen uses sort-merge because `dim_product` has no stats / `dim_product` broadcasts under defaults | pick one for the specimen and explain via Iceberg's `sizeInBytes` estimate (Ch 5) |
| App. A vs genesis brief | catalog = HMS / HMS + Iceberg REST | reconcile |

Re-run `python <skill>/scripts/lint_chapter.py --all` after fixes; it detects
the prose cases automatically.

## 5. Myths the book must never repeat (and must actively correct)

| Myth | Reality |
|---|---|
| "Spark is in-memory, so it doesn't touch disk" | Shuffles always write local disk; spills happen under memory pressure; caches can be disk-backed |
| "`cache()` caches it now" | Lazy — materialized by the next action, partition by partition |
| "`repartition` ≈ `coalesce`" | `repartition` always shuffles and balances; `coalesce` merges without a shuffle, can't increase, can unbalance and cut upstream parallelism |
| "More partitions is faster" | Scheduling overhead + tiny files; size from bytes (Ch 4's hyperbola) |
| "One action = one stage" | One action → ≥ 1 job → stages split at shuffles → one task per partition |
| "Executors are threads" | Executors are JVM processes; tasks are threads in slots |
| "The driver processes data" | It plans/schedules; `collect()`/`toPandas()` pull data *to* it — classic driver OOM |
| "Broadcast is always faster" | Only when the small side truly is small; the driver collects it first; estimates can be wrong (M4) |
| "Raise executor memory to fix a slow stage" | Skew isn't fixed by memory (M5); check max-vs-median task time first |
| "`groupByKey` vs `reduceByKey`" as current advice | RDD-era; DataFrame aggregates already do partial aggregation |
| "AQE fixes everything" | Only re-plans after a shuffle; can't fix the first stage, unsplittable files, or a planning-time shuffle |
| "Iceberg = Parquet with time travel" | A metadata tree the planner reads *instead of* data (M6/M7) |
| "Partition pruning works with any WHERE" | A function on the source column, a cast, or a non-transform predicate can defeat a pruning layer (M7) |
| "MoR is faster" | Faster writes, slower reads until compaction — a schedule decision (M8) |

## 6. End-of-chapter accuracy checklist

- [ ] Every `\conf{}` key spelled exactly; default + version where relevant
- [ ] `lint_chapter.py` reports no default mismatches
- [ ] Every `EXPLAIN`/UI excerpt is real output or marked `% CAPTURE:`
- [ ] Figures match the plan/code (stage count, Exchange placement, join type, partition counts)
- [ ] Worked arithmetic uses App. A's cluster (4 cores, 16 GB, 10 executors → 40 slots)
- [ ] Spark 4.x differences that touch the chapter are in a `note`
- [ ] No myth from §5 slipped in through casual phrasing
- [ ] Terms match `voice-and-style.md` §5
