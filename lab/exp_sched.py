"""Chapter 18: which shuffle writer each SQL shuffle gets, and what scheduling costs per task."""
import json
import time

from labutil import OUT, session

spark = session("sched")
spark.conf.set("spark.sql.adaptive.enabled", "false")
res = {}


def handles(rdd, out, seen):
    if rdd.id() in seen:
        return
    seen.add(rdd.id())
    it = rdd.dependencies().iterator()
    while it.hasNext():
        d = it.next()
        if d.getClass().getSimpleName() == "ShuffleDependency":
            out.append(d.shuffleHandle().getClass().getSimpleName().replace("ShuffleHandle", ""))
        handles(d.rdd(), out, seen)


def writers(df):
    out = []
    handles(df._jdf.queryExecution().executedPlan().execute(), out, set())
    return out


# --- 1. writer per shuffle
rows = []
for n in (50, 200, 201, 1000):
    spark.conf.set("spark.sql.shuffle.partitions", str(n))
    cases = {
        "repartition(n)": spark.table("orders").select("order_id", "customer_id").repartition(n),
        "GROUP BY": spark.sql("SELECT customer_id, count(*) c, sum(order_total) s FROM orders GROUP BY customer_id"),
        "sort-merge join": spark.sql("SELECT /*+ MERGE(p) */ count(*) FROM orders o JOIN dim_product p ON o.product_id = p.product_id"),
        "ORDER BY": spark.sql("SELECT order_id FROM orders ORDER BY order_total"),
        "window": spark.sql("SELECT sum(order_total) OVER (PARTITION BY customer_id) FROM orders"),
    }
    for name, df in cases.items():
        w = writers(df)
        rows.append({"partitions": n, "query": name, "writers": w})
        print(n, name, w)
res["writers"] = rows

# --- 2. scheduling cost per task: n empty-ish tasks in one stage (local[8])
spark.conf.set("spark.sql.shuffle.partitions", "8")
trows = []
for n in (1000, 5000, 20000, 80000):
    q = spark.range(0, n, 1, n).selectExpr("sum(id)")
    q.collect()
    t = time.time(); q.collect(); el = time.time() - t
    trows.append({"tasks": n, "seconds": round(el, 2), "ms_per_task": round(1000 * el / n, 3)})
    print(trows[-1])
res["task_scheduling"] = trows
json.dump(res, open(f"{OUT}/sched_results.json", "w"), indent=1)
print("DONE")
