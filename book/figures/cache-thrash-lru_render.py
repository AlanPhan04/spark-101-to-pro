#!/usr/bin/env python3
"""cache-thrash-lru.pdf: three MEMORY_ONLY caches that do not fit together, measured on the lab.

lab/exp_cache3.py thrash (4 GB heap, spark.memory.fraction=0.3, 2 cores). Fraction of each cache's partitions that
are still resident after each step; Spark evicts the least recently used blocks, one partition at a time.
"""
import matplotlib.pyplot as plt
import numpy as np

from bookplot import C, save, use_book_style

STEPS = ["cache ca", "cache cb", "cache cc", "re-read ca"]
CACHED = {"ca": [8, 8, 4, 8], "cb": [None, 8, 8, 4], "cc": [None, None, 8, 8]}   # partitions resident, of 8
COL = {"ca": C["blue"], "cb": C["orange"], "cc": C["green"]}
FILL = {"ca": C["blue_fill"], "cb": C["orange_fill"], "cc": C["green_fill"]}

use_book_style(3.1)
fig, ax = plt.subplots()
x = np.arange(len(STEPS))
w = 0.26
for i, name in enumerate(("ca", "cb", "cc")):
    vals = CACHED[name]
    heights = [0 if v is None else v for v in vals]
    ax.bar(x + (i - 1) * w, heights, w, color=FILL[name], edgecolor=COL[name], linewidth=1.1, label=name)
    for xi, v in zip(x, vals):
        if v is not None:
            ax.text(xi + (i - 1) * w, v + 0.15, f"{v}/8", ha="center", fontsize=8.5, color=C["gray_ink"])
ax.set_xticks(x)
ax.set_xticklabels(STEPS)
ax.set_ylim(0, 11.5)
ax.set_ylabel("partitions still cached (of 8)")
ax.legend(ncol=3, loc="upper left")
ax.annotate("ca loses half its blocks,\nleast recently used first", xy=(2 - w, 4.2), xytext=(0.0, 5.6), fontsize=9,
            color=C["blue_ink"], arrowprops=dict(arrowstyle="->", color=C["blue_ink"], lw=1.1))
ax.annotate("re-reading ca took 8.5 s\n(cc: 0.4 s) and evicted cb", xy=(3 + 0.0, 8.3), xytext=(1.5, 10.4), fontsize=9,
            color=C["rose_ink"], arrowprops=dict(arrowstyle="->", color=C["rose_ink"], lw=1.1))
ax.grid(axis="x", visible=False)
fig.tight_layout()
save(fig, "cache-thrash-lru")
