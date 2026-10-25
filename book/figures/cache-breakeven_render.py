#!/usr/bin/env python3
"""cache-breakeven.pdf: total seconds for N aggregations over one week of orders, with and without cache().

Measured on the lab (lab/exp_cache3.py sweep, warm JVM): the cache costs 4.1-5.0 s to build and saves about
0.4 s per read, so it pays only past roughly ten reads.
"""
import matplotlib.pyplot as plt

from bookplot import C, save, use_book_style

READS = [1, 2, 5, 10]
NO_CACHE = [2.77, 3.15, 7.54, 14.37]          # N uncached aggregations
CACHE = [6.60, 6.69, 9.57, 14.70]             # materialize + N cached aggregations

use_book_style(3.2)
fig, ax = plt.subplots()
ax.plot(READS, NO_CACHE, marker="o", color=C["rose"], label="no cache: read the source each time")
ax.plot(READS, CACHE, marker="s", color=C["green"], label="cache(): build once, then read memory")
ax.fill_between(READS, NO_CACHE, CACHE, where=[c > n for c, n in zip(CACHE, NO_CACHE)], color=C["rose_fill"], alpha=0.7, lw=0)
ax.set_xlabel("number of aggregations over the same week")
ax.set_ylabel("total seconds")
ax.set_xticks(READS)
ax.annotate("cache loses:\nit costs more to build\nthan it saves", xy=(2, 5.0), xytext=(2.6, 9.5), fontsize=9,
            color=C["rose_ink"], arrowprops=dict(arrowstyle="->", color=C["rose_ink"], lw=1.1))
ax.annotate("break-even near 10 reads", xy=(10, 14.5), xytext=(5.8, 15.4), fontsize=9, color=C["gray_ink"],
            arrowprops=dict(arrowstyle="->", color=C["gray_ink"], lw=1.1))
ax.set_ylim(0, 18)
ax.legend(loc="upper left")
fig.tight_layout()
save(fig, "cache-breakeven")
