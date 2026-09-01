# Book source — *Apache Spark: A Practical Guide*

LaTeX source for the PDF guide. Structure follows the 8-phase roadmap in the
repository `README.md`. This is currently a **skeleton**: every leaf section is a
`[Section to be written.]` placeholder. Content is filled in later, priority
order Phase 2 → 3 → 4.

## Build

Requires a LaTeX distribution with **XeLaTeX + biber** (the Times New Roman font
via `fontspec` and the `biblatex` bibliography both need this):

```powershell
winget install MiKTeX.MiKTeX   # if not already installed; then restart the terminal
cd book
.\build.ps1                     # xelatex -> biber -> xelatex x2, then sweeps artifacts
```

Other targets: `.\build.ps1 -Quick` (one pass, text-only edits),
`.\build.ps1 -Clean`, `.\build.ps1 -Distclean`. A `Makefile` with the same
targets is provided for `make` users.

Output: `book/main.pdf`.

## Layout

| Path | Contents |
|------|----------|
| `main.tex` | preamble, front/back matter, chapter include list |
| `sections/` | cover page, preface, glossary, references, `ref.bib` |
| `chapters/` | one file per phase, `01`–`09` |
| `appendices/` | cluster reference, config cheat sheet, internal classes, further reading |
| `images/` | figures (none yet) |

The preamble is adapted from the `capstone_thesis` template: `report` class,
XeLaTeX, `biblatex`, `listings`, `titlesec` chapter headings, `cleveref`,
`\newtheorem{definition}`.
