#!/usr/bin/env python3
"""commit-throughput.pdf: cumulative committed snapshots over time for 12 writers racing for one table (lab, measured).

Each step is one snapshot; every snapshot's parent is the previous one, so commits form one line no matter how many
writers there are. Data: figures/data/commit_times_r4.csv and commit_times_r0.csv (lab/out/k_snapshots_*.txt).
"""
import csv
import os

import matplotlib.pyplot as plt

from bookplot import C, save, use_book_style

HERE = os.path.dirname(os.path.abspath(__file__))


def load(name):
    with open(os.path.join(HERE, "data", name), newline="") as f:
        return [float(r["seconds"]) for r in csv.DictReader(f)]


r4 = load("commit_times_r4.csv")
r0 = load("commit_times_r0.csv")
use_book_style(3.0)
fig, ax = plt.subplots()
ax.step(r4, range(1, len(r4) + 1), where="post", color=C["blue"], label=f"retries = 4: {len(r4)} commits in {r4[-1]:.0f} s")
ax.step(r0, range(1, len(r0) + 1), where="post", color=C["rose"], label=f"retries = 0: {len(r0)} commits in {r0[-1]:.0f} s")
ax.set_xlabel("seconds since the first commit")
ax.set_ylabel("snapshots committed")
ax.legend(loc="upper left")
ax.annotate("12 writers, one pointer:\ncommits land one at a time", xy=(r4[len(r4) // 2], len(r4) // 2), xytext=(r4[-1] * 0.45, 8),
            fontsize=9, color=C["gray_ink"], arrowprops=dict(arrowstyle="->", color=C["gray_ink"], lw=1.1))
fig.tight_layout()
save(fig, "commit-throughput")
