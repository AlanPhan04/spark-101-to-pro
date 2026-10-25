"""Chapter 5: the four join strategies on the lab data, forced with hints. Seconds, plan operator, shuffle bytes (from the event log by job group)."""
import json
import re
import statistics
import time

from labutil import OUT, plan_text, session

spark = session("joins")
spark.conf.set("spark.sql.adaptive.enabled", "false")
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")      # hints decide, not sizes
spark.conf.set("spark.sql.shuffle.partitions", "40")
res = []


def go(label, build, hint, sql, reps=2):
    ts = []
    for i in range(reps):
        group = f"j_{label}_{hint}".replace(" ", "_")
        spark.sparkContext.setJobGroup(group, group)
        df = spark.sql(sql)
        t = time.time()
        try:
            df.collect()
        except Exception as e:
            res.append({"build": label, "hint": hint, "error": str(e).strip().splitlines()[0][:140]})
            print(res[-1]); return
        ts.append(time.time() - t)
    plan = plan_text(df, "simple")
    op = re.findall(r"(BroadcastHashJoin|ShuffledHashJoin|SortMergeJoin|BroadcastNestedLoopJoin|CartesianProduct)", plan)
    res.append({"build": label, "hint": hint, "operator": op[0] if op else "?", "seconds": round(statistics.median(ts), 2), "group": group,
                "exchanges": len(re.findall(r"Exchange", plan))})
    print(res[-1])


S = "SELECT /*+ {h}({t}) */ count(*), sum(o.order_total) FROM orders o JOIN {t} {a} ON {on}"
cases = [
    ("dim_date (365 rows)", "dim_date", "d", "date(o.order_ts) = d.date"),
    ("dim_customer (2M rows)", "dim_customer", "c", "o.customer_id = c.customer_id"),
    ("dim_product (2M rows, 170 MB)", "dim_product", "p", "o.product_id = p.product_id"),
]
for label, t, a, on in cases:
    for h in ("BROADCAST", "SHUFFLE_HASH", "MERGE"):
        go(label, t, h, S.format(h=h, t=t, a=a, on=on))
# non-equi join: only broadcast nested loop or cartesian can run it
go("dim_date non-equi (365 rows)", "dim_date", "BROADCAST", "SELECT /*+ BROADCAST(d) */ count(*) FROM (SELECT * FROM orders LIMIT 200000) o JOIN dim_date d ON date(o.order_ts) >= d.date AND date(o.order_ts) < date_add(d.date, 1)")
go("dim_date non-equi (365 rows)", "dim_date", "MERGE", "SELECT /*+ MERGE(d) */ count(*) FROM (SELECT * FROM orders LIMIT 200000) o JOIN dim_date d ON date(o.order_ts) >= d.date AND date(o.order_ts) < date_add(d.date, 1)")
json.dump(res, open(f"{OUT}/joins_results.json", "w"), indent=1)
print("DONE")
