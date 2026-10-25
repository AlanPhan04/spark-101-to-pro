"""Turn p{..} columns of every tabular/longtable in the book into ragged-right P{..} columns."""
import glob
import os
import re

root = os.path.join(os.path.dirname(__file__), "..", "book")
pat = re.compile(r"\\begin\{(?:tabular|longtable)\}\{[^\n]*")
for f in glob.glob(os.path.join(root, "chapters", "*.tex")) + glob.glob(os.path.join(root, "appendices", "*.tex")):
    s = open(f, encoding="utf-8", newline="").read()
    n = pat.sub(lambda m: m.group(0).replace("p{", "P{"), s)
    if f.endswith("b-configuration-reference.tex"):
        n = n.replace("P{6.0cm}P{2.1cm}P{6.2cm}", "P{6.6cm}P{2.3cm}P{5.7cm}")
    if n != s:
        open(f, "w", encoding="utf-8", newline="").write(n)
        print(os.path.basename(f))
