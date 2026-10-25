#!/usr/bin/env python3
"""delete-bytes-written.pdf: bytes written to delete ONE row of a 969,000-row day, copy-on-write vs merge-on-read.

Lab (lab/exp_iceberg_spec.py): the COW DELETE rewrote one 34.78 MB data file (snapshot summary added-files-size
34,781,105); the MoR DELETE wrote one 1,492-byte position delete file.
"""
import matplotlib.pyplot as plt

from bookplot import C, save, use_book_style

LABELS = ["copy-on-write (default)", "merge-on-read"]
BYTES = [34_781_105, 1_492]

use_book_style(2.4)
fig, ax = plt.subplots()
ax.barh([0, 1], BYTES, color=[C["rose_fill"], C["green_fill"]], edgecolor=[C["rose"], C["green"]], linewidth=1.2, height=0.55)
ax.set_xscale("log")
ax.set_xlim(500, 2e8)
ax.set_yticks([0, 1])
ax.set_yticklabels(LABELS)
ax.invert_yaxis()
ax.text(BYTES[0] * 1.15, 0, "34.8 MB: the whole data file rewritten", va="center", fontsize=9, color=C["rose_ink"])
ax.text(BYTES[1] * 1.6, 1, "1.5 KB: one position delete file", va="center", fontsize=9, color=C["green_ink"])
ax.set_xlabel("bytes written to delete one row (log scale)")
ax.grid(axis="y", visible=False)
fig.tight_layout()
save(fig, "delete-bytes-written")
