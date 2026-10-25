"""Find overlapping words and text spilling out of its box in every figure PDF."""
import glob
import os
import sys

import pymupdf

root = os.path.join(os.path.dirname(__file__), "..", "book", "images")
bad = 0
for f in sorted(glob.glob(os.path.join(root, "*.pdf"))):
    d = pymupdf.open(f)
    p = d[0]
    words = p.get_text("words")
    issues = []
    for a in range(len(words)):
        for b in range(a + 1, len(words)):
            x, y = words[a], words[b]
            ox = min(x[2], y[2]) - max(x[0], y[0])
            oy = min(x[3], y[3]) - max(x[1], y[1])
            if ox > 1.5 and oy > 2.5:
                issues.append(f"overlap '{x[4]}' x '{y[4]}'")
    rects = []
    for dr in p.get_drawings():
        r = dr["rect"]
        if dr.get("fill") is not None and r.width > 12 and r.height > 8 and r.width < p.rect.width * 0.98:
            rects.append(r)
    lines = {}
    for w in words:
        lines.setdefault((w[5], w[6]), []).append(w)
    for k, ws in lines.items():
        x0 = min(w[0] for w in ws); x1 = max(w[2] for w in ws)
        y0 = min(w[1] for w in ws); y1 = max(w[3] for w in ws)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        cont = [r for r in rects if r.x0 <= cx <= r.x1 and r.y0 <= cy <= r.y1]
        if not cont:
            continue
        r = min(cont, key=lambda r: r.width * r.height)
        if x0 < r.x0 - 1.5 or x1 > r.x1 + 1.5:
            txt = " ".join(w[4] for w in ws)[:50]
            issues.append(f"spill '{txt}' by {max(r.x0 - x0, x1 - r.x1):.1f}pt")
    if issues:
        bad += 1
        print(os.path.basename(f), len(issues), "; ".join(issues[:5]))
print("figures with issues:", bad, "of", len(glob.glob(os.path.join(root, "*.pdf"))))
