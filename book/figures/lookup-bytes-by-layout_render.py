#!/usr/bin/env python3
"""lookup-bytes-by-layout.pdf: one customer_id lookup on four copies of the same 9.7M rows (lab, measured)."""
import matplotlib.pyplot as plt

from bookplot import C, save, use_book_style

LABELS = ["unsorted", "unsorted + bloom filter", "sorted by customer_id", "sorted, metrics = counts"]
MB = [60.5, 28.9, 0.2, 1.5]
FILES = [10, 10, 1, 200]
SKIPPED = [0, 0, 199, 0]

use_book_style(2.7)
fig, ax = plt.subplots()
y = list(range(len(LABELS)))
cols = [C["rose"], C["orange"], C["green"], C["blue"]]
fills = [C["rose_fill"], C["orange_fill"], C["green_fill"], C["blue_fill"]]
ax.barh(y, MB, color=fills, edgecolor=cols, linewidth=1.2, height=0.6)
ax.set_yticks(y)
ax.set_yticklabels(LABELS, fontsize=9.5)
ax.invert_yaxis()
for i, (v, f, s) in enumerate(zip(MB, FILES, SKIPPED)):
    ax.text(v + 1.0, i, f"{v:g} MB read, {f} file{'s' if f > 1 else ''} opened" + (f", {s} skipped" if s else ""),
            va="center", fontsize=9, color=C["gray_ink"])
ax.set_xlim(0, 105)
ax.set_xlabel("bytes read for one equality lookup (MB)")
ax.grid(axis="y", visible=False)
fig.tight_layout()
save(fig, "lookup-bytes-by-layout")
