# Visual System — figures that replace paragraphs

The author's goal: a book that is *beautiful, colorful, and easy to
understand*, where pictures carry what would otherwise be long prose. A reader
who reads only the figures and captions of a chapter should still get its
mental model.

## 1. When a figure must replace text

Draw instead of writing (or draw first, then write less) whenever the prose would describe:

| The text describes… | Figure type | Existing example |
|---|---|---|
| who talks to whom | **topology** — boxes + labeled arrows | `application-topology` |
| an ordered process | **numbered flow** (top→bottom or left→right) | `query-submission-flow`, `catalyst-pipeline` |
| data being split / moved / regrouped | **partition boxes** with 1:1 or all-to-all edges | `narrow-vs-wide`, `aqe-skew-split` |
| nested structure / budgets | **nested containers**, area ∝ size where size matters | `executor-memory-model`, `unsaferow-layout` |
| a hierarchy / pointer chain | **tree**, top→down | `iceberg-metadata-tree` |
| events over time, concurrency, races | **timeline / swim-lanes** | `gc-pause-stall`, `catalog-commit-race` |
| a choice between alternatives | **side-by-side panels**, identical layout, one thing changed | `cow-vs-mor`, `join-strategies`, `dpp-flow` |
| successive filtering | **funnel** (narrowing bars) | `pruning-layers-funnel`, `ui-diagnostic-funnel` |
| a negotiation / protocol | **two-party exchange** | `dsv2-pushdown-negotiation` |
| a real quantitative relationship | **matplotlib plot** of the exact formula/measurement | `partition-sizing` |

**Trigger phrases:** if a paragraph says *first… then… meanwhile… finally*,
names more than three components, or compares two alternatives in prose — stop
and draw. If you write an enumerated list of steps, a figure usually belongs
next to it (Ch 1 pairs its 8-step list with `query-submission-flow`).

**Density target:** ≥ 3 figures per chapter (one *signature figure* that
installs the chapter's mental model + one per major mechanism), and never more
than ~900 words without a figure, table, or listing. Chapters 5–19 currently
have 1 figure each and Ch 14 has none — the biggest visual gap in the book.

## 2. Color = meaning (the book's existing palette, formalized)

Extracted from the 22 existing `.drawio` files — keep using exactly these
triples (fill / stroke / font). `check_figures.py` rejects anything else.

| Role | Fill | Stroke | Text | Meaning in this book |
|---|---|---|---|---|
| **Blue** | `#cfe0f4` | `#3b6ea5` | `#1f3d5c` | driver, planner, plan nodes, **the main path** of a flow; map side of a shuffle |
| Blue container | `#eaf1fb` / `#e7f0fb` | `#3b6ea5` | `#1f3d5c` | grouping box around blue things |
| **Green** | `#d8ebcf` | `#4f8a3d` | `#2f5320` | executors, tasks doing work, reduce side, **the good / fixed / succeeded state** |
| Green container | `#e4f1dc` / `#eaf4e3` | `#4f8a3d` | `#2f5320` | "with the fix" panel |
| **Rose** | `#f7dde0` | `#b5545e` | `#7d2f38` | **cost and failure**: shuffle boundary, Exchange, spill, skewed task, OOM-prone region, rejected commit, "without the fix" |
| Rose container | `#fdeef0` | `#b5545e` | `#7d2f38` | "before / without" panel |
| Rose edge (dense) | — | `#c99aa0` | — | many-to-many shuffle edges (lighter so 12+ lines stay readable) |
| **Orange** | `#fce7d2` | `#c77f3b` | `#7a4a17` | the **other party / alternative path**: storage memory, MoR, Iceberg-side components (ScanBuilder, manifests), retry path, borrowed space |
| **Purple** | `#ece6f4` | `#6a5a8a` | `#3f335c` | **infrastructure envelope**: cluster manager / Kubernetes, job wrapper, broadcast exchange, container limit, tracker on the driver |
| **Gray** | `#eceef1` | `#6b7280` | `#374151` | client, raw inputs (tables), reserved/unchanged, neutral steps |
| **Amber** | `#fbeecf` | `#c9a227` | `#7a5c0a` | attention / timeout — at most one per figure |
| Inks | — | `#2f3b52` | `#2f3b52`, `#57503f`, `#555555`, `#888888` | heavy frames, free-text annotations, edge labels, axes |

Rules:
1. **Rose is reserved for cost.** A reader should learn "red = this is where the time goes" by Chapter 1 and never be wrong after that.
2. **Green-container vs rose-container panels** mean *with vs without* the technique (AQE, DPP, CoW/MoR).
3. Text is always the dark variant of its hue on the light fill — never white text.
4. Never rely on color alone: pair rose with a **heavier stroke or dashed outline**, borrowed/optional with **dashed**, the main path with **thicker arrows**. The book may be printed in grayscale.
5. ≤ 4 hues + gray per figure. More means the figure is doing two jobs — split it.
6. Same concept, same hue, in every figure (driver is always blue, executor always green, Kubernetes always purple).

Known off-palette strays to fix when those figures are next touched:
`catalog-commit-race` (#8a7f6a), `catalyst-pipeline` (#e7eef7), `executor-memory-model`
overhead box (#f1eee7/#8a7f6a → use gray), `gc-pause-stall` & `query-submission-flow` (#999999 → #888888),
`narrow-vs-wide` panel (#eef6ea → #eaf4e3).

## 3. Print legibility — the #1 visual problem right now

Verified on the committed `main.pdf`: figure labels print at **4–5 pt** while
body text is 13 pt (every one of the 22 figures fails a 7 pt minimum). The
cause is geometry, not taste:

```
printed size (pt)  ≈  fontSize × 400 × width_fraction / pageWidth
                     (FONT_SCALE 1.18, CANVAS_DPI 66, 16 cm text width)
```

A `font-size:9px` span on a 740-px canvas at `\linewidth` prints at ≈ 4.9 pt.

| `pageWidth` | min `fontSize` for ≥ 8 pt at `\linewidth` | min for titles (≥ 9.5 pt) |
|---|---|---|
| 560 | 11 | 13 |
| 640 | 13 | 15 |
| 740 | 15 | 18 |
| 900 | 18 | 21 |

**Rules for every new or revised figure:**
- `pageWidth` **≤ 640**, base `fontSize` **≥ 13**, titles `≥ 15`, no `font-size:9px`/`10px` sub-lines. If the content doesn't fit, it's two figures, or the words belong in the caption.
- ≤ ~8 words per box. Labels are noun phrases, not sentences; explanation goes in the caption and prose.
- Run `check_figures.py <slug>` — it computes the real printed size from the PDF's width and the `\includegraphics` width, and flags text that overflows its box.
- Global alternative (author's call, one-line change): raise `FONT_SCALE` in `figures/_drawio.py`, then widen boxes in every `.drawio` until `check_figures.py` passes. Don't change it silently — it moves every figure at once.

## 4. The renderer and its limits (`figures/_drawio.py`)

draw.io desktop isn't installed in the author's toolchain; each `.drawio` is
hand-authored mxfile XML, and `_drawio.py` redraws it with matplotlib. It supports:

- vertices: `rounded=1` or square rectangles (`ellipse` → rounded), `fillColor`, `strokeColor`, `fontColor`, `strokeWidth`, `dashed=1`, `opacity`, `container=1` (drawn behind edges), free text via `text;` + `fillColor=none`
- labels: HTML with `<b>`, `<br>`, `<span style="font-size:Npx">`; `align=left|center`, `verticalAlign=top|middle`, `spacingLeft`, `spacingTop`
- edges: **straight lines only** between two vertex ids (or explicit source/target points); `exitX/exitY/entryX/entryY`; `dashed=1`; `endArrow=none`; `startArrow`; one midpoint label at a fixed 10 pt

It does **not** support: waypoints/orthogonal routing, curved edges, cylinders/hexagons/other shapes, edge-label positioning, icons, gradients. Design within that (it's why the book's figures are clean box diagrams). If a figure truly needs more, extend `_drawio.py` deliberately (e.g. add `<Array as="points">` waypoints) and re-render *all* figures to check nothing moved.

Coordinates: y grows downward; geometry is absolute px within the page. Lay
out on a **20-px grid**, align box edges, keep ≥ 30 px between sibling boxes
and ≥ 20 px padding inside containers.

## 5. Making a figure — workflow

1. **Caption first** — the takeaway sentence. If it needs "and", make two figures.
2. Pick the type (§1) and colors by role (§2). Sketch the grid: columns × rows, pageWidth ≤ 640.
3. Copy `assets/figure-template.drawio` → `book/figures/<slug>.drawio`; copy `assets/figure_render_template.py` → `book/figures/<slug>_render.py` (replace `<slug>`).
4. Write the cells. Use the palette style strings in the template verbatim.
5. Render: `python figures/<slug>_render.py` (or `.\figures\build.ps1` for all).
6. **Look at it.** Rasterize and open: `pdftoppm -png -r 110 -singlefile images/<slug>.pdf /tmp/<slug>` (or open the PDF). Check overlaps, arrows through boxes, clipped text, balance.
7. `python <skill>/scripts/check_figures.py <slug>` until clean.
8. Insert with the figure environment (`latex-conventions.md` §5), `\Cref` it before it appears.
9. Update `genesis/artifacts/07-figure-list.md` (status → **done**) and `PROJECT_STATE.yaml` `figures:`.

Quantitative figures: a `<slug>_render.py` that plots the exact formula or
measured data with `assets/bookplot.py` (same palette, fonts, sizes). Never fake data —
`partition-sizing` is the model: it plots the real hyperbola for the real worked example.

## 6. Signature figures & backlog

Each mental model needs one figure the reader could redraw from memory:

| Model | Signature figure | Status |
|---|---|---|
| M1 query tree rewritten & compiled | `catalyst-pipeline` | done — text too small, redo at ≤ 640 px |
| M2 partitions through stages; shuffle = wall | `job-stage-task` + `narrow-vs-wide` | done |
| M3 executor memory budget | `executor-memory-model` | done — label overlap at top, overhead box off-palette |
| M4 stats → plan | `join-strategies` + **`broadcast-vs-smj`** | 2nd one missing |
| M5 skew | `aqe-skew-split` | done — one label overflows |
| M6 Iceberg metadata tree | `iceberg-metadata-tree` | done |
| M7 pruning layers | `pruning-layers-funnel` | done |
| M8 CoW vs MoR | `cow-vs-mor` | done |

Backlog from `07-figure-list.md` not yet drawn (pass 1 first):
`broadcast-vs-smj` (Ch 5) · `aqe-coalesce` (Ch 6) · `storage-levels` (Ch 8) ·
`iceberg-commit-swap` (Ch 9) · `hidden-partitioning` (Ch 11) ·
`scan-metrics` (Ch 12) · `maintenance-order` (Ch 13) · **`config-precedence` (Ch 14 — has zero figures)** ·
`failure-signatures` (Ch 15) · `streaming-to-iceberg` (Ch 16) · `wholestage-codegen` (Ch 17).
Already built under different names: `pruning-layers`→`pruning-layers-funnel`,
`catalog-pointer-swap`→`catalog-commit-race`, `ui-diagnostic-map`→`ui-diagnostic-funnel`,
`microbatch-commit`→`microbatch-commit-loop`, `tungsten-row`→`unsaferow-layout`,
`shuffle-framework`/`scheduler-flow`→`scheduler-components`. Update the list.

Visual defects seen in the current renders (fix during a "figure pass"):
`executor-memory-model` title overlaps the Reserved box · `gc-pause-stall` heartbeat box overlaps slot rows ·
`aqe-skew-split` bottom-right label overflows · `catalog-commit-race` label collides with the swap box ·
`unsaferow-layout` variable-region label overflows · `catalyst-pipeline` / `query-submission-flow` /
`join-strategies` text far too small.

## 7. Captions

Readers read captions before body text. Caption = **sentence 1: the takeaway**,
sentence 2 (optional): **how to read it** (what red/dashed/green means here).

> ✗ `\caption{The shuffle.}`
>
> ✓ `\caption{A shuffle writes every map task's output to local disk, then each reduce task fetches its slice from every executor. The rose step is where spills happen on both sides.}`

The existing captions are already good (Ch 1's are the model) — keep that standard.

## 8. Composition rules

1. One message per figure.
2. Left→right = data flow / time; top→bottom = hierarchy, drill-down, funnel. Stay consistent.
3. Before/after panels: identical positions; change only what the lesson is about.
4. Size encodes quantity when quantity is the point (a 10 GB partition drawn visibly bigger than 2.5 GB ones).
5. Edge labels are verbs ("fetch over network"); node labels are nouns.
6. Number the steps (`1.`, `2.`) when order matters and layout alone can't show it.
7. Use names from the running example: `orders`, `dim_product`, `product_id`, `day(order_ts)` — not `TableA`.
8. ≤ 12 boxes. More → an overview figure now, a zoomed figure later.
9. Whitespace is part of the design; don't fill the canvas.
10. A one-line free-text annotation under the figure is allowed (warm ink `#57503f`), but if it's longer than a line, it belongs in the caption.

## 9. Beyond figures — making the book itself more colorful

Today the callouts are grayscale (`black!3` fills), code is blue/red keywords
on white, and the page is thesis-style (A4, 1.5 spacing). For a colorful,
published look, propose — don't impose — the drop-in in
`assets/latex/colorful-callouts.tex`: palette-matched `note` (blue), `tip`
(green), `warning` (rose), `analogy` (amber), plus listing colors in the same
palette. It replaces the four `\newtcolorbox` blocks in `main.tex`; the
environment names don't change, so no chapter needs editing. Show the author a
before/after page (`pdftoppm` the rebuilt page) and let him decide.
