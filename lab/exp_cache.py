"""Chapter 8: when caching pays, lazy vs eager, storage levels, borrowing/eviction, exchange reuse."""
import json
import time

from pyspark import StorageLevel

from labutil import OUT, plan_text, run, session, storage_info

spark = session("exp-cache")
spark.conf.set("spark.sql.adaptive.enabled", "false")
results = {}
WEEK = "order_ts >= TIMESTAMP '2026-03-01 00:00:00' AND order_ts < TIMESTAMP '2026-03-08 00:00:00'"


def timed(group, fn):
    spark.sparkContext.setJobGroup(group, group)
    t = time.time()
    out = fn()
    return round(time.time() - t, 2), out


# --- A. when caching pays: week of orders read by two aggregations ------------------------------------------
def two_reads(df):
    a = df.groupBy("product_id").sum("order_total").count()
    b = df.groupBy("customer_id").count().count()
    return a, b

base = spark.table("orders").where(WEEK)
t_nocache, _ = timed("c_a1_nocache", lambda: two_reads(base))
cached = spark.table("orders").where(WEEK).cache()
t_first, _ = timed("c_a2_cache_first_use", lambda: cached.count())
t_cached, _ = timed("c_a3_cached_two_reads", lambda: two_reads(cached))
results["A"] = {"no_cache_two_reads_s": t_nocache, "cache_materialize_s": t_first, "cached_two_reads_s": t_cached}
results["A_storage"] = storage_info(spark, "after cache of one week")
cached.unpersist()

# --- B. lazy vs eager ------------------------------------------------------------------------------------------------------
lazy = spark.table("orders").where(WEEK).cache()
results["B_after_cache_call"] = storage_info(spark, "after .cache() with no action")
lazy.count()
results["B_after_action"] = storage_info(spark, "after count()")
lazy.unpersist()
spark.sql(f"CACHE LAZY TABLE wk_lazy AS SELECT * FROM orders WHERE {WEEK}")
results["B_cache_lazy_table"] = storage_info(spark, "after CACHE LAZY TABLE")
spark.sql("SELECT count(*) FROM wk_lazy").collect()
results["B_lazy_after_use"] = storage_info(spark, "after first use")
spark.sql("UNCACHE TABLE wk_lazy")
spark.sql(f"CACHE TABLE wk_eager AS SELECT * FROM orders WHERE {WEEK}")
results["B_cache_table_eager"] = storage_info(spark, "after CACHE TABLE (eager)")
spark.sql("UNCACHE TABLE wk_eager")

# --- C. storage levels: same rows, three representations --------------------------------------------------------------
def size_of(level_name, make):
    d = spark.table("orders").where(WEEK)
    make(d)
    d.count() if level_name != "rdd_objects" else None
    return storage_info(spark, level_name)

for name, lvl in [("MEMORY_AND_DISK", StorageLevel.MEMORY_AND_DISK), ("MEMORY_AND_DISK_SER", StorageLevel(True, True, False, False, 1)),
                  ("DISK_ONLY", StorageLevel.DISK_ONLY)]:
    d = spark.table("orders").where(WEEK)
    d.persist(lvl)
    d.count()
    results["C_" + name] = storage_info(spark, name)
    d.unpersist()
r = spark.table("orders").where(WEEK).rdd
r.persist(StorageLevel.MEMORY_ONLY)
r.count()
results["C_rdd_objects_MEMORY_ONLY"] = storage_info(spark, "RDD of Row objects, MEMORY_ONLY")
r.unpersist()

# --- D. exchange reuse -------------------------------------------------------------------------------------------------------------
REUSE = """WITH w AS (SELECT product_id, sum(order_total) AS s FROM orders GROUP BY product_id)
           SELECT count(*) FROM w a JOIN w b ON a.product_id = b.product_id"""
spark.conf.set("spark.sql.exchange.reuse", "true")
df, _ = run(spark, "c_d1_reuse_on", REUSE)
spark.conf.set("spark.sql.exchange.reuse", "false")
df, _ = run(spark, "c_d2_reuse_off", REUSE)
spark.conf.set("spark.sql.exchange.reuse", "true")
# reuse broken: the two sides aggregate with different expressions
BROKEN = """SELECT count(*) FROM (SELECT product_id, sum(order_total) AS s FROM orders GROUP BY product_id) a
            JOIN (SELECT product_id, max(order_total) AS m FROM orders GROUP BY product_id) b ON a.product_id = b.product_id"""
df, _ = run(spark, "c_d3_reuse_broken", BROKEN)

json.dump(results, open(f"{OUT}/cache_results.json", "w"), indent=1, default=str)
print("DONE")
