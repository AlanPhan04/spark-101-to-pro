#!/usr/bin/env python3
"""Editor's lint for the book's LaTeX chapters (book/chapters/*.tex).

    python <skill>/scripts/lint_chapter.py chapters/06-adaptive-query-execution.tex
    python <skill>/scripts/lint_chapter.py --all          # every chapter + appendix
    python <skill>/scripts/lint_chapter.py --status       # one-line depth table per chapter

Checks
  structure   figure: \\caption + \\label{fig:..} + image exists + \\Cref'd before it
              table:  caption + \\label{tab:..};  lstlisting: language= caption= label=lst:
              every \\Cref/\\cref target exists somewhere in the book
  density     prose stretches > MAX_WORDS_BETWEEN_VISUALS with no figure/table/listing
  prose       paragraphs > MAX_PARA_WORDS, filler words, "the figure below", "In this
              section we", back-to-back callouts, > 2 callouts per 1,000 words
  configs     a spark.* key in prose not wrapped in \\conf{}; a "default" next to a
              \\conf{} that disagrees with the Spark 3.5.x documented default
Exit 1 if any ERROR.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

MAX_WORDS_BETWEEN_VISUALS = 900
MAX_PARA_WORDS = 140
CALLOUTS_PER_1K = 2.0
TARGET_WORDS = (6000, 9000)    # ~20 pp per chapter at 380 pp / 19 chapters
TARGET_FIGS = 3
TARGET_LISTINGS = 4

FILLER = ["simply", "just", "easily", "obviously", "clearly", "basically", "very",
          "really", "of course", "in order to", "it is important to note",
          "note that", "leverage", "utilize", "delve", "seamless", "robust",
          "needless to say"]
JUST_OK = re.compile(r"\bjust (as|like|before|after|enough|once|because)\b", re.I)
PHRASES = {
    r"\bthe (figure|table|listing) (below|above)\b": "use \\Cref{...} — floats move",
    r"\bas (mentioned|shown|discussed) (above|below|earlier)\b": "use \\Cref{...}",
    r"\bin this (section|chapter),? we (will )?": "just start — no throat-clearing",
    r"\blet['’]s\b": "book voice: no \"let's\"",
}
CALLOUTS = ("note", "warning", "tip", "analogy")

# Spark 3.5.x documented defaults (verified against spark.apache.org/docs/3.5.x).
# value in bytes for sizes, plain number otherwise.
MB = 1024 ** 2
DEFAULTS = {
    "spark.sql.shuffle.partitions": 200,
    "spark.sql.autoBroadcastJoinThreshold": 10 * MB,
    "spark.sql.adaptive.advisoryPartitionSizeInBytes": 64 * MB,
    "spark.sql.adaptive.coalescePartitions.minPartitionSize": 1 * MB,
    "spark.sql.adaptive.skewJoin.skewedPartitionFactor": 5,
    "spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes": 256 * MB,
    "spark.sql.files.maxPartitionBytes": 128 * MB,
    "spark.sql.files.openCostInBytes": 4 * MB,
    "spark.memory.fraction": 0.6,
    "spark.memory.storageFraction": 0.5,
    "spark.executor.memoryOverheadFactor": 0.1,
    "spark.reducer.maxSizeInFlight": 48 * MB,
    "spark.shuffle.file.buffer": 32 * 1024,
    "spark.executor.heartbeatInterval": 10,       # seconds
    "spark.network.timeout": 120,                 # seconds
}
UNITS = {"b": 1, "kb": 1024, "k": 1024, "kib": 1024, "mb": MB, "m": MB, "mib": MB,
         "gb": 1024 ** 3, "g": 1024 ** 3, "gib": 1024 ** 3, "s": 1, "ms": 0.001}

issues: list[tuple[str, str, str]] = []
def err(w, m):  issues.append(("ERROR", w, m))
def warn(w, m): issues.append(("WARN", w, m))


def strip_tex(s: str) -> str:
    s = re.sub(r"(?<!\\)%.*", "", s)
    s = re.sub(r"\\(conf|texttt|nolinkurl)\{[^}]*\}", " X ", s)
    s = re.sub(r"\\(Cref|cref|label|ref|cite|includegraphics)(\[[^\]]*\])?\{[^}]*\}", " ", s)
    s = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?", " ", s)
    return re.sub(r"[{}$~\\]", " ", s)


def nwords(s: str) -> int:
    return len(re.findall(r"[A-Za-z][A-Za-z'’-]*", strip_tex(s)))


def all_labels(book: pathlib.Path) -> set[str]:
    labels = set()
    for tex in book.rglob("*.tex"):
        txt = tex.read_text(encoding="utf-8", errors="ignore")
        labels |= set(re.findall(r"\\label\{([^}]+)\}", txt))
        labels |= set(re.findall(r"\blabel=\{?([\w:.-]+)", txt))      # lstlisting [label=lst:..]
    return labels


def parse_size(num: str, unit: str | None) -> float:
    v = float(num.replace(",", ""))
    return v * UNITS.get((unit or "").lower(), 1)


def lint(path: pathlib.Path, book: pathlib.Path, labels: set[str], quiet=False) -> dict:
    src = path.read_text(encoding="utf-8")
    lines = src.splitlines()
    name = path.name
    stats = dict(words=0, figs=0, tables=0, listings=0, callouts=0)

    # cross-refs (whole file)
    for i, line in enumerate(lines, 1):
        for grp in re.findall(r"\\[Cc]ref\{([^}]+)\}", line):
            for t in grp.split(","):
                if t.strip() and t.strip() not in labels:
                    err(f"{name}:{i}", f"\\Cref target “{t.strip()}” is not defined anywhere")

    env = None            # current environment we're inside
    env_start, env_buf = 0, []
    refs_seen: set[str] = set()
    since_visual, visual_line = 0, 0
    para, para_start = [], 0
    last_block_end_was_callout, last_nonblank_after_callout = False, True

    def flush_para():
        nonlocal para
        if not para:
            return
        text = " ".join(para)
        n = nwords(text)
        stats["words"] += n
        if n > MAX_PARA_WORDS:
            warn(f"{name}:{para_start}", f"paragraph of {n} words (> {MAX_PARA_WORDS}) — split it or move structure into a figure/table")
        plain = re.sub(r"\\(conf|texttt)\{[^}]*\}", "", text)
        low = plain.lower()
        for f in FILLER:
            for m in re.finditer(rf"\b{re.escape(f)}\b", low):
                if f == "just" and JUST_OK.match(low, m.start()):
                    continue
                warn(f"{name}:{para_start}", f"filler word “{f}”")
        for pat, why in PHRASES.items():
            if re.search(pat, low):
                warn(f"{name}:{para_start}", f"“{re.search(pat, low).group(0)}” — {why}")
        # config keys outside \conf
        for m in re.finditer(r"(?<![{\w.])spark\.[a-z]+(\.[A-Za-z]+)+", re.sub(r"\\conf\{[^}]*\}|\\texttt\{[^}]*\}", "", text)):
            warn(f"{name}:{para_start}", f"config key {m.group(0)} in prose — wrap it in \\conf{{}}")
        for m in re.finditer(r"\\texttt\{(spark\.[a-z]+\.[A-Za-z.]+)\}", text):
            warn(f"{name}:{para_start}", f"\\texttt{{{m.group(1)}}} — use \\conf{{}} (breakable)")
        # stated defaults vs documented defaults
        num = r"([\d][\d,]*(?:\.\d+)?)\s*~?\s*(\\%|percent|KiB|MiB|GiB|KB|MB|GB|kb|mb|gb|k|m|g|ms|s)?(?![\w])"
        for m in re.finditer(r"\\conf\{([^}]+)\}(.{0,110})", text):
            key = m.group(1).replace("\\", "")
            tail = re.split(r"\.\s|;|\\conf\{", m.group(2))[0]       # stop at sentence end / next key
            if key not in DEFAULTS:
                continue
            nm = (re.search(r"default[^\d]{0,25}?" + num, tail, re.I)
                  or re.search(num + r"[^\d]{0,6}by default", tail, re.I))
            if not nm:
                continue
            unit = nm.group(2) or ""
            stated = (float(nm.group(1).replace(",", "")) / 100 if unit in ("\\%", "percent")
                      else parse_size(nm.group(1), unit))
            want = DEFAULTS[key]
            if abs(stated - want) > 1e-6 * max(1, want):
                pretty = f"{want / MB:g} MB" if want >= MB else f"{want:g}"
                err(f"{name}:{para_start}", f"\\conf{{{key}}}: text says default “{nm.group(0).strip()}”, Spark 3.5 documents {pretty}")
        para = []

    for i, raw in enumerate(lines, 1):
        line = re.sub(r"(?<!\\)%.*", "", raw)
        for grp in re.findall(r"\\[Cc]ref\{([^}]+)\}", line):
            refs_seen |= {t.strip() for t in grp.split(",")}

        b = re.match(r"\s*\\begin\{(figure|table|lstlisting|chapterintro|" + "|".join(CALLOUTS) + r"|itemize|enumerate|description|exercises)\}(\[[^\]]*\])?", line)
        if b and env is None:
            flush_para()
            env, env_start, env_buf = b.group(1), i, [line]
            if env in CALLOUTS:
                stats["callouts"] += 1
                if last_block_end_was_callout and not last_nonblank_after_callout:
                    warn(f"{name}:{i}", "two callouts back to back — merge or move one")
            if env == "lstlisting":
                opts = b.group(2) or ""
                if "language=" not in opts:
                    warn(f"{name}:{i}", "lstlisting without language= (sql / scala / text)")
                if "caption=" not in opts:
                    warn(f"{name}:{i}", "lstlisting without caption=")
                if "label=lst:" not in opts:
                    warn(f"{name}:{i}", "lstlisting without label=lst:…")
            if line.strip().endswith("\\end{" + env + "}"):
                pass
            else:
                continue
        if env is not None:
            env_buf.append(line)
            if re.search(r"\\end\{" + re.escape(env) + r"\}", line):
                body = "\n".join(env_buf)
                where = f"{name}:{env_start}"
                if env == "figure":
                    stats["figs"] += 1
                    lab = re.search(r"\\label\{(fig:[^}]+)\}", body)
                    if "\\caption" not in body:
                        err(where, "figure without \\caption")
                    if not lab:
                        err(where, "figure without \\label{fig:…}")
                    elif lab.group(1) not in refs_seen:
                        warn(where, f"{lab.group(1)} is not \\Cref'd in the prose before the figure appears")
                    for img in re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", body):
                        p = book / "images" / img
                        if not p.exists() and not p.with_suffix(".pdf").exists():
                            err(where, f"image not found: images/{img}")
                    cap = re.search(r"\\caption\{(.*)", body, re.S)
                    if cap and nwords(cap.group(1)) < 8:
                        warn(where, "caption is a label, not a takeaway — say what the reader should see")
                elif env == "table":
                    stats["tables"] += 1
                    if "\\caption" not in body:
                        (warn if "appendices" in str(path) else err)(where, "table without \\caption")
                    if not re.search(r"\\label\{tab:", body):
                        warn(where, "table without \\label{tab:…} (can't be cross-referenced)")
                elif env == "lstlisting":
                    stats["listings"] += 1
                elif env in CALLOUTS or env in ("itemize", "enumerate", "description", "exercises", "chapterintro"):
                    stats["words"] += nwords(body)
                    since_visual += nwords(body)
                if env in ("figure", "table", "lstlisting"):
                    since_visual, visual_line = 0, i
                last_block_end_was_callout = env in CALLOUTS
                last_nonblank_after_callout = False
                env = None
            continue

        if re.match(r"\s*\\(chapter|section|subsection)\*?\{", line):
            flush_para()
            continue
        if not line.strip():
            flush_para()
            continue
        if last_block_end_was_callout:
            last_nonblank_after_callout = True
        if not para:
            para_start = i
        para.append(line.strip())
        since_visual += nwords(line)
        if since_visual > MAX_WORDS_BETWEEN_VISUALS:
            warn(f"{name}:{visual_line}-{i}", f"{since_visual}+ words with no figure, table, or listing — which mechanism here would a picture show faster?")
            since_visual = 0
    flush_para()

    w = stats["words"]
    if w and stats["callouts"] / (w / 1000) > CALLOUTS_PER_1K:
        warn(name, f"{stats['callouts']} callouts in ~{w} words — more than {CALLOUTS_PER_1K:g} per 1,000 dilutes them")
    return stats


def main() -> int:
    try:  # Windows consoles default to cp1252; keep emoji/quotes from crashing
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*", type=pathlib.Path)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--status", action="store_true", help="print the depth table only")
    ap.add_argument("--sections", nargs="?", const=20, type=int, metavar="N",
                    help="list the N thinnest \\section{}s across all chapters (prose words, listings excluded)")
    ap.add_argument("--book", type=pathlib.Path)
    a = ap.parse_args()
    book = a.book or next((p for p in [pathlib.Path("."), pathlib.Path("book")] if (p / "main.tex").exists()), None)
    if book is None:
        print("run from the repo root or book/, or pass --book")
        return 2
    if a.sections:
        rows = []
        for f in sorted((book / "chapters").glob("*.tex")):
            t = f.read_text(encoding="utf-8")
            for part in re.split(r"\\section\{", t)[1:]:
                title = re.sub(r"\\texttt\{([^}]*)\}?", r"\1", part.split("\n")[0]).rstrip("}")
                body = re.sub(r"\\begin\{lstlisting\}.*?\\end\{lstlisting\}", "", part, flags=re.S)
                rows.append((nwords(body), f.name[:2], title))
        print(f"{'words':>5}  ch  section")
        for w, c, t in sorted(rows)[: a.sections]:
            if t.lower().startswith("summary"):
                continue
            print(f"{w:5d}  {c}  {t}")
        return 0
    files = a.files
    if a.all or a.status or not files:
        files = sorted((book / "chapters").glob("*.tex")) + ([] if a.status else sorted((book / "appendices").glob("*.tex")))
    labels = all_labels(book)
    rows = [(f.name, lint(f, book, labels)) for f in files]

    if a.status or len(rows) > 1:
        lo, hi = TARGET_WORDS
        print(f"{'chapter':45s} {'words':>6} {'figs':>4} {'tabs':>4} {'lst':>4} {'callo':>5}  depth")
        for n, s in rows:
            depth = "▓" * min(10, round(10 * s["words"] / hi)) + "░" * max(0, 10 - round(10 * s["words"] / hi))
            flags = []
            if s["words"] < lo: flags.append(f"thin (<{lo})")
            if s["figs"] < TARGET_FIGS: flags.append(f"figs<{TARGET_FIGS}")
            if s["listings"] < TARGET_LISTINGS: flags.append(f"listings<{TARGET_LISTINGS}")
            print(f"{n:45s} {s['words']:6d} {s['figs']:4d} {s['tables']:4d} {s['listings']:4d} {s['callouts']:5d}  {depth} {' · '.join(flags)}")
        if a.status:
            return 0
        print()
    if not issues:
        print("✅ no issues")
        return 0
    for level, where, msg in issues:
        print(f"{'❌' if level == 'ERROR' else '⚠️ '} {level:5} {where}: {msg}")
    n = sum(1 for l, *_ in issues if l == "ERROR")
    print(f"— {n} errors, {len(issues) - n} warnings")
    return 1 if n else 0


if __name__ == "__main__":
    sys.exit(main())
