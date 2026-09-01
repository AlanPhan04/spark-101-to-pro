# Book source — *Spark Query Optimization and the Iceberg Lakehouse*

LaTeX source for the book. A practitioner's deep dive into why a Spark SQL query
runs the way it does — from the Catalyst optimizer, through the shuffle and the
execution model, into the Iceberg metadata layer — and how to change it.

Currently a **skeleton**: the full part/chapter/section structure is in place and
every leaf section is a `[Section to be written.]` placeholder. Chapter 3's
"executor memory model" material is drafted. Content is filled in chapter by
chapter.

Planning artifacts (brief, comps, reader/promise, mental models, outline, figure
list) live in [`genesis/`](genesis/), produced by the `book-genesis` pipeline.

## Build

Requires a LaTeX distribution with **XeLaTeX + biber** (Times New Roman via
`fontspec` and the `biblatex` bibliography both need this):

```powershell
winget install MiKTeX.MiKTeX   # if not already installed; then restart the terminal
cd book
.\figures\build.ps1            # regenerate figure PDFs from the .drawio sources
.\build.ps1                    # xelatex -> biber -> xelatex x2, then sweeps artifacts
```

Other targets: `.\build.ps1 -Quick`, `-Clean`, `-Distclean`. A `Makefile` with
the same targets is provided for `make` users.

Output: `book/main.pdf` (git-ignored — regenerate with `build.ps1`).

## Layout

| Path | Contents |
|------|----------|
| `main.tex` | preamble, `\part` structure, front/back matter, chapter includes |
| `sections/` | cover page, preface, "who this book is for", "how to use", "conventions", `references.tex`, `ref.bib` |
| `chapters/` | 19 chapters, `01`–`19`, across 5 parts |
| `appendices/` | reference environment · config reference · reading query plans · glossary · further reading |
| `figures/` | `<slug>.drawio` sources + `<slug>_render.py` matplotlib renderers |
| `images/` | generated figure PDFs (`\includegraphics` targets) |
| `genesis/` | `book-genesis` planning artifacts (`PROJECT_STATE.yaml`, `artifacts/`) |

## Figures

Diagrams follow the `.drawio` + matplotlib-renderer convention (no draw.io CLI
needed): each figure is `figures/<slug>.drawio` (hand-authored mxfile) plus
`figures/<slug>_render.py` (parses it, redraws with matplotlib) producing
`images/<slug>.pdf`. `figures/build.ps1` runs every renderer. Edit the `.drawio`
in the draw.io app to refine, then re-run the renderer (or export PDF from the
app directly).

## Structure

Preamble adapted from the `capstone_thesis` template, then moved to the `book`
class: `\frontmatter` / `\mainmatter` / `\backmatter`, `\part` dividers, XeLaTeX,
`biblatex`, `tcolorbox` callouts (`note` / `warning` / `tip`), `listings`,
`cleveref`. The full outline is in [`genesis/artifacts/06-outline.md`](genesis/artifacts/06-outline.md).
