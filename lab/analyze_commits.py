"""Histogram of commit attempts per retry setting from exp_commits.log (Iceberg CommitReport lines)."""
import collections
import re
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "out/exp_commits.log"
setting = None
hist = collections.defaultdict(collections.Counter)
durations = collections.defaultdict(list)
failures = collections.Counter()
for line in open(path, encoding="utf-8", errors="replace"):
    m = re.match(r"### setting retries=(\d+)", line)
    if m:
        setting = m.group(1)
        continue
    if setting is None:
        continue
    if "CommitReport" in line and "operation=append" in line and "t_race" in line:
        a = re.search(r"attempts=CounterResult\{unit=COUNT, value=(\d+)\}", line)
        d = re.search(r"totalDuration=TimerResult\{timeUnit=NANOSECONDS, totalDuration=PT([\d.]+)S", line)
        if a:
            hist[setting][int(a.group(1))] += 1
        if d:
            durations[(setting, int(a.group(1)))].append(float(d.group(1)))
    if "CommitFailedException" in line or "Cannot commit" in line:
        failures[re.sub(r"\d{6,}", "N", line.strip())[:140]] += 1
for s in hist:
    print("retries", s, "attempts histogram", dict(sorted(hist[s].items())))
for k in sorted(durations):
    v = durations[k]
    print("retries", k[0], "attempts", k[1], "n", len(v), "mean commit s", round(sum(v) / len(v), 2))
for f, n in failures.most_common(3):
    print(n, f)
