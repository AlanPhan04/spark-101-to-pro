import os

root = os.path.join(os.path.dirname(__file__), "..", "book")


def edit(rel, pairs):
    p = os.path.join(root, rel)
    s = open(p, encoding="utf-8", newline="").read()
    for a, b in pairs:
        if a not in s:
            print("MISSING in", rel, ":", a[:60])
        s = s.replace(a, b, 1)
    open(p, "w", encoding="utf-8", newline="").write(s)


edit("main.tex", [
    ("{20pt}{\\Huge}", "{20pt}{\\Huge\\raggedright\\hyphenpenalty=10000 \\exhyphenpenalty=10000 }"),
])
edit("chapters/06-adaptive-query-execution.tex", [
    ("\\begin{tabular}{@{}rll@{}}\n\\toprule\n\\textbf{Adaptive threshold}", "\\begin{tabular}{@{}rlP{5.2cm}@{}}\n\\toprule\n\\textbf{Adaptive threshold}"),
])
edit("chapters/10-catalogs-and-commits.tex", [
    ("\\begin{tabular}{@{}lll@{}}\n\\toprule\n\\textbf{Property}", "\\begin{tabular}{@{}P{5.6cm}P{2.0cm}P{6.4cm}@{}}\n\\toprule\n\\textbf{Property}"),
])
