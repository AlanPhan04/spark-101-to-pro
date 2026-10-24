"""House style for the book's quantitative figures (matplotlib).

Copy next to the renderer (book/figures/bookplot.py) and use it from a
<slug>_render.py that plots an exact formula or measured data — never
illustrative fake numbers (partition-sizing_render.py is the model).

    from bookplot import use_book_style, C, save
    use_book_style()
    fig, ax = plt.subplots()
    ax.plot(x, y, color=C["blue"])
    ax.axvspan(lo, hi, color=C["green_fill"])
    save(fig, "partition-sizing")          # -> ../images/partition-sizing.pdf

Sizes are set so the PDF prints at the same scale as the body text when
included at width=\\linewidth on the book's 16 cm text block: a 6.3 in wide
figure is placed 1:1, so 9–10 pt here is 9–10 pt on paper.
"""
from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# The book palette (same triples as the .drawio figures).
C = {
    "blue": "#3b6ea5", "blue_fill": "#cfe0f4", "blue_ink": "#1f3d5c",
    "green": "#4f8a3d", "green_fill": "#d8ebcf", "green_ink": "#2f5320",
    "rose": "#b5545e", "rose_fill": "#f7dde0", "rose_ink": "#7d2f38",
    "orange": "#c77f3b", "orange_fill": "#fce7d2", "orange_ink": "#7a4a17",
    "purple": "#6a5a8a", "purple_fill": "#ece6f4", "purple_ink": "#3f335c",
    "gray": "#6b7280", "gray_fill": "#eceef1", "gray_ink": "#374151",
    "amber": "#c9a227", "amber_fill": "#fbeecf",
    "grid": "#dddddd", "annot": "#57503f",
}
CYCLE = [C["blue"], C["green"], C["orange"], C["purple"], C["rose"], C["gray"]]

TEXTWIDTH_IN = 16 / 2.54          # 6.30 in


def use_book_style(height_in: float = 3.6):
    matplotlib.rcParams.update({
        "figure.figsize": (TEXTWIDTH_IN, height_in),
        "font.family": ["Arial", "Liberation Sans", "DejaVu Sans"],
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "axes.labelsize": 10,
        "axes.labelcolor": C["gray_ink"],
        "axes.edgecolor": "#9aa0a6",
        "axes.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.color": C["grid"],
        "grid.linewidth": 0.6,
        "axes.prop_cycle": matplotlib.cycler(color=CYCLE),
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "xtick.color": C["gray_ink"],
        "ytick.color": C["gray_ink"],
        "legend.fontsize": 9,
        "legend.frameon": False,
        "lines.linewidth": 2.4,
        "pdf.fonttype": 42,           # embed TrueType, like _drawio.py
    })


def annotate(ax, text, xy, xytext, color=None):
    """Arrowed annotation in the book's style (use the role's *_ink color)."""
    color = color or C["annot"]
    ax.annotate(text, xy=xy, xytext=xytext, fontsize=9, color=color,
                arrowprops=dict(arrowstyle="->", color=color, lw=1.1))


def save(fig, slug: str):
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, os.pardir, "images", f"{slug}.pdf")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    fig.savefig(out, format="pdf", bbox_inches="tight", pad_inches=0.05,
                metadata={"CreationDate": None})
    plt.close(fig)
    print("wrote", os.path.relpath(out, here))
