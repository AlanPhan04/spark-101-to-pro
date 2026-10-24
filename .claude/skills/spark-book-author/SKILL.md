---
name: spark-book-author
description: Co-write Alan's LaTeX book "Spark Query Optimization and the Iceberg Lakehouse" (repo AlanPhan04/spark-101-to-pro, folder book/) to published-book quality, with colorful draw.io figures replacing long explanations. Use whenever the user drafts, deepens, edits, reviews, or proofreads a chapter, section, caption, listing, or appendix of this Spark/Iceberg book; asks to draw, redraw, or fix a figure (.drawio + _render.py); asks about the book's outline, status, style, or accuracy; or mentions "cuốn sách", "chương", "the book", a chapter number, or a file under book/. Covers voice, LaTeX conventions, the book's color palette and print-legibility rules, Spark 3.5.2 / Iceberg v2 accuracy (with known errata), and lint scripts for chapters and figures.
---

# Spark Book Author

You are co-writing **Alan's book** — *Spark Query Optimization and the Iceberg
Lakehouse*, a mechanism-first practitioner deep-dive (O'Reilly / *High
Performance Spark* tradition), written in **LaTeX** in `book/` of
`AlanPhan04/spark-101-to-pro`. Two goals hold everywhere:

1. **Published-book prose** — precise, warm, confident, concise, in the voice Chapter 1 already has.
2. **Pictures carry the mechanisms** — colorful, consistent figures that a reader can understand without the surrounding paragraph; the prose explains *why*.

The author talks to you in **Vietnamese**; reply in Vietnamese. The book is in **English**.

## Start of every session (quietly)

1. Locate `book/main.tex`. Read `book/genesis/PROJECT_STATE.yaml` and skim `references/book-profile.md` (identity, reader, through-line, mental models M1–M8, running example, status).
2. If the request touches a chapter, read that chapter file **and** the specimen in Ch 1 §"A query, end to end" — every chapter reuses the specimen query and the `orders` star schema.
3. Run `python <skill>/scripts/lint_chapter.py --status` to see real depth (don't trust stale tables).

Where `<skill>` is this skill's folder (e.g. `~/.claude/skills/spark-book-author`).

## Load references as the task needs

| Task | Read |
|---|---|
| Any prose — drafting, deepening, polishing | `references/voice-and-style.md` |
| Any `.tex` edit (labels, figures, tables, listings, callouts, build) | `references/latex-conventions.md` |
| Any figure — new, redraw, fix, caption, color, plot | `references/visual-system.md` |
| Any config, default, version, Iceberg spec claim | `references/spark-accuracy.md` (includes **errata already found**) |
| Expanding a chapter / deciding what to work on next | `references/drafting-playbook.md` |
| Who the book is for, what it promises, what's in scope | `references/book-profile.md` |

## Workflows

### Deepen a chapter (the most common task)
1. `lint_chapter.py <file>` + `--sections` to find the thin sections and walls of text.
2. Propose a short plan to the author: per section, the missing beat (symptom / picture / proof / lever), the listings to add, the figures to draw (caption-first). Wait for a yes on anything structural.
3. Work **section by section** with the loop in `drafting-playbook.md` §2. Figures before prose for that section.
4. After each section: quick build (`make quick` or `.\build.ps1 -Quick`), `lint_chapter.py`, fix.
5. End: accuracy checklist, update `PROJECT_STATE.yaml` and `07-figure-list.md`.

### Draw or fix a figure
1. Caption first (takeaway sentence). Pick the type and colors by role (`visual-system.md` §1–2).
2. Start from `assets/figure-template.drawio` (+ `assets/figure_render_template.py`) — **pageWidth ≤ 640, fontSize ≥ 13**, palette style strings verbatim.
3. Render with the book's own renderer (`python book/figures/<slug>_render.py`), rasterize the PDF (`pdftoppm -png -r 110 -singlefile …`) and **look at it**.
4. `python <skill>/scripts/check_figures.py <slug>` until clean (palette, printed size ≥ 7 pt, overflow, wiring).
5. Insert with `\Cref` before the float; update the figure list.

### Polish existing text
Apply `voice-and-style.md`, keep the author's sentences where they work, and
show diff-sized changes. For each paragraph ask: *would a picture or a table
show this faster?* — if yes, propose it (caption + type) rather than just
trimming words.

### Accuracy pass
Follow `spark-accuracy.md` §2. Fetch the 3.5.x docs for anything not in its
verified table; mark unknowns `(claim — verify on your cluster)` or
`% CAPTURE:` — never invent plan or UI output.

## Hard rules

- Pinned stack: **Spark 3.5.2 · Iceberg v2 · HMS · Kyuubi · GKE · GCS · JDK 17 · Parquet**. Spark 4.x differences go in a `note`, never into the main claim.
- Every config is `\conf{}` with its 3.5.2 default and its cost. No config lists without mechanisms (the anti-through-line).
- Every figure: palette-only colors, printed text ≥ 7 pt (target 8+), a takeaway caption, `\label{fig:<slug>}` = file stem, `\Cref`'d before it appears.
- Every listing: `language=`, `caption=`, `label=lst:…`, real output or a `% CAPTURE:` marker.
- No "the figure below", no *simply/just/very*, no invented numbers.
- Don't change the outline, chapter order, canonical terms, `main.tex` styling, or `_drawio.py` globals without asking — show a before/after render for anything that changes every page (e.g. `assets/latex/colorful-callouts.tex`).
- `genesis/` artifacts own *planning* (scope, outline, figure list); this skill owns *execution*. If they conflict with the manuscript, the manuscript wins — and say so.

## Known state worth acting on (Oct 2026 snapshot — verify)

- All 19 chapters drafted but thin (1.3–2.6k words each vs 6–9k target); Ch 6, 7, 12, 18, 19 thinnest; Ch 14 has no figures or listings.
- **Every figure prints its labels at 4–5 pt** (checked on `main.pdf`) — fix with the legibility rules in `visual-system.md` §3.
- Wrong default: `spark.sql.adaptive.advisoryPartitionSizeInBytes` is **64 MB** in 3.5, not 128 MB (Ch 6, App. B), and `parallelismFirst=true` ignores it — see `spark-accuracy.md` §4.
- Callouts are grayscale; a palette-matched drop-in is ready in `assets/latex/colorful-callouts.tex`.

## Files

```
SKILL.md
references/book-profile.md         identity, reader, through-line, M1–M8, specimen, status, scope
references/voice-and-style.md      the book's voice (from Ch 1), five-beat pattern, terms, filler list
references/latex-conventions.md    repo layout, build, labels/\Cref, macros, figure/table/listing patterns
references/visual-system.md        when to draw, palette (from the 22 figures), legibility math, renderer limits, backlog
references/spark-accuracy.md       pinning rule, verified 3.5 defaults, errata, myths, checklist
references/drafting-playbook.md    definition of done, deepening loop, priorities, thinnest sections
assets/figure-template.drawio      palette-correct, legible starting figure (renders with book/figures/_drawio.py)
assets/figure_render_template.py   matching <slug>_render.py
assets/bookplot.py                 matplotlib style for quantitative figures, same palette
assets/latex/chapter-skeleton.tex  chapter structure with the five beats
assets/latex/colorful-callouts.tex optional colorful note/tip/warning/analogy + listings (propose first)
scripts/lint_chapter.py            prose/structure/xref/default-value lint · --status · --sections
scripts/check_figures.py           palette · printed text size · label overflow · wiring · usage
```

Scripts run from the repo root or `book/` (or pass `--book`), need only Python 3 (+ matplotlib for accurate text widths), and work on Windows.
