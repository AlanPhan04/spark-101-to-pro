# LaTeX Conventions — how this book's source is written

The manuscript **is** the LaTeX in `book/`. Never write chapters as Markdown
first; edit the `.tex` directly. Match the existing patterns exactly so the
build stays clean and the look stays uniform.

## 1. Repo layout

```
book/
├── main.tex                 preamble (macros, callouts, listings) + \part / \input structure
├── chapters/NN-<slug>.tex   19 chapters, one file each
├── appendices/a-…e-….tex    reference env · config reference · reading plans · glossary · reading
├── sections/                cover, preface, who-for, how-to-use, conventions, ref.bib
├── figures/<slug>.drawio    diagram source (authoritative)
├── figures/<slug>_render.py renderer → images/<slug>.pdf (via shared figures/_drawio.py)
├── images/<slug>.pdf        what \includegraphics loads
├── genesis/                 book-genesis planning: PROJECT_STATE.yaml + artifacts/00…08
├── build.ps1 / Makefile     xelatex → biber → xelatex ×2
```

Build (Windows, MiKTeX): `cd book; .\figures\build.ps1; .\build.ps1` — or
`make build` / `make quick` / `make check`. Requires **XeLaTeX + biber**
(fontspec + biblatex). After any edit, at minimum run a quick build and
`make check` (or read the log summary `build.ps1` prints) for undefined
references.

## 2. Chapter skeleton (copy `assets/latex/chapter-skeleton.tex`)

```latex
\chapter{Adaptive Query Execution}
\label{ch:aqe}

\begin{chapterintro}
<specimen symptom> … <what this chapter does / doesn't do> … <the payoff>.
\end{chapterintro}

\section{<Mechanism, in plain words>}
\label{sec:aqe-<short>}
…
\section{Summary}
\label{sec:aqe-summary}
<one prose paragraph restating the model> <bridge sentence to next chapter>

\exercisehead
\begin{exercises}
\item <run-and-observe on the specimen>
\item <read-this-plan>
\item <predict, then check>
\end{exercises}
```

Use `\subsection*{…}` or `\paragraph{…}` for unnumbered breakouts (the draft
uses both); numbered sections stop at `\section`/`\subsection` (secnumdepth 2).

## 3. Labels & cross-references

| Thing | Label | Reference |
|---|---|---|
| chapter | `\label{ch:<short>}` (e.g. `ch:shape`, `ch:catalyst`, `ch:aqe`) | `\Cref{ch:aqe}` → "Chapter 6" |
| section | `\label{sec:<chapter-short>-<topic>}` | `\Cref{sec:aqe-coalesce}` |
| figure | `\label{fig:<slug>}` — **same as the image file stem** | `\Cref{fig:job-stage-task}` |
| table | `\label{tab:<chapter-short>-<topic>}` | `\Cref{tab:shape-narrow-wide}` |
| listing | `label=lst:<chapter-short>-<topic>` in the `lstlisting` options | `\Cref{lst:shape-query}` |
| appendix | `\label{app:<short>}` | `\Cref{app:refenv}` → "Appendix A" |

Always `\Cref` (capitalised, cleveref) — never `Figure~\ref{}` by hand, never
"below/above". Every reference must resolve: `lint_chapter.py` checks this
across the whole book (it also reads `label=` inside listing options).

## 4. Macros & environments defined in `main.tex`

| Macro / env | Use |
|---|---|
| `\conf{spark.sql.shuffle.partitions}` | every config key inline — breakable monospace. Not `\texttt{}`. |
| `\texttt{orders}` | tables, columns, operators, functions, file names |
| `\emph{term}` | first use of a term (italic) |
| `\textbf{driver}` | role definitions; the one bold rule per chapter |
| `chapterintro` | the italic opener with a rule below it |
| `\exercisehead` + `exercises` | numbered exercises at chapter end |
| `note` | version gotcha, clarification, pointer to a later chapter |
| `warning` | a default/pattern that silently costs money, correctness, or data |
| `tip` | a diagnostic shortcut: a UI panel, a one-liner |
| `analogy` | bounded intuition; must say where it breaks; skippable |
| `definition` | theorem-style numbered definition (rarely used — prefer `\emph`) |
| `\tbd` | placeholder for an unwritten section (none remain) |

**Callout budget:** ≤ 1 per page in normal flow (~2 per 1,000 words), never two
back to back, never the only place a core idea is explained.

## 5. Figures

```latex
\begin{figure}[htbp]
  \centering
  \includegraphics[width=\linewidth]{shuffle-write-read-path.pdf}
  \caption{<Sentence 1: the takeaway.> <Sentence 2: how to read it — what the
  colors / dashed lines / red box mean.>}
  \label{fig:shuffle-write-read-path}
\end{figure}
```

- Introduce it first in prose: "…the write and read halves of a shuffle (\Cref{fig:shuffle-write-read-path})."
- Width is `\linewidth` by default; narrower widths make printed text smaller — check with `check_figures.py`, which reads the width from here.
- `[htbp]`, never `[H]` for figures (tables use `[H]` in places; leave those).
- Source/build rules for the PDF itself: `visual-system.md`.

## 6. Tables

```latex
\begin{table}[htbp]
\centering\footnotesize
\renewcommand{\arraystretch}{1.25}
\begin{tabular}{@{}p{3cm}p{5cm}p{5.5cm}@{}}
\toprule
\textbf{Strategy} & \textbf{What moves} & \textbf{When the planner picks it} \\
\midrule
… \\
\bottomrule
\end{tabular}
\caption{<takeaway sentence>}
\label{tab:joins-strategies}
\end{table}
```

booktabs only (no vertical rules), `@{}` outer padding, `p{}` columns summing
to ≲ 14.5 cm (text width is 16 cm). Every table gets a caption and a `tab:`
label — two in Ch 1 and several in the appendices currently lack them.

## 7. Listings

```latex
\begin{lstlisting}[language=SQL,caption={Forcing a broadcast with a hint},captionpos=b,label=lst:joins-hint]
SELECT /*+ BROADCAST(p) */ p.category, count(*)
FROM orders o JOIN dim_product p ON o.product_id = p.product_id
GROUP BY p.category;
\end{lstlisting}
```

- Languages in use: `SQL`, `scala` (≤ 15 lines), `text` (plans, UI, logs — `numbers=none`), `bash`.
- Plans: `language=text,numbers=none`, trimmed, elisions marked `-- ... 3 Filter nodes elided`; long plans add `basicstyle=\footnotesize\ttfamily,breaklines=false`.
- Every listing gets `caption=` and `label=lst:…` (26 currently lack a label — fix when touching them). Every listing that produces output shows it, labelled.
- Keep lines ≲ 85 chars at `\small` so nothing wraps on A4.

## 8. Math & numbers

- Arithmetic inline: `$6000\,\text{MB} / 128\,\text{MB} \approx 47$`. Use `\,` before units inside math, `~` before units in text (`64~MB`).
- Sizes in decimal MB/GB unless exactness matters (then MiB/GiB, and say so).
- `\times` for multiplication, `$\sim$180` for "about".

## 9. Bibliography

`sections/ref.bib` via biblatex; cite with `\cite{key}`. Cite the Spark/Iceberg
docs, SPIP/JIRA tickets (e.g. `SPARK-47208`), papers (Spark SQL SIGMOD'15,
Iceberg spec) for every non-obvious claim. Add entries in the existing style.

## 10. Keep `genesis/` in sync

After drafting or deepening a chapter, update `genesis/PROJECT_STATE.yaml`
(`chapters:` status + note, `figures:` status) and tick the row in
`genesis/artifacts/07-figure-list.md` when a figure goes from `spec` to `done`.
If the author uses the `book-genesis` skill too, its artifacts outrank this
skill on *planning* questions (scope, outline, figure list); this skill owns
*execution* (prose, figures, accuracy, lint).
