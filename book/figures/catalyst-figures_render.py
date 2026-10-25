#!/usr/bin/env python3
"""Chapter 2 measured figure (lab/exp_catalyst.py): bytes read and time with one optimizer rule excluded."""
import json
import os

import matplotlib.pyplot as plt

from bookplot import C, save, use_book_style

d = [x for x in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "catalyst_rules.json"))) if "V2" not in x["variant"]]
labels = ["all rules", "no column\npruning", "no predicate\npushdown", "no constant\nfolding", "none of\nthe four"]
use_book_style(2.8)
fig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 2.8))
cols = [C["green"]] + [C["rose"]] * 3 + [C["gray"]]
fills = [C["green_fill"]] + [C["rose_fill"]] * 3 + [C["gray_fill"]]
for ax, key, title, fmt in ((a, "mb", "bytes read from Parquet (MB)", "{:,.0f}"), (b, "seconds", "wall clock (s)", "{:g}")):
    vals = [x[key] for x in d]
    ax.bar(range(5), vals, color=fills, edgecolor=cols, linewidth=1.2)
    for i, v in enumerate(vals):
        ax.text(i, v + max(vals) * 0.02, fmt.format(v), ha="center", fontsize=8, color=C["gray_ink"])
    ax.set_xticks(range(5)); ax.set_xticklabels(labels, fontsize=7); ax.set_title(title, fontsize=9); ax.set_ylim(0, max(vals) * 1.15); ax.grid(axis="x", visible=False)
fig.tight_layout(); save(fig, "optimizer-rules-measured")
