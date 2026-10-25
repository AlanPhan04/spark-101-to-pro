"""Chapter 19: what the DSv2 negotiation looks like from outside. Pushdown outcome per predicate, aggregate pushdown, statistics, failed write."""
import json
import os
import re
import time

from labutil import OUT, plan_text, scan_metrics, session

spark = session("dsv2")
spark.conf.set("spark.sql.adaptive.enabled", "false")
T = "TIMESTAMP"
res = {}

# --- 1. one predicate at a time: does Iceberg take it, and does Spark keep a Filter above the scan?
preds = [
    ("range on partition source", f"order_ts >= {T} '2026-03-05 00:00:00' AND order_ts < {T} '2026-03-06 00:00:00'"),
    ("equality on data column", "product_id = 'p0000042'"),
    ("IN list on data column", "customer_id IN ('c00000007','c00000008','c00000009')"),
    ("range on data column", "order_total > 900"),
    ("CAST ts AS STRING", "CAST(order_ts AS STRING) >= '2026-03-05' AND CAST(order_ts AS STRING) < '2026-03-06'"),
    ("function on data column", "lower(product_id) = 'p0000042'"),
    ("arithmetic on data column", "order_total * 2 > 1800"),
    ("LIKE prefix", "product_id LIKE 'p00000%'"),
    ("two columns compared", "promised_days < delivery_days"),
]
rows = []
for name, p in preds:
    df = spark.sql(f"SELECT sum(order_total) FROM orders WHERE {p}")
    df.collect()
    plan = df._jdf.queryExecution().executedPlan().toString()
    scan = [l for l in plan.splitlines() if "BatchScan" in l][0].strip()
    has_filter = any(re.search(r"^\s*[+:\- ]*\*?\(?\d*\)?\s*Filter\b", l) for l in plan.splitlines())
    m = list(scan_metrics(df).values())[0]
    rows.append({"predicate": name, "sql": p, "scan_line": scan[:230], "filter_above_scan": has_filter,
                 "rows_out_of_scan": m.get("numOutputRows"), "files_read": m.get("resultDataFiles", m.get("numFiles"))})
    print(name, "| Filter above:", has_filter, "| scan rows:", m.get("numOutputRows"), "|", scan[:160])
res["pushdown"] = rows

# --- 2. aggregate pushdown
aggs = [("count(*) no filter", "SELECT count(*) FROM orders"),
        ("min/max order_ts", "SELECT min(order_ts), max(order_ts) FROM orders"),
        ("count(*) partition filter", f"SELECT count(*) FROM orders WHERE order_ts >= {T} '2026-03-05 00:00:00' AND order_ts < {T} '2026-03-06 00:00:00'"),
        ("count(*) data filter", "SELECT count(*) FROM orders WHERE product_id = 'p0000042'"),
        ("sum(order_total)", "SELECT sum(order_total) FROM orders"),
        ("max(order_total)", "SELECT max(order_total) FROM orders")]
arows = []
for name, q in aggs:
    df = spark.sql(q)
    t = time.time(); r = df.collect(); el = round(time.time() - t, 2)
    plan = df._jdf.queryExecution().executedPlan().toString()
    kind = "LocalTableScan" if "LocalTableScan" in plan else ("BatchScan" if "BatchScan" in plan else "other")
    arows.append({"query": name, "seconds": el, "root_leaf": kind, "result": str(r[0]), "plan_head": " | ".join(l.strip() for l in plan.splitlines()[:4])[:300]})
    print(name, el, kind, r[0])
res["aggregates"] = arows

# --- 3. statistics the source reports
srows = []
for name, q in [("orders", "SELECT * FROM orders"),
                ("orders, one day", f"SELECT * FROM orders WHERE order_ts >= {T} '2026-03-05 00:00:00' AND order_ts < {T} '2026-03-06 00:00:00'"),
                ("orders, product = hot", "SELECT * FROM orders WHERE product_id = 'p0000042'"),
                ("dim_product", "SELECT * FROM dim_product"),
                ("dim_date", "SELECT * FROM dim_date")]:
    st = spark.sql(q)._jdf.queryExecution().optimizedPlan().stats()
    srows.append({"scan": name, "sizeInBytes": int(str(st.sizeInBytes())), "rowCount": str(st.rowCount())})
    print(name, srows[-1])
res["stats"] = srows

# --- 4. a failed write leaves no snapshot
spark.sql("DROP TABLE IF EXISTS t_fail PURGE")
spark.sql(f"CREATE TABLE t_fail USING iceberg AS SELECT * FROM orders WHERE order_ts < {T} '2026-03-03 00:00:00'")
wh = "/lab/warehouse/db/t_fail"


def disk_files():
    n = 0
    for root, _, fs in os.walk(wh + "/data"):
        n += sum(1 for f in fs if f.endswith(".parquet"))
    return n


before = {"snapshots": spark.sql("SELECT count(*) FROM lab.db.t_fail.snapshots").collect()[0][0], "parquet_on_disk": disk_files(),
          "rows": spark.sql("SELECT count(*) FROM t_fail").collect()[0][0]}
err = ""
try:
    spark.sql(f"INSERT INTO t_fail SELECT order_id, order_ts, product_id, customer_id, promised_days, delivery_days, "
              f"if(order_ts >= {T} '2026-03-02 23:00:00', CAST(raise_error('boom at the end') AS DOUBLE), order_total) "
              f"FROM orders WHERE order_ts < {T} '2026-03-03 00:00:00'")
except Exception as e:
    err = str(e).strip().splitlines()[0][:200]
after = {"snapshots": spark.sql("SELECT count(*) FROM lab.db.t_fail.snapshots").collect()[0][0], "parquet_on_disk": disk_files(),
         "rows": spark.sql("SELECT count(*) FROM t_fail").collect()[0][0]}
res["failed_write"] = {"before": before, "after": after, "error": err}
print("failed write", res["failed_write"])
json.dump(res, open(f"{OUT}/dsv2_results.json", "w"), indent=1, default=str)
print("DONE")
