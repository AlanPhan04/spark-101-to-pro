"""Chapter 19, follow-up: partition-boundary alignment of pushed predicates, and the failure message of an aborted write."""
import json
import os
import re

from labutil import OUT, scan_metrics, session

spark = session("dsv2b")
spark.conf.set("spark.sql.adaptive.enabled", "false")
T = "TIMESTAMP"
preds = [
    ("one whole day (aligned)", f"order_ts >= {T} '2026-03-05 00:00:00' AND order_ts < {T} '2026-03-06 00:00:00'"),
    ("one hour inside a day", f"order_ts >= {T} '2026-03-05 10:00:00' AND order_ts < {T} '2026-03-05 11:00:00'"),
    ("date(order_ts) = day", "date(order_ts) = DATE '2026-03-05'"),
    ("partition OR data column", f"order_ts >= {T} '2026-03-05 00:00:00' AND order_ts < {T} '2026-03-06 00:00:00' OR product_id = 'p0000042'"),
    ("partition AND data column", f"order_ts >= {T} '2026-03-05 00:00:00' AND order_ts < {T} '2026-03-06 00:00:00' AND order_total > 200"),
]
rows = []
for name, p in preds:
    df = spark.sql(f"SELECT sum(order_total) FROM orders WHERE {p}")
    df.collect()
    plan = df._jdf.queryExecution().executedPlan().toString()
    scan = [l for l in plan.splitlines() if "BatchScan" in l][0].strip()
    has_filter = any(re.search(r"^\s*[+:\- ]*\*?\(?\d*\)?\s*Filter\b", l) for l in plan.splitlines())
    m = list(scan_metrics(df).values())[0]
    rows.append({"predicate": name, "filter_above_scan": has_filter, "rows_out_of_scan": m.get("numOutputRows"), "scan_line": scan[:260]})
    print(name, "| Filter above:", has_filter, "| scan rows:", m.get("numOutputRows"))
json.dump(rows, open(f"{OUT}/dsv2b_results.json", "w"), indent=1)

# the aborted write, with the real cause
spark.sql("DROP TABLE IF EXISTS t_fail PURGE")
spark.sql(f"CREATE TABLE t_fail USING iceberg AS SELECT * FROM orders WHERE order_ts < {T} '2026-03-03 00:00:00'")


def files():
    n = 0
    for root, _, fs in os.walk("/lab/warehouse/db/t_fail"):
        n += sum(1 for f in fs if f.endswith(".parquet"))
    return n


b = (spark.sql("SELECT count(*) FROM lab.db.t_fail.snapshots").collect()[0][0], files())
msg = ""
try:
    spark.sql(f"INSERT INTO t_fail SELECT order_id, order_ts, product_id, customer_id, promised_days, delivery_days, "
              f"if(order_ts >= {T} '2026-03-02 23:00:00', CAST(raise_error('boom at the end') AS DOUBLE), order_total) "
              f"FROM orders WHERE order_ts < {T} '2026-03-03 00:00:00'")
except Exception as e:
    j = getattr(e, "java_exception", None)
    msg = (j.getMessage() if j is not None else str(e)).strip().splitlines()[0][:260]
a = (spark.sql("SELECT count(*) FROM lab.db.t_fail.snapshots").collect()[0][0], files())
out = {"error": msg, "snapshots_before_after": [b[0], a[0]], "parquet_before_after": [b[1], a[1]]}
print("RESULT", json.dumps(out))
json.dump(out, open(f"{OUT}/dsv2b_failed.json", "w"), indent=1)
