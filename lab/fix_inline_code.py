"""Make long unbreakable inline \\texttt{token} breakable by switching it to \\conf{token} (URL-style breaking)."""
import glob
import os
import re

root = os.path.join(os.path.dirname(__file__), "..", "book")
skip_line = re.compile(r"^\s*\\(caption|section|subsection|subsubsection|chapter|paragraph|label|Cref|cref)")
tok = re.compile(r"\\texttt\{((?:[A-Za-z0-9_.\-()<>,=*/:]|\\_)+)\}")
total = 0
for f in glob.glob(os.path.join(root, "chapters", "*.tex")) + glob.glob(os.path.join(root, "appendices", "*.tex")):
    out, in_lst, changed = [], False, 0
    for line in open(f, encoding="utf-8", newline="").read().split("\n"):
        if "\\begin{lstlisting}" in line or "\\begin{verbatim}" in line:
            in_lst = True
        if not in_lst and not skip_line.match(line):
            def sub(m):
                t = m.group(1).replace("\\_", "_")
                if len(t) >= 15:
                    return "\\conf{" + t + "}"
                return m.group(0)
            new = tok.sub(sub, line)
            if new != line:
                changed += 1
                line = new
        if "\\end{lstlisting}" in line or "\\end{verbatim}" in line:
            in_lst = False
        out.append(line)
    if changed:
        open(f, "w", encoding="utf-8", newline="").write("\n".join(out))
        print(os.path.basename(f), changed)
        total += changed
print("lines changed", total)
