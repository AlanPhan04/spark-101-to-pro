# Drafting Playbook — from first draft to published depth

Every chapter has a complete first draft. The book is ~35k words toward a
~120–150k target, so most sessions will be **deepening** a chapter, not
writing from nothing. This file says how, in what order, and what "done" means.

## 1. Definition of done for a chapter

| Dimension | Target |
|---|---|
| Length | 6,000–9,000 words (≈ 18–25 printed pages at the book's 13 pt / 1.5 spacing) |
| Figures | ≥ 3: the chapter's signature figure + one per major mechanism; all pass `check_figures.py` |
| Listings | ≥ 4, each with real output (or `% CAPTURE:` marker) — `EXPLAIN FORMATTED`, `SET`, metadata-table queries, UI/metric readouts |
| Specimen | the chapter's mechanism is shown *on the specimen query or the `orders` schema*, with reference-cluster arithmetic |
| Tables | every "which one" decision is a booktabs table with caption + `tab:` label |
| Callouts | ≤ 2 per 1,000 words; at least one `tip` with a UI/metric shortcut |
| Exercises | 3: run-and-observe · read-a-plan · predict-then-check |
| Lint | `lint_chapter.py` no errors; warnings fixed or consciously kept |
| Accuracy | `spark-accuracy.md` §6 checklist passed; 4.x differences noted |
| State | `PROJECT_STATE.yaml` + `07-figure-list.md` updated |

## 2. The deepening loop (one section at a time)

For each section of the chapter, in order:

1. **Read the section and its neighbours.** Note the claim, the evidence present, the evidence missing.
2. **Find the missing beat** of the five-beat pattern (symptom → picture → name → prove → lever). The draft usually has *name* and *lever*; it is usually missing *symptom*, *picture*, and *prove*.
3. **Add the proof:** the listing that shows it on `orders` + the output + "Put numbers on it" arithmetic on 40 slots / 16 GB executors.
4. **Add or plan the picture** if the section describes structure/flow/comparison (`visual-system.md` §1). Caption first.
5. **Split walls:** paragraphs > 140 words → split; an enumeration in prose → `enumerate` or a table.
6. **Polish words** (`voice-and-style.md` §5) — remove *just/simply/very*, unify terms.
7. **Build + lint** after each section: `make quick` (or `.\build.ps1 -Quick`) and `lint_chapter.py <file>`.
8. Show the author the diff for that section before moving on when the change is large.

Never pad. Depth means *more evidence and more mechanism*, not more adjectives.
If a section is complete at 400 words, leave it at 400 words.

## 3. Priority order

1. **Errata** (`spark-accuracy.md` §4) — wrong defaults first; they poison later chapters' arithmetic.
2. **Part II (Ch 4–8)** — the promise lives here ("predict the plan, fix the slow stage"). Ch 6 (1.3k words, 0 listings) and Ch 7 (1.3k) are the thinnest in the core.
3. **Part III (Ch 9–13)** — Iceberg; Ch 9, 11, 12 have no listings at all — add `SELECT * FROM orders.snapshots / .manifests / .files` style metadata-table evidence.
4. **Ch 14** — zero figures, zero listings; draw `config-precedence`, add a worked sizing listing.
5. **Part I polish** (Ch 1–3) — already the strongest; mainly figure legibility and a 2nd listing each.
6. **Part V** (optional internals) last.

## 4. Thinnest sections right now (words, excluding listings)

| Words | Ch | Section | What's missing |
|---|---|---|---|
| 83 | 13 | Rewriting manifests | when manifests fragment, `rewrite_manifests` call + before/after `.manifests` counts |
| 86 | 6 | Reading an AQE plan | a real `AdaptiveSparkPlan isFinalPlan=true` listing with `AQEShuffleRead coalesced / skewed` annotated |
| 94 | 12 | Vectorized reads | what the reader gains (batch size, Arrow/columnar), how to see it in the plan (`BatchScan … ColumnarToRow`) |
| 102 | 8 | When caching pays | a cost model: recompute cost × reuse count vs memory + GC; the Storage tab readout |
| 107 | 5 | Sort-merge join | the plan shape (Exchange → Sort → SMJ) as listing + `broadcast-vs-smj` figure |
| 109 | 14 | Configuration precedence and profiles | `config-precedence` figure; Kyuubi session vs engine conf |
| 115 | 14 | Parallelism defaults | `shuffle.partitions` vs `default.parallelism` vs file splits, on 40 slots |
| 117 | 6 | `parallelismFirst` | correct semantics (ignores advisory size) + a worked example |
| 119 | 11 | Target file size / small files | `write.target-file-size-bytes`, distribution mode, a `.files` size histogram (bookplot) |
| 119 | 18 | The map output tracker | what it stores, fetch-failure → stage resubmission |
| 121 | 6 | SMJ → broadcast at runtime | plan before/after; the AQE broadcast threshold |
| 123 | 12 | Column stats & pushdown into Iceberg | `metrics` per column, a `.files` query showing lower/upper bounds |
| 125 | 10 | The Hive Metastore catalog | how the pointer swap is implemented on HMS (lock / `metadata_location`) |
| 126 | 8 | Exchange and subquery reuse | `ReusedExchange` in a plan listing |
| 131 | 12 | Bloom filters | table property, when they help (point lookups on high-cardinality), cost |

Re-generate it rather than trusting it: `python <skill>/scripts/lint_chapter.py --sections 20`.

## 5. Listing ideas that fit the running example

- `EXPLAIN FORMATTED` of the specimen — Ch 2 has it (`lst:explain-anatomy`); later chapters should show **how their mechanism changes that same plan** (broadcast hint, AQE final plan, DPP `dynamicpruningexpression`, bucketed/storage-partitioned join removing the Exchange).
- `SET spark.sql.autoBroadcastJoinThreshold = -1;` then re-`EXPLAIN` — before/after.
- Iceberg metadata tables: `SELECT * FROM orders.snapshots`, `.manifests`, `.files` (record_count, file_size_in_bytes, lower_bounds), `.partitions`.
- Iceberg procedures: `CALL catalog.system.rewrite_data_files(table => 'orders', ...)`, `expire_snapshots`, `remove_orphan_files`, `rewrite_manifests`.
- `ANALYZE TABLE dim_product COMPUTE STATISTICS FOR ALL COLUMNS` — and what Iceberg tables actually expose to Spark's CBO.
- Spark UI readouts as `text` listings: Stage Summary Metrics rows (min/25th/median/75th/max), Executors tab rows.
- Kyuubi: session-level `SET` vs engine config (`kyuubi.engine.share.level`).

## 6. Working with the author

- He writes to Claude in Vietnamese; reply in Vietnamese, write the book in English.
- He prefers concise, direct answers and Markdown deliverables for reference material.
- Before restructuring a chapter, moving sections between chapters, or changing a canonical term, ask — the outline in `genesis/artifacts/06-outline.md` is his.
- For anything that changes every page (callout colors, fonts, page size, `FONT_SCALE`), show a before/after render and let him decide.
