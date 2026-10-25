#!/usr/bin/env python3
"""commit-attempts.pdf: 12 concurrent writers x 4 appends each (48 commits) racing for one table, lab-measured.

Left: the default five attempts (commit.retry.num-retries = 4): how many attempts each successful commit needed.
Right: commit.retry.num-retries = 0, where a lost race is a failed commit. Data: lab/exp_commits.py and
lab/analyze_commits.py (Iceberg CommitReport 'attempts' counter).
"""
import matplotlib.pyplot as plt

from bookplot import C, save, use_book_style

use_book_style(3.0)
fig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 3.0), gridspec_kw={"width_ratios": [1.15, 1]})

# retries = 4
labels = ["1 attempt", "2 attempts", "4 attempts", "failed"]
vals = [12, 34, 1, 1]
cols = [C["green"], C["orange"], C["rose"], C["gray"]]
fills = [C["green_fill"], C["orange_fill"], C["rose_fill"], C["gray_fill"]]
a.bar(range(4), vals, color=fills, edgecolor=cols, linewidth=1.2)
for i, v in enumerate(vals):
    a.text(i, v + 0.8, str(v), ha="center", fontsize=9, color=C["gray_ink"])
a.set_xticks(range(4))
a.set_xticklabels(labels, rotation=20, ha="right", fontsize=8.5)
a.set_ylabel("commits (of 48)")
a.set_title("retries = 4 (default)", fontsize=10)
a.set_ylim(0, 42)
a.grid(axis="x", visible=False)

# retries = 0
b.bar(range(2), [41, 7], color=[C["green_fill"], C["gray_fill"]], edgecolor=[C["green"], C["gray"]], linewidth=1.2)
for i, v in enumerate([41, 7]):
    b.text(i, v + 0.8, str(v), ha="center", fontsize=9, color=C["gray_ink"])
b.set_xticks(range(2))
b.set_xticklabels(["1 attempt", "failed"], fontsize=8.5)
b.set_title("retries = 0", fontsize=10)
b.set_ylim(0, 48)
b.grid(axis="x", visible=False)
fig.tight_layout()
save(fig, "commit-attempts")
