#!/usr/bin/env python3
"""Lint the book's draw.io figures the way a print production editor would.

For every book/figures/<slug>.drawio:
  palette      every fill/stroke/font color comes from the book palette
  print size   each label's size *as printed* (after LaTeX scales the PDF to the
               width used in \\includegraphics) is >= MIN_PRINT_PT
  overflow     each label's estimated width fits inside its box
  wiring       every edge's source/target id exists; renderer + PDF exist and
               the PDF is newer than the .drawio
  usage        the figure is \\includegraphics'd somewhere in chapters/appendices

Usage (from the repo's book/ folder, or pass --book):
    python <skill>/scripts/check_figures.py               # all figures
    python <skill>/scripts/check_figures.py job-stage-task shuffle-write-read-path
Exit 1 if any ERROR.
"""
from __future__ import annotations

import argparse
import html
import pathlib
import re
import sys
import logging
import warnings
import xml.etree.ElementTree as ET

logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
warnings.filterwarnings("ignore", message="Glyph")

# ── must mirror book/figures/_drawio.py ─────────────────────────────────────
FONT_SCALE = 1.18
LABEL_FACTOR = 0.82          # _draw_label: fontsize = size * 0.82 * FONT_SCALE
CANVAS_DPI = 66.0
EDGE_LABEL_PT = 10           # edge labels are drawn at a fixed 10 pt
# ── print geometry (main.tex: a4paper, left=3cm, right=2cm) ────────────────
TEXTWIDTH_PT = (21.0 - 3.0 - 2.0) / 2.54 * 72.0     # 16 cm ≈ 453.5 pt
MIN_PRINT_PT = 7.0           # body text is 13 pt; < 7 pt reads as fine print
WARN_PRINT_PT = 8.0

PALETTE = {  # see references/visual-system.md §2 — the only legal colors
    # blue: driver / planning / primary flow
    "#3b6ea5", "#cfe0f4", "#eaf1fb", "#e7f0fb", "#1f3d5c",
    # green: executors / task work / success / the fixed state
    "#4f8a3d", "#d8ebcf", "#e4f1dc", "#eaf4e3", "#2f5320",
    # rose: cost / problem — shuffle, spill, skew, OOM, rejected
    "#b5545e", "#f7dde0", "#fdeef0", "#7d2f38",
    "#c99aa0",                      # muted rose: many-to-many shuffle edges only
    # orange: alternate path / Iceberg-side / secondary actor
    "#c77f3b", "#fce7d2", "#7a4a17",
    # purple: cluster manager / infrastructure envelope / broadcast
    "#6a5a8a", "#ece6f4", "#3f335c",
    # gray: client, neutral inputs, unchanged
    "#6b7280", "#eceef1", "#374151", "#555555", "#888888",
    "#2f3b52",                      # ink: heavy frame / figure title
    "#57503f",                      # warm ink: free-text annotations under a figure
    # amber: attention / timeout — rare
    "#c9a227", "#fbeecf", "#7a5c0a",
    # neutrals
    "#ffffff", "#000000", "#1a1a1a", "#333333", "none",
}

issues: list[tuple[str, str, str]] = []
def err(fig, msg):  issues.append(("ERROR", fig, msg))
def warn(fig, msg): issues.append(("WARN", fig, msg))


def style(s: str | None) -> dict:
    d = {}
    for part in (s or "").split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            d[k] = v
        elif part:
            d[part] = "1"
    return d


def label_lines(value: str | None, base: int) -> list[tuple[str, int, bool]]:
    """Mirror of _drawio._label_lines (span font-size persists until </span>)."""
    if not value:
        return []
    value = value.replace("&#10;", "<br>").replace("\\n", "<br>")
    out, cur = [], base
    for chunk in re.split(r"<br\s*/?>", value):
        bold = "<b>" in chunk or "<b " in chunk
        m = re.search(r"font-size:\s*(\d+)px", chunk)
        if m:
            cur = int(m.group(1))
        text = html.unescape(re.sub(r"<[^>]+>", "", chunk)).strip()
        out.append((text, cur, bold))
        if "</span>" in chunk:
            cur = base
    return out


_t2p = None
def text_width_pt(text: str, size_pt: float, bold: bool) -> float:
    global _t2p
    try:
        from matplotlib.font_manager import FontProperties
        from matplotlib.textpath import TextToPath
        if _t2p is None:
            _t2p = TextToPath()
        fp = FontProperties(family=["Arial", "Liberation Sans", "DejaVu Sans"], size=size_pt,
                            weight="bold" if bold else "normal")
        w, _, _ = _t2p.get_text_width_height_descent(text.replace("\n", " "), fp, ismath=False)
        return w
    except Exception:            # matplotlib missing: crude average-glyph estimate
        return len(text) * size_pt * (0.58 if bold else 0.52)


def pdf_width_pt(pdf: pathlib.Path) -> float | None:
    m = re.search(rb"/MediaBox\s*\[\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", pdf.read_bytes())
    return float(m.group(3)) - float(m.group(1)) if m else None


def include_widths(book: pathlib.Path) -> dict[str, list[tuple[float, str]]]:
    """slug -> [(fraction of \\linewidth, where)] from every \\includegraphics."""
    out: dict[str, list[tuple[float, str]]] = {}
    pat = re.compile(r"\\includegraphics\[([^\]]*)\]\{([^}]+)\}")
    for tex in sorted(list((book / "chapters").glob("*.tex")) + list((book / "appendices").glob("*.tex"))):
        for i, line in enumerate(tex.read_text(encoding="utf-8").splitlines(), 1):
            for opts, name in pat.findall(line):
                slug = pathlib.Path(name).stem
                m = re.search(r"width\s*=\s*([\d.]*)\s*\\(?:line|text)width", opts)
                frac = float(m.group(1) or 1) if m else 1.0
                out.setdefault(slug, []).append((frac, f"{tex.name}:{i}"))
    return out


def check(book: pathlib.Path, src: pathlib.Path, widths: dict):
    slug = src.stem
    figs, imgs = book / "figures", book / "images"
    try:
        model = ET.parse(src).getroot().find("diagram").find("mxGraphModel")
    except Exception as e:
        err(slug, f"cannot parse .drawio: {e}")
        return
    cells = model.find("root").findall("mxCell")
    ids = {c.get("id") for c in cells}

    pdf = imgs / f"{slug}.pdf"
    renderer = figs / f"{slug}_render.py"
    if not renderer.exists():
        err(slug, f"no renderer {renderer.name}")
    if not pdf.exists():
        err(slug, "images/%s.pdf missing — run the renderer" % slug)
    elif pdf.stat().st_mtime < src.stat().st_mtime:
        warn(slug, "PDF is older than the .drawio — re-render")

    uses = widths.get(slug, [])
    if not uses:
        warn(slug, "not \\includegraphics'd in any chapter or appendix")
    frac = max((f for f, _ in uses), default=1.0)
    pw = pdf_width_pt(pdf) if pdf.exists() else None
    scale = (TEXTWIDTH_PT * frac / pw) if pw else None   # PDF pt -> printed pt

    smallest = (99.0, "")
    for c in cells:
        st = style(c.get("style"))
        where = f"{slug} [{c.get('id')}]"
        for key in ("fillColor", "strokeColor", "fontColor"):
            v = st.get(key)
            if v and v.lower() not in PALETTE:
                err(where, f"{key}={v} is off-palette")
        if c.get("edge") == "1":
            for end in ("source", "target"):
                if c.get(end) and c.get(end) not in ids:
                    err(where, f"edge {end}='{c.get(end)}' does not exist")
            if c.get("value") and scale:
                p = EDGE_LABEL_PT * scale
                if p < MIN_PRINT_PT:
                    err(where, f"edge label prints at {p:.1f} pt (< {MIN_PRINT_PT})")
            continue
        if c.get("vertex") != "1":
            continue
        g = c.find("mxGeometry")
        if g is None:
            continue
        box_w = float(g.get("width", 0))
        base = int(st.get("fontSize", 12))
        pad = float(st.get("spacingLeft", 12)) + 6 if st.get("align") == "left" else 10
        for text, size, bold in label_lines(c.get("value"), base):
            if not text:
                continue
            pt = size * LABEL_FACTOR * FONT_SCALE                 # matplotlib pt in the PDF
            if scale:
                printed = pt * scale
                if printed < smallest[0]:
                    smallest = (printed, text[:30])
                if printed < MIN_PRINT_PT:
                    err(where, f"“{text[:40]}” prints at {printed:.1f} pt (< {MIN_PRINT_PT})")
                elif printed < WARN_PRINT_PT:
                    warn(where, f"“{text[:40]}” prints at {printed:.1f} pt — borderline")
            if "text" in st and st.get("fillColor", "none").lower() in ("none", ""):
                continue                                          # free text: no box to overflow
            text_px = text_width_pt(text, pt, bold) / 72.0 * CANVAS_DPI
            if box_w and text_px > box_w - pad:
                err(where, f"label overflows its box: “{text[:40]}” ≈{text_px:.0f}px in a {box_w:.0f}px box")
    if scale:
        print(f"  {slug:28s} printed at {frac:.2f}\\linewidth · smallest text {smallest[0]:.1f} pt")


def main() -> int:
    try:  # Windows consoles default to cp1252; keep emoji/quotes from crashing
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--book", type=pathlib.Path, default=None, help="path to the book/ folder")
    ap.add_argument("-v", "--verbose", action="store_true", help="list every issue (default: grouped per figure)")
    a = ap.parse_args()
    book = a.book or next((p for p in [pathlib.Path("."), pathlib.Path("book")] if (p / "main.tex").exists()), None)
    if book is None:
        print("run from the repo root or book/, or pass --book")
        return 2
    widths = include_widths(book)
    srcs = sorted((book / "figures").glob("*.drawio"))
    if a.slugs:
        srcs = [s for s in srcs if s.stem in a.slugs]
    print(f"Checking {len(srcs)} figure(s) — min printed size {MIN_PRINT_PT} pt, text width {TEXTWIDTH_PT:.0f} pt")
    for s in srcs:
        check(book, s, widths)
    for slug in sorted(set(widths) - {s.stem for s in (book / 'figures').glob('*.drawio')}):
        if not (book / "figures" / f"{slug}_render.py").exists():
            warn(slug, "included in the book but has no .drawio or renderer (plot-only figures are fine if a *_render.py exists)")
    if not issues:
        print("✅ no issues")
        return 0
    if a.verbose:
        for level, where, msg in issues:
            print(f"{'❌' if level == 'ERROR' else '⚠️ '} {level:5} {where}: {msg}")
    else:
        groups: dict[str, list] = {}
        for level, where, msg in issues:
            groups.setdefault(where.split(" [")[0], []).append((level, where, msg))
        for fig, its in groups.items():
            kinds: dict[str, int] = {}
            for _, _, msg in its:
                k = ("tiny text" if "prints at" in msg else "overflow" if "overflows" in msg
                     else "off-palette" if "off-palette" in msg else msg[:50])
                kinds[k] = kinds.get(k, 0) + 1
            worst = next((w for l, w, m in its if l == "ERROR"), its[0][1])
            print(f"{'❌' if any(l == 'ERROR' for l, *_ in its) else '⚠️ '} {fig:28s} " +
                  ", ".join(f"{v}× {k}" for k, v in kinds.items()))
        print("   (re-run with -v for every label)")
    n = sum(1 for l, *_ in issues if l == "ERROR")
    print(f"— {n} errors, {len(issues) - n} warnings")
    return 1 if n else 0


if __name__ == "__main__":
    sys.exit(main())
