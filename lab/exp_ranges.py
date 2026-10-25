"""Per-file min/max of customer_id for an unsorted and a sorted copy: the data behind the file-stat-ranges figure."""
import csv

from labutil import OUT, session

spark = session("exp-ranges")
for t in ("t_plain", "t_sorted"):
    rows = spark.sql(f"SELECT readable_metrics.customer_id.lower_bound AS lo, readable_metrics.customer_id.upper_bound AS hi FROM lab.db.{t}.files").collect()
    data = sorted((int(r.lo[1:]), int(r.hi[1:])) for r in rows)
    with open(f"{OUT}/ranges_{t}.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["lo", "hi"]); w.writerows(data)
    print(t, len(data), data[:3])
print("DONE")
