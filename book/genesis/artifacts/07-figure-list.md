# 07 — Figure list

Authoring convention: `references/prompts/diagramming.md`
(`book/figures/<slug>.drawio` + `<slug>_render.py` → `book/images/<slug>.pdf`).

Status: `spec` = described here only · `render` = ready to build · `done` = PDF committed.

| Slug | Ch | Type | Purpose (what prose can't do) | Pass | Status |
|---|---|---|---|---|---|
| `application-topology` | 1 | structure | driver / executors / cluster manager on K8s; where each piece lives | 1 | **done** |
| `query-submission-flow` | 1 | flow | the specimen from submit → compile → acquire → map → shuffle → reduce → collect → return | 1 | **done** |
| `job-stage-task` | 1 | structure | one query → 1 job → N stages (split at shuffles) → M tasks/stage; one red skewed task | 1 | **done** |
| `narrow-vs-wide` | 1 | structure | narrow = 1:1 partition dep, no move; wide = all-to-all, the shuffle | 1 | **done** |
| `catalyst-pipeline` | 2 | flow | SQL → unresolved → analyzed → optimized → physical → codegen; what each stage changes | 1 | **done** |
| `explain-anatomy` | 2 | listing | kept as an `lstlisting` in the chapter with prose call-outs, not a rendered figure | 1 | n/a |
| `executor-memory-model` | 3 | structure | heap (reserved / unified[exec\|storage] / user) + off-heap + overhead; container limit; 8 GB/2 GB numbers | 1 | **done** |
| `gc-pause-stall` | 3 | sequence | a stop-the-world pause freezing all 4 task slots at once; heartbeat timeout → executor lost | 1 | **done** |
| `shuffle-write-read-path` | 4 | flow | map task steps -> map output tracker -> reduce task steps, over the network | 1 | **done** |
| `partition-sizing` | 4 | plot | exact hyperbola (MB/task = shuffle bytes / partitions) for a 100 GB shuffle; target band + default-200 point | 1 | **done** |
| `join-strategies` | 5 | structure | the four strategies side by side: what shuffles, what broadcasts, what sorts | 1 | spec |
| `broadcast-vs-smj` | 5 | flow | same join, two plans; where the small side goes | 2 | spec |
| `aqe-coalesce` | 6 | before/after | 2000 tiny post-shuffle partitions (6 GB) → ~94 at 64 MB, at runtime | 2 | done |
| `aqe-skew-split` | 6 | structure | one 3.2 GB partition split into ~50; the small side replicated | 2 | done (redrawn, legible) |
| `aqe-feedback-loop` | 6 | flow | driver re-plans between stages from measured partition sizes | 2 | done |
| `pruning-layers` | 7 | structure | partition → manifest → file/row-group → bloom; each layer's input filter form | 1 | spec |
| `dpp-flow` | 7 | sequence | scan dim first → collect keys → filter fact partitions before scanning | 2 | done (redrawn, legible) |
| `pruning-static` | 7 | structure | 7 of 31 daily partitions read; 24 skipped at plan time | 2 | done |
| `bucketed-join` | 7 | before/after | two Exchanges vs a bucket-pair join with none | 2 | done |
| `storage-levels` | 8 | table-figure | MEMORY_AND_DISK / _SER / OFF_HEAP / DISK_ONLY vs GC cost vs read speed | 2 | spec |
| `iceberg-metadata-tree` | 9 | structure | catalog → metadata file → manifest list → manifests → data/delete files | 1 | spec |
| `iceberg-commit-swap` | 9 | sequence | write files → write new metadata → catalog swaps pointer atomically | 1 | spec |
| `catalog-pointer-swap` | 10 | sequence | two writers, optimistic concurrency, one wins the swap, the other retries | 2 | spec |
| `hidden-partitioning` | 11 | flow | `WHERE event_ts > ...` → Iceberg derives the partition predicate on `day(event_ts)` | 2 | spec |
| `partition-evolution` | 11 | before/after | old data in `day` partitions, new in `hour`, one table, no rewrite | 2 | spec |
| `pruning-layers-iceberg` | 12 | structure | extends `pruning-layers` with the manifest-list / manifest stats path | 1 | spec |
| `scan-metrics` | 12 | annotated | an Iceberg scan report with the pruning ratio at each layer marked | 2 | done |
| `file-stat-ranges` | 12 | quantitative | measured per-file customer_id min/max: unsorted 10/10 files overlap the key, sorted 1/200 | 2 | done |
| `pruning-layers-funnel` | 12 | funnel | the four pruning layers | 2 | done (redrawn, legible) |
| `cow-vs-mor` | 13 | structure | update on CoW (rewrite file) vs MoR (add delete file); read-time merge | 1 | spec |
| `maintenance-order` | 13 | flow | rewrite_data_files → expire_snapshots → remove_orphan_files → rewrite_manifests, and why the order | 2 | spec |
| `config-precedence` | 14 | structure | SparkConf < spark-defaults < CLI < session `SET` < query hint | 2 | spec |
| `ui-diagnostic-map` | 15 | annotated | the four UI tabs and the one question each answers | 1 | spec |
| `failure-signatures` | 15 | table-figure | OOM / fetch failure / straggler / GC-bound → what each looks like in the UI | 2 | spec |
| `microbatch-commit` | 16 | sequence | trigger → process micro-batch → one Iceberg commit; cadence = trigger interval | 2 | spec |
| `streaming-to-iceberg` | 16 | flow | continuous commits → small files → metadata growth → scheduled compaction | 2 | spec |
| `tungsten-row` | 17 | structure | a row as a packed off-heap byte layout vs an array of boxed Java objects | 2 | spec |
| `wholestage-codegen` | 17 | flow | an operator subtree collapsed into one generated Java method | 2 | spec |
| `shuffle-framework` | 18 | structure | shuffle manager, writers, map output tracker, block transfer service | 3 | spec |
| `scheduler-flow` | 18 | sequence | DAG scheduler → stages → task scheduler → executor backend | 3 | spec |
| `dsv2-pushdown-negotiation` | 19 | sequence | planner asks the source: these filters? these columns? this aggregate? | 3 | spec |

**Build now:** `executor-memory-model` only. Everything else is backlog; a
figure is authored when its chapter is drafted (pass 1 figures first).

## Added in the lab-backed pass (all legible, measured where quantitative)

| slug | ch | type | note | status |
|---|---|---|---|---|
| `coalesce-tasks` | 6 | plot | formula vs measured reduce-stage task counts (7 settings) | done |
| `aqe-broadcast-promotion` | 6 | before/after | initial SMJ vs final BHJ with measured sizes | done |
| `skew-partition-sizes` | 6 | plot | the 200 measured partition sizes vs the skew thresholds | done |
| `broadcast-vs-smj` | 5 | before/after | shuffle+sort both sides vs broadcast | done |
| `join-selection-flow` | 5 | flow | planner's strategy order | done |
| `scan-bytes-by-filter` | 7 | plot | bytes read for five spellings of one-day filter | done |
| `repartition-vs-coalesce` | 7 | stage graph | scan/shuffle/write structure for coalesce vs repartition | done |
| `lookup-bytes-by-layout` | 12 | plot | bytes read for one lookup across four layouts | done |
| `cache-breakeven` | 8 | plot | N reads with and without cache(), measured; break-even near 10 | done |
| `cache-eviction-measured` | 8 | stacked bar | a cached month before/after a join: memory vs disk, measured | done |
| `cache-thrash-lru` | 8 | plot | three caches that do not fit: LRU eviction per partition, measured | done |
| `reuse-exchange` | 8 | before/after | one exchange read twice vs the same exchange written twice | done |
| `metadata-tree-lab` | 9 | tree | the 3-commit table: catalog -> v3.metadata.json -> manifest list -> 3 manifests -> 5 files | done |
| `manifest-reuse` | 9 | reuse | three snapshots; each commit writes one manifest and reuses the rest | done |
| `sequence-number-rule` | 9 | rule | position delete at seq 5 applies to files at 1, 2, 4; not the later append at 6 | done |
| `delete-bytes-written` | 9 | plot | 34.8 MB (copy-on-write) vs 1.5 KB (merge-on-read) to delete one row | done |
| `commit-attempts` | 10 | plot | attempts per commit, 12 writers x 4 commits, retries 4 vs 0 (measured) | done |
| `commit-throughput` | 10 | plot | cumulative snapshots over time: one chain regardless of writer count (measured) | done |
| `catalog-pointer-types` | 10 | comparison | file-based vs HMS vs REST: where the pointer lives and how a loser is rejected | done |
