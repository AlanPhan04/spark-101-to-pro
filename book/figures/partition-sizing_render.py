#!/usr/bin/env python3
"""Render partition-sizing.pdf: an exact plot, not illustrative fake data.

For a fixed shuffle size S, size-per-task = S / (number of partitions). This
script plots that hyperbola for the chapter's 100 GB worked example and shades
the 128-200 MB target-task-size band, so the reader can see exactly where the
"good" partition count comes from instead of taking it on faith.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

matplotlib.rcParams["font.family"] = ["Arial", "DejaVu Sans"]
matplotlib.rcParams["pdf.fonttype"] = 42

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, os.pardir, "images", "partition-sizing.pdf")

SHUFFLE_GB = 100
SHUFFLE_MB = SHUFFLE_GB * 1024
TARGET_LOW, TARGET_HIGH = 128, 200          # MB per task, the target band
DEFAULT_PARTITIONS = 200                    # spark.sql.shuffle.partitions default

lo_partitions = SHUFFLE_MB / TARGET_HIGH    # fewer partitions -> bigger tasks
hi_partitions = SHUFFLE_MB / TARGET_LOW

x = np.linspace(20, 4000, 2000)
y = SHUFFLE_MB / x

fig, ax = plt.subplots(figsize=(6.6, 4.2))

ax.axvspan(20, lo_partitions, color="#f7dde0", alpha=0.7, lw=0, zorder=1,
           label="too few partitions -- each task spills")
ax.axvspan(hi_partitions, 4000, color="#fce7d2", alpha=0.7, lw=0, zorder=1,
           label="too many partitions -- scheduling overhead")
ax.axvspan(lo_partitions, hi_partitions, color="#d8ebcf", alpha=0.6, lw=0, zorder=1,
           label="target: 128-200 MB per task")

ax.plot(x, y, color="#3b6ea5", lw=2.4, zorder=3,
        label=f"{SHUFFLE_GB} GB shuffle: MB/task = {SHUFFLE_MB}/partitions")

default_y = SHUFFLE_MB / DEFAULT_PARTITIONS
ax.plot([DEFAULT_PARTITIONS], [default_y], marker="o", ms=8, color="#b5545e", zorder=4)
ax.annotate(f"default 200 partitions\n-> {default_y:.0f} MB/task (spills)",
            xy=(DEFAULT_PARTITIONS, default_y), xytext=(420, 900),
            fontsize=9, color="#7d2f38",
            arrowprops=dict(arrowstyle="->", color="#7d2f38", lw=1.2))

mid_partitions = (lo_partitions + hi_partitions) / 2
mid_y = SHUFFLE_MB / mid_partitions
ax.annotate(f"~{lo_partitions:.0f}-{hi_partitions:.0f} partitions\nfor this shuffle size",
            xy=(mid_partitions, mid_y), xytext=(1100, 260),
            fontsize=9, color="#2f5320",
            arrowprops=dict(arrowstyle="->", color="#2f5320", lw=1.2))

ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlim(20, 4000)
ax.set_ylim(20, 6000)
ax.set_xlabel("spark.sql.shuffle.partitions")
ax.set_ylabel("shuffle-read size per task (MB)")
ax.set_title(f"Sizing shuffle partitions for a {SHUFFLE_GB} GB shuffle", fontsize=12)
ax.grid(True, which="both", color="#dddddd", lw=0.6, zorder=0)
for spine in ("top", "right"):
    ax.spines[spine].set_visible(False)
ax.legend(loc="upper right", fontsize=8, framealpha=0.9)

fig.tight_layout()
os.makedirs(os.path.dirname(OUT), exist_ok=True)
fig.savefig(OUT, format="pdf")
plt.close(fig)
print("wrote", os.path.relpath(OUT, HERE))
