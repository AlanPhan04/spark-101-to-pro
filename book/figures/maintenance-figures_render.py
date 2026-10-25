#!/usr/bin/env python3
"""Chapter 13 measured figures from the lab (lab/exp_maint.py, results in lab/out/maint_results.json):

  update-cost-cow-mor   ten small UPDATEs: seconds and bytes written per update
  merge-scan-bytes      MERGE with and without a partition predicate in ON
  stream-small-files    60 tiny commits: files, manifests, scan time through compaction and manifest rewrite
  expire-orphans        directory size through expire_snapshots and remove_orphan_files
"""
import matplotlib.pyplot as plt
import numpy as np

from bookplot import C, save, use_book_style


def labels(ax, bars, fmt="{:g}", dy=0.0):
    for b in bars:
        h = b.get_height()
        ax.text(b.get_x() + b.get_width() / 2, h + dy, fmt.format(h), ha="center", va="bottom", fontsize=8.5, color=C["gray_ink"])


# --- update cost -----------------------------------------------------------------------------------------------------------------------------
use_book_style(2.7)
fig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 2.7))
modes = ["copy-on-\nwrite", "merge-on-\nread"]
cols = [C["rose"], C["green"]]
fills = [C["rose_fill"], C["green_fill"]]
bars = a.bar(modes, [7.87, 2.85], color=fills, edgecolor=cols, linewidth=1.2)
labels(a, bars, "{:g} s", dy=0.15)
a.set_title("seconds per UPDATE", fontsize=9.5)
a.set_ylim(0, 9.5)
a.grid(axis="x", visible=False)
bars = b.bar(modes, [34_837_738, 4_005], color=fills, edgecolor=cols, linewidth=1.2)
b.set_yscale("log")
b.set_ylim(1e3, 2e8)
b.set_title("bytes written per UPDATE", fontsize=9.5)
b.text(0, 34_837_738 * 1.3, "34.8 MB", ha="center", fontsize=8.5, color=C["rose_ink"])
b.text(1, 4_005 * 1.5, "4 KB", ha="center", fontsize=8.5, color=C["green_ink"])
b.grid(axis="x", visible=False)
fig.tight_layout()
save(fig, "update-cost-cow-mor")

# --- merge scan bytes ---------------------------------------------------------------------------------------------------------------------------
use_book_style(2.6)
fig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 2.6))
modes = ["no partition\npredicate", "with partition\npredicate"]
bars = a.bar(modes, [200.7, 35.1], color=[C["rose_fill"], C["green_fill"]], edgecolor=[C["rose"], C["green"]], linewidth=1.2)
labels(a, bars, "{:g} MB", dy=4)
a.set_title("bytes the MERGE scan read", fontsize=9.5)
a.set_ylim(0, 235)
a.grid(axis="x", visible=False)
bars = b.bar(modes, [9.76, 8.18], color=[C["rose_fill"], C["green_fill"]], edgecolor=[C["rose"], C["green"]], linewidth=1.2)
labels(b, bars, "{:g} s", dy=0.15)
b.set_title("MERGE wall clock", fontsize=9.5)
b.set_ylim(0, 11.5)
b.grid(axis="x", visible=False)
fig.tight_layout()
save(fig, "merge-scan-bytes")

# --- small files / manifests ----------------------------------------------------------------------------------------------------------------------
use_book_style(2.7)
fig, axes = plt.subplots(1, 3, figsize=(6.3, 2.7))
steps = ["60\ncommits", "after\ncompaction", "after manifest\nrewrite"]
for ax, vals, title, fmt in ((axes[0], [60, 1, 1], "data files", "{:g}"), (axes[1], [60, 61, 1], "manifests", "{:g}"), (axes[2], [0.45, 0.12, 0.13], "full scan (s)", "{:g}")):
    bars = ax.bar(range(3), vals, color=[C["rose_fill"], C["blue_fill"], C["green_fill"]], edgecolor=[C["rose"], C["blue"], C["green"]], linewidth=1.1)
    labels(ax, bars, fmt, dy=max(vals) * 0.02)
    ax.set_xticks(range(3))
    ax.set_xticklabels(steps, fontsize=7.5)
    ax.set_title(title, fontsize=9.5)
    ax.set_ylim(0, max(vals) * 1.2)
    ax.grid(axis="x", visible=False)
fig.tight_layout()
save(fig, "stream-small-files")

# --- expire and orphans ---------------------------------------------------------------------------------------------------------------------------------
use_book_style(2.8)
fig, ax = plt.subplots()
x = ["12 snapshots,\n20 data files", "after\nexpire_snapshots", "a failed write\nleaves 5 MB", "after\nremove_orphan_files"]
vals = [386.1, 350.8, 355.8, 350.8]
colors = [C["rose"], C["green"], C["orange"], C["green"]]
fills = [C["rose_fill"], C["green_fill"], C["orange_fill"], C["green_fill"]]
bars = ax.bar(range(4), vals, color=fills, edgecolor=colors, linewidth=1.2)
labels(ax, bars, "{:g} MB", dy=1.0)
ax.set_xticks(range(4))
ax.set_xticklabels(x, fontsize=8)
ax.set_ylim(0, 500)
ax.set_ylabel("table directory (MB)")
ax.annotate("11 data files, 11 manifests,\n11 manifest lists deleted", xy=(1, 372), xytext=(1.5, 450), ha="center", fontsize=8.5, color=C["green_ink"],
            arrowprops=dict(arrowstyle="-", color=C["green_ink"], lw=0.8, shrinkB=1))
ax.grid(axis="x", visible=False)
fig.tight_layout()
save(fig, "expire-orphans")
