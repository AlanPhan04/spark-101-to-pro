#!/usr/bin/env python3
"""scan-bytes-by-filter.pdf: bytes read for one day of orders, five ways to write the filter (lab, measured)."""
import matplotlib.pyplot as plt

from bookplot import C, save, use_book_style

LABELS = [
    "order_ts >= .. AND order_ts < ..",
    "date(order_ts) = DATE '..'",
    "CAST(order_ts AS DATE) = DATE '..'",
    "CAST(order_ts AS STRING) LIKE '..%'",
    "order_ts + INTERVAL 1 DAY > ..",
]
MB = [6.7, 6.7, 6.7, 207.3, 207.3]          # input bytes of the scan stage, lab run
TASKS = [1, 1, 1, 31, 31]

use_book_style(2.9)
fig, ax = plt.subplots()
y = range(len(LABELS))
cols = [C["green"] if v < 10 else C["rose"] for v in MB]
fills = [C["green_fill"] if v < 10 else C["rose_fill"] for v in MB]
ax.barh(list(y), MB, color=fills, edgecolor=cols, linewidth=1.2, height=0.62)
ax.set_yticks(list(y))
ax.set_yticklabels(LABELS, family="monospace", fontsize=8.5)
ax.invert_yaxis()
for i, (v, t) in enumerate(zip(MB, TASKS)):
    ax.text(v + 3, i, f"{v:g} MB, {t} task{'s' if t > 1 else ''}", va="center", fontsize=9,
            color=C["green_ink"] if v < 10 else C["rose_ink"])
ax.set_xlim(0, 270)
ax.set_xlabel("input bytes read by the scan (MB)")
ax.grid(axis="y", visible=False)
fig.tight_layout()
save(fig, "scan-bytes-by-filter")
