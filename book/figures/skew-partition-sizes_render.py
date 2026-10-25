#!/usr/bin/env python3
"""skew-partition-sizes.pdf: the lab's 200 reduce partitions of the skewed join, measured.

Data: figures/data/skew_tasks_aqe_off.csv (lab/export_task_sizes.py on the AQE-coalescing-off run).
Each bar is the shuffle bytes one reduce task read. One bar is the viral product's key.
"""
import csv
import os

import matplotlib.pyplot as plt

from bookplot import C, annotate, save, use_book_style

HERE = os.path.dirname(os.path.abspath(__file__))
rows = sorted(int(r["shuffle_read_bytes"]) for r in csv.DictReader(open(os.path.join(HERE, "data", "skew_tasks_aqe_off.csv"))))
mb = [b / 1e6 for b in rows]
median = mb[len(mb) // 2]

use_book_style(3.6)
fig, ax = plt.subplots()
colors = [C["rose"] if v == mb[-1] else C["blue_fill"] for v in mb]
edges = [C["rose_ink"] if v == mb[-1] else C["blue"] for v in mb]
ax.bar(range(len(mb)), mb, color=colors, edgecolor=edges, linewidth=0.4, width=0.9)
ax.set_yscale("log")
ax.set_ylim(0.5, 700)
ax.set_xlim(-2, len(mb) + 1)
ax.set_xlabel("the 200 reduce partitions, sorted by size")
ax.set_ylabel("shuffle read per task (MB, log scale)")
ax.grid(axis="x", visible=False)

ax.axhline(median, color=C["gray"], lw=1.0, ls=":")
ax.text(2, median * 1.12, f"median {median:.1f} MB", fontsize=9, color=C["gray_ink"])
ax.axhline(5 * median, color=C["orange"], lw=1.2, ls="--")
ax.text(2, 5 * median * 1.12, f"5 x median = {5 * median:.1f} MB (relative test)", fontsize=9, color=C["orange_ink"])
ax.axhline(32, color=C["purple"], lw=1.2, ls="--")
ax.text(2, 32 * 1.12, "lab floor 32 MB", fontsize=9, color=C["purple_ink"])
ax.axhline(64, color=C["green"], lw=1.2, ls="--")
ax.text(2, 64 * 1.12, "64 MB default advisory size (split target)", fontsize=9, color=C["green_ink"])
ax.axhline(256, color=C["rose"], lw=1.2, ls="--")
ax.text(2, 256 * 1.12, "256 MB default floor", fontsize=9, color=C["rose_ink"])
annotate(ax, f"viral product: {mb[-1]:.1f} MB,\n{mb[-1] / median:.0f} x the median", xy=(len(mb) - 1, mb[-1]),
         xytext=(len(mb) - 78, 2.2), color=C["rose_ink"])
fig.tight_layout()
save(fig, "skew-partition-sizes")
