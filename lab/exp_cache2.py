"""Chapter 8, part 2: break-even reads, working exchange reuse, borrowing/eviction, LRU thrashing."""
import json
import time

from pyspark import StorageLevel

from labutil import OUT, plan_text, run, session, storage_info

spark = session("exp-cache2")
spark.conf.set("spark.sql.adaptive.enabled", "false")
res = {}
WEEK = "order_ts >= TIMESTAMP '2026-03-01 00:00:00' AND order_ts < TIMESTAMP '2026-03-08 00:00:00'"


def agg_read(df):
    df.groupBy("product_id").sum("order_total").count()


def timeit(fn):
    t = time.time(); fn(); return round(time.time() - t, 2)


# --- A. break-even: N aggregations over one week --------------------------------------------------------------------
agg_read(spark.table("orders").where(WEEK))   # warm-up: JIT, OS page cache
sweep = []
for n in (1, 2, 5):
    no = timeit(lambda: [agg_read(spark.table("orders").where(WEEK)) for _ in range(n)])
    c = spark.table("orders").where(WEEK).cache()
    mat = timeit(lambda: c.count())
    rd = timeit(lambda: [agg_read(c) for _ in range(n)])
    c.unpersist(blocking=True)
    sweep.append({"reads": n, "no_cache_s": no, "materialize_s": mat, "cached_reads_s": rd, "cache_total_s": round(mat + rd, 2)})
    print("sweep", sweep[-1])
res["sweep"] = sweep

# --- D. exchange reuse that actually uses the aggregates ---------------------------------------------------------------
REUSE = """WITH w AS (SELECT product_id, sum(order_total) AS s FROM orders GROUP BY product_id)
           SELECT sum(a.s + b.s) AS t FROM w a JOIN w b ON a.product_id = b.product_id"""
BROKEN = """SELECT sum(a.s + b.m) AS t
            FROM (SELECT product_id, sum(order_total) AS s FROM orders GROUP BY product_id) a
            JOIN (SELECT product_id, max(order_total) AS m FROM orders GROUP BY product_id) b ON a.product_id = b.product_id"""
spark.conf.set("spark.sql.exchange.reuse", "true")
res["reuse_on_s"] = timeit(lambda: run(spark, "c_d1_reuse_on", REUSE))
spark.conf.set("spark.sql.exchange.reuse", "false")
res["reuse_off_s"] = timeit(lambda: run(spark, "c_d2_reuse_off", REUSE))
spark.conf.set("spark.sql.exchange.reuse", "true")
res["broken_s"] = timeit(lambda: run(spark, "c_d3_reuse_broken", BROKEN))

# --- E. borrowing and eviction -------------------------------------------------------------------------------------------------
month = spark.table("orders").cache()
month.count()
res["E_after_cache"] = storage_info(spark, "month cached, MEMORY_AND_DISK")
JOIN = "SELECT count(*) FROM orders o JOIN dim_customer c ON o.customer_id = c.customer_id WHERE c.segment = 'gold'"
spark.sparkContext.setJobGroup("c_e1_join_under_cache", "c_e1_join_under_cache")
spark.sql(JOIN).collect()
res["E_after_join"] = storage_info(spark, "after a join in the same application")
month.unpersist(blocking=True)

# --- F. LRU thrashing: three caches that do not fit together (MEMORY_ONLY so evicted blocks are dropped) ------------------------
for name, lo, hi in [("ca", 1, 9), ("cb", 9, 17), ("cc", 17, 25)]:
    spark.sql(f"CREATE OR REPLACE TEMP VIEW {name} AS SELECT * FROM orders WHERE order_ts >= TIMESTAMP '2026-03-{lo:02d} 00:00:00' AND order_ts < TIMESTAMP '2026-03-{hi:02d} 00:00:00'")
steps = {}
for name in ("ca", "cb", "cc"):
    spark.catalog.cacheTable(name, StorageLevel.MEMORY_ONLY)
    spark.table(name).count()
    steps["after_" + name] = storage_info(spark, f"after caching {name}")
res["F_steps"] = steps
res["F_reread_ca_s"] = timeit(lambda: spark.table("ca").count())
steps2 = storage_info(spark, "after re-reading ca")
res["F_after_reread"] = steps2
for name in ("ca", "cb", "cc"):
    spark.catalog.uncacheTable(name)

json.dump(res, open(f"{OUT}/cache2_results.json", "w"), indent=1, default=str)
print("DONE")
