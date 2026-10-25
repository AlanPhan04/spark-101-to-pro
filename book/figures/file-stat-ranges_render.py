#!/usr/bin/env python3
"""Render file-stat-ranges.pdf from the lab's measured per-file min/max of customer_id.

Top panel: ten files of an unsorted table; every file's [min, max] spans (almost) the whole key
range, so a point lookup cannot exclude any of them. Bottom panel: 200 files of the same rows
sorted by customer_id; the ranges are disjoint and the lookup key falls inside exactly one.
Data: figures/data/ranges_t_plain.csv and ranges_t_sorted.csv (lab/exp_ranges.py).
"""
import csv
import os

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from bookplot import C, save, use_book_style

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = 1774971          # the customer_id looked up in the experiment (c01774971)
MAX_ID = 2_000_000


def load(name):
    with open(os.path.join(HERE, "data", name), newline="") as f:
        r = csv.DictReader(f)
        return [(int(x["lo"]), int(x["hi"])) for x in r]


plain = load("ranges_t_plain.csv")
srt = load("ranges_t_sorted.csv")

use_book_style()
fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.3, 4.4), gridspec_kw={"height_ratios": [2.2, 1]}, sharex=True)

# unsorted: one row per file
for i, (lo, hi) in enumerate(plain):
    hit = lo <= KEY <= hi
    a1.add_patch(Rectangle((lo, i + 0.15), hi - lo, 0.7,
                           facecolor=C["rose_fill"] if hit else C["gray_fill"],
                           edgecolor=C["rose"] if hit else C["gray"], lw=1.0))
a1.set_ylim(0, len(plain))
a1.set_yticks([])
a1.set_title("Unsorted: 10 files, all 10 must be opened", color=C["rose_ink"])
a1.grid(False)

# sorted: one thin cell per file
for lo, hi in srt:
    hit = lo <= KEY <= hi
    a2.add_patch(Rectangle((lo, 0.1), hi - lo, 0.8,
                           facecolor=C["green_fill"] if hit else C["gray_fill"],
                           edgecolor=C["green"] if hit else C["gray"], lw=0.6 if not hit else 1.4))
a2.set_ylim(0, 1)
a2.set_yticks([])
a2.set_title("Sorted by customer_id: 200 files, 1 must be opened", color=C["green_ink"])
a2.grid(False)

for ax in (a1, a2):
    ax.axvline(KEY, color=C["rose_ink"], lw=1.6, ls="--", zorder=5)
a1.text(KEY - 30_000, len(plain) - 0.2, "lookup key", ha="right", va="top", fontsize=9, color=C["rose_ink"])
a2.set_xlim(0, MAX_ID)
a2.set_xlabel("customer_id (per-file min to max, from the manifest)")
a2.set_xticks([0, 500_000, 1_000_000, 1_500_000, 2_000_000])
a2.set_xticklabels(["0", "0.5M", "1M", "1.5M", "2M"])
fig.tight_layout()
save(fig, "file-stat-ranges")
