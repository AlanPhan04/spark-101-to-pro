import os

root = os.path.join(os.path.dirname(__file__), "..", "book", "figures")


def ed(f, a, b):
    p = os.path.join(root, f)
    s = open(p, encoding="utf-8").read()
    assert a in s, (f, a)
    open(p, "w", encoding="utf-8").write(s.replace(a, b))


ed("catalyst-figures_render.py",
   'labels = ["all rules", "no column\\npruning", "no predicate\\npushdown", "no constant\\nfolding", "none of\\nthe four"]',
   'labels = ["all\\nrules", "no\\ncolumn\\npruning", "no\\npredicate\\npushdown", "no\\nconstant\\nfolding", "none\\nof the\\nfour"]')
ed("catalyst-figures_render.py",
   "use_book_style(2.8)\nfig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 2.8))",
   "use_book_style(3.1)\nfig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 3.1))")
ed("cache-eviction-measured_render.py",
   'ax.legend(loc="lower right")',
   'ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, frameon=False)')
ed("tuning-figures_render.py",
   'ax.text(370, 520, "threshold\\nbetween\\n298 and 456"',
   'ax.text(370, 200, "threshold\\nbetween\\n298 and 456"')
ed("scheduler-figures_render.py",
   '''    a.text(i, r["seconds"] + 0.8, f"{r['seconds']:g} s", ha="center", fontsize=8, color=C["gray_ink"])''',
   '''    if i < len(t) - 1:
        a.text(i, r["seconds"] + 1.6, f"{r['seconds']:g} s", ha="center", fontsize=8, color=C["gray_ink"])
    else:
        a.text(i - 0.12, r["seconds"] - 0.5, f"{r['seconds']:g} s", ha="right", va="top", fontsize=8, color=C["gray_ink"])''')
