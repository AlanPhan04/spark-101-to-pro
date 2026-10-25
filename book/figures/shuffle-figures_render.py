#!/usr/bin/env python3
"""Chapter 4 measured figure (lab/exp_shuffle.py): shuffle bytes and time under each compression setting."""
import json
import os

import matplotlib.pyplot as plt

from bookplot import C, save, use_book_style

d = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "shuffle_codecs.json")))
names = ["none", "lz4", "snappy", "lzf", "zstd"]
use_book_style(2.7)
fig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 2.7))
cols = [C["rose"]] + [C["blue"]] * 3 + [C["green"]]
fills = [C["rose_fill"]] + [C["blue_fill"]] * 3 + [C["green_fill"]]
for ax, key, title, fmt in ((a, "mb", "shuffle bytes written (MB)", "{:,.0f}"), (b, "s", "wall clock (s)", "{:g}")):
    vals = [d[n][key] for n in names]
    ax.bar(range(5), vals, color=fills, edgecolor=cols, linewidth=1.2)
    for i, v in enumerate(vals):
        ax.text(i, v + max(vals) * 0.02, fmt.format(v), ha="center", fontsize=8, color=C["gray_ink"])
    ax.set_xticks(range(5)); ax.set_xticklabels(["off", "lz4", "snappy", "lzf", "zstd"], fontsize=8.5); ax.set_title(title, fontsize=9.5)
    ax.set_ylim(0, max(vals) * 1.15); ax.grid(axis="x", visible=False)
fig.tight_layout(); save(fig, "shuffle-codecs")
