#!/usr/bin/env python3
"""Chapter 11 measured figures, all from the lab (lab/exp_layout1.py, lab/exp_layout2.py):

  partition-granularity   day vs hour partitions of one month of orders
  sort-vs-zorder          files read per lookup on an unsorted, sorted and Z-ordered table
  distribution-modes      files written per mode into a day-partitioned table
  bucket-hot-key          bytes per bucket of bucket(16, product_id) with one viral product
  evolution-cost          one day of old (month spec) vs new (day spec) data
"""
import csv
import os

import matplotlib.pyplot as plt
import numpy as np

from bookplot import C, save, use_book_style

HERE = os.path.dirname(os.path.abspath(__file__))


def value_labels(ax, bars, fmt="{:g}", dy=0.0, color=None):
    for b in bars:
        h = b.get_height()
        ax.text(b.get_x() + b.get_width() / 2, h + dy, fmt.format(h), ha="center", va="bottom", fontsize=8.5,
                color=color or C["gray_ink"])


# --- partition granularity ------------------------------------------------------------------------------------------------------------
use_book_style(2.9)
fig, axes = plt.subplots(1, 3, figsize=(6.3, 2.9))
labels = ["day", "hour"]
cols = [C["green"], C["rose"]]
fills = [C["green_fill"], C["rose_fill"]]
for ax, vals, title, fmt in (
    (axes[0], [31, 744], "files in the table", "{:g}"),
    (axes[1], [34.8, 1.43], "average file (MB)", "{:g}"),
    (axes[2], [7, 168], "files read, one week", "{:g}"),
):
    bars = ax.bar(labels, vals, color=fills, edgecolor=cols, linewidth=1.2)
    value_labels(ax, bars, fmt, dy=max(vals) * 0.02)
    ax.set_title(title, fontsize=9.5)
    ax.set_ylim(0, max(vals) * 1.18)
    ax.grid(axis="x", visible=False)
fig.tight_layout()
save(fig, "partition-granularity")

# --- sort vs Z-order -------------------------------------------------------------------------------------------------------------------------------
use_book_style(3.1)
fig, ax = plt.subplots()
layouts = ["unsorted", "sorted by\n(customer, product)", "Z-order\n(customer, product)"]
READ = {"customer id": [50, 1, 24], "product id": [50, 43, 3], "both": [50, 1, 2]}
x = np.arange(3)
w = 0.26
for i, (name, col, fill) in enumerate((("customer id", C["blue"], C["blue_fill"]), ("product id", C["orange"], C["orange_fill"]), ("both", C["green"], C["green_fill"]))):
    bars = ax.bar(x + (i - 1) * w, READ[name], w, color=fill, edgecolor=col, linewidth=1.1, label=f"lookup on {name}")
    value_labels(ax, bars, dy=0.8)
ax.set_xticks(x)
ax.set_xticklabels(layouts, fontsize=8.5)
ax.set_ylabel("data files read (of 43 to 50)")
ax.set_ylim(0, 62)
ax.legend(loc="upper right", fontsize=8.5)
ax.grid(axis="x", visible=False)
fig.tight_layout()
save(fig, "sort-vs-zorder")

# --- distribution modes ----------------------------------------------------------------------------------------------------------------------------------
use_book_style(2.6)
fig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 2.6))
modes = ["none", "hash", "range"]
files = [100, 10, 10]
sizes = [3.64, 34.78, 34.78]
bars = a.bar(modes, files, color=[C["rose_fill"], C["green_fill"], C["green_fill"]], edgecolor=[C["rose"], C["green"], C["green"]], linewidth=1.2)
value_labels(a, bars, dy=2)
a.set_title("files written (10 days)", fontsize=9.5)
a.set_ylim(0, 118)
a.grid(axis="x", visible=False)
bars = b.bar(modes, sizes, color=[C["rose_fill"], C["green_fill"], C["green_fill"]], edgecolor=[C["rose"], C["green"], C["green"]], linewidth=1.2)
value_labels(b, bars, dy=0.8)
b.set_title("average file (MB)", fontsize=9.5)
b.set_ylim(0, 42)
b.grid(axis="x", visible=False)
fig.tight_layout()
save(fig, "distribution-modes")

# --- bucket hot key ---------------------------------------------------------------------------------------------------------------------------------------
rows = list(csv.DictReader(open(os.path.join(HERE, "data", "bucket_sizes.csv"))))
mb = [float(r["mb"]) for r in rows]
hot = int(np.argmax(mb))
use_book_style(2.8)
fig, ax = plt.subplots()
bars = ax.bar(range(len(mb)), mb, color=[C["rose_fill"] if i == hot else C["blue_fill"] for i in range(len(mb))],
              edgecolor=[C["rose"] if i == hot else C["blue"] for i in range(len(mb))], linewidth=1.0)
ax.set_xticks(range(len(mb)))
ax.set_xticklabels([r["bucket"] for r in rows], fontsize=8)
ax.set_xlabel("bucket(16, product_id)")
ax.set_ylabel("MB of data files")
ax.annotate(f"viral product's bucket: {mb[hot]:.0f} MB,\n{mb[hot] / np.median(mb):.1f} x the median", xy=(hot, mb[hot]), xytext=(hot - 6.5, mb[hot] * 0.82), fontsize=9,
            color=C["rose_ink"], arrowprops=dict(arrowstyle="->", color=C["rose_ink"], lw=1.1))
ax.grid(axis="x", visible=False)
fig.tight_layout()
save(fig, "bucket-hot-key")

# --- evolution cost ---------------------------------------------------------------------------------------------------------------------------------------
use_book_style(2.7)
fig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 2.7))
labels = ["old data\n(month spec)", "new data\n(day spec)"]
bars = a.bar(labels, [517.0, 34.8], color=[C["rose_fill"], C["green_fill"]], edgecolor=[C["rose"], C["green"]], linewidth=1.2)
value_labels(a, bars, dy=8)
a.set_title("data file opened for a\none-day query (MB)", fontsize=9.5)
a.set_ylim(0, 600)
a.grid(axis="x", visible=False)
bars = b.bar(labels, [11.3, 0.97], color=[C["rose_fill"], C["green_fill"]], edgecolor=[C["rose"], C["green"]], linewidth=1.2)
value_labels(b, bars, dy=0.2)
b.set_title("rows decoded for that\nquery (millions)", fontsize=9.5)
b.set_ylim(0, 13.5)
b.grid(axis="x", visible=False)
fig.tight_layout()
save(fig, "evolution-cost")
