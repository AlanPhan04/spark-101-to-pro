#!/usr/bin/env python3
"""Chapter 5 measured figure (lab/exp_joins.py): the three equi-join strategies forced by hint on three dimensions."""
import json
import os

import matplotlib.pyplot as plt

from bookplot import C, save, use_book_style

res = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "joins_results.json")))
dims = ["dim_date (365 rows)", "dim_customer (2M rows)", "dim_product (2M rows, 170 MB)"]
strat = [("BROADCAST", "broadcast hash", C["green"], C["green_fill"]), ("SHUFFLE_HASH", "shuffled hash", C["blue"], C["blue_fill"]), ("MERGE", "sort-merge", C["rose"], C["rose_fill"])]
use_book_style(2.9)
fig, ax = plt.subplots(figsize=(6.3, 2.9))
w = 0.26
for j, (h, label, col, fill) in enumerate(strat):
    vals = [next(r["seconds"] for r in res if r.get("build") == d and r.get("hint") == h) for d in dims]
    xs = [i + (j - 1) * w for i in range(3)]
    ax.bar(xs, vals, w, color=fill, edgecolor=col, linewidth=1.2, label=label)
    for x, v in zip(xs, vals):
        ax.text(x, v + 0.15, f"{v:g}", ha="center", fontsize=8.5, color=C["gray_ink"])
ax.set_xticks(range(3)); ax.set_xticklabels(["dim_date\n365 rows", "dim_customer\n2 M rows", "dim_product\n2 M rows, 170 MB"], fontsize=8.5)
ax.set_ylabel("seconds (join with 30 M orders)"); ax.set_ylim(0, 14); ax.legend(loc="upper left", ncol=3, fontsize=8.5); ax.grid(axis="x", visible=False)
fig.tight_layout(); save(fig, "join-strategy-times")
