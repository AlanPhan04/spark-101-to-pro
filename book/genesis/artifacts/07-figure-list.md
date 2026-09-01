# 07 — Figure list

Authoring convention: `references/prompts/diagramming.md`
(`book/figures/<slug>.drawio` + `<slug>_render.py` → `book/images/<slug>.pdf`).

Status: `spec` = described here only · `render` = ready to build · `done` = PDF committed.

| Slug | Ch | Type | Purpose (what prose can't do) | Pass | Status |
|---|---|---|---|---|---|
| `application-topology` | 1 | structure | driver / executors / cluster manager on K8s; where each piece lives | 1 | spec |
| `job-stage-task` | 1 | structure | one query → 1 job → N stages (split at shuffles) → M tasks/stage | 1 | spec |
| `catalyst-pipeline` | 2 | flow | SQL string → unresolved → analyzed → optimized → physical → codegen; what each stage may change | 1 | spec |
| `explain-anatomy` | 2 | annotated | a real `EXPLAIN FORMATTED` with call-outs on PartitionFilters / PushedFilters / Exchange / `*(n)` codegen markers | 1 | spec |
| `executor-memory-model` | 3 | structure | heap (reserved / unified[exec\|storage] / user) + off-heap + overhead; container limit brace; 8 GB/2 GB worked numbers; spill vs OOM annotations | **now** | render |
| `gc-pause-stall` | 3 | sequence | a stop-the-world pause freezing all tasks on an executor at once; heartbeat timeout | 2 | spec |
| `shuffle-write-read-path` | 4 | flow | map task: serialize → sort → spill → map-side file; reduce task: fetch → merge; the disk+network hop | 1 | spec |
| `partition-sizing` | 4 | plot | shuffle-read size vs partition count vs per-task size; the spill zone and the tiny-task zone | 2 | spec |
| `join-strategies` | 5 | structure | the four strategies side by side: what shuffles, what broadcasts, what sorts | 1 | spec |
| `broadcast-vs-smj` | 5 | flow | same join, two plans; where the small side goes | 2 | spec |
| `aqe-coalesce` | 6 | before/after | 2000 tiny post-shuffle partitions → ~50 right-sized, at runtime | 2 | spec |
| `aqe-skew-split` | 6 | structure | one 10 GB partition split into 5; the small side replicated 5× | 2 | spec |
| `pruning-layers` | 7 | structure | partition → manifest → file/row-group → bloom; each layer's input filter form | 1 | spec |
| `dpp-flow` | 7 | sequence | scan dim first → collect keys → filter fact partitions before scanning | 2 | spec |
| `storage-levels` | 8 | table-figure | MEMORY_AND_DISK / _SER / OFF_HEAP / DISK_ONLY vs GC cost vs read speed | 2 | spec |
| `iceberg-metadata-tree` | 9 | structure | catalog → metadata file → manifest list → manifests → data/delete files | 1 | spec |
| `iceberg-commit-swap` | 9 | sequence | write files → write new metadata → catalog swaps pointer atomically | 1 | spec |
| `catalog-pointer-swap` | 10 | sequence | two writers, optimistic concurrency, one wins the swap, the other retries | 2 | spec |
| `hidden-partitioning` | 11 | flow | `WHERE event_ts > ...` → Iceberg derives the partition predicate on `day(event_ts)` | 2 | spec |
| `partition-evolution` | 11 | before/after | old data in `day` partitions, new in `hour`, one table, no rewrite | 2 | spec |
| `pruning-layers-iceberg` | 12 | structure | extends `pruning-layers` with the manifest-list / manifest stats path | 1 | spec |
| `scan-metrics` | 12 | annotated | an Iceberg scan report with the pruning ratio at each layer marked | 2 | spec |
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
