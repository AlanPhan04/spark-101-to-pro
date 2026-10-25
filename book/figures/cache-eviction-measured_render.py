#!/usr/bin/env python3
"""cache-eviction-measured.pdf: a cached month of orders before and after a join runs in the same application.

Lab, 4 GB heap (unified memory about 2.3 GB), MEMORY_AND_DISK (lab/exp_cache3.py borrow). All 31 partitions stay
cached, but 235 MB more of them live on disk after the join needed execution memory.
"""
import matplotlib.pyplot as plt

from bookplot import C, save, use_book_style

BEFORE = (2252.7, 175.6)       # (memory MB, disk MB)
AFTER = (1930.6, 410.4)

use_book_style(2.6)
fig, ax = plt.subplots()
labels = ["after cache().count()", "after a join ran"]
mem = [BEFORE[0], AFTER[0]]
disk = [BEFORE[1], AFTER[1]]
y = [0, 1]
ax.barh(y, mem, color=C["blue_fill"], edgecolor=C["blue"], label="in storage memory", height=0.55)
ax.barh(y, disk, left=mem, color=C["orange_fill"], edgecolor=C["orange"], label="spilled to disk", height=0.55)
for yi, m, d in zip(y, mem, disk):
    ax.text(m / 2, yi, f"{m:,.0f} MB", ha="center", va="center", fontsize=9, color=C["blue_ink"])
    ax.text(m + d + 25, yi, f"{d:,.0f} MB on disk", va="center", fontsize=9, color=C["orange_ink"])
ax.set_yticks(y)
ax.set_yticklabels(labels)
ax.invert_yaxis()
ax.set_xlim(0, 3300)
ax.set_xlabel("cached bytes of orders (MB), 31 of 31 partitions in both rows")
ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, frameon=False)
ax.grid(axis="y", visible=False)
fig.tight_layout()
save(fig, "cache-eviction-measured")
