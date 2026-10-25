"""Chapter 8, part 3 (run twice): `sweep` at 4 GB, `thrash` at 2 GB of heap so the caches do not fit together."""
import json
import sys
import time

from pyspark import StorageLevel

from labutil import OUT, session, storage_info

mode = sys.argv[1]
spark = session("exp-cache3-" + mode)
spark.conf.set("spark.sql.adaptive.enabled", "false")
WEEK = "order_ts >= TIMESTAMP '2026-03-01 00:00:00' AND order_ts < TIMESTAMP '2026-03-08 00:00:00'"
res = {}


def timeit(fn):
    t = time.time(); fn(); return round(time.time() - t, 2)


def agg_read(df):
    df.groupBy("product_id").sum("order_total").count()


if mode == "sweep":
    agg_read(spark.table("orders").where(WEEK))   # warm-up
    out = []
    for n in (1, 2, 5, 10):
        no = timeit(lambda: [agg_read(spark.table("orders").where(WEEK)) for _ in range(n)])
        c = spark.table("orders").where(WEEK).cache()
        mat = timeit(lambda: c.count())
        rd = timeit(lambda: [agg_read(c) for _ in range(n)])
        c.unpersist(blocking=True)
        out.append({"reads": n, "no_cache_s": no, "materialize_s": mat, "cached_reads_s": rd, "cache_total_s": round(mat + rd, 2)})
        print("sweep", out[-1])
    res["sweep"] = out
elif mode == "borrow":
    month = spark.table("orders").cache()
    month.count()
    res["after_cache"] = storage_info(spark, "month cached, MEMORY_AND_DISK")
    spark.sql("SELECT count(*) FROM orders o JOIN dim_customer c ON o.customer_id = c.customer_id WHERE c.segment = 'gold'").collect()
    res["after_join"] = storage_info(spark, "after a join in the same application")
else:
    for name, lo, hi in [("ca", 1, 9), ("cb", 9, 17), ("cc", 17, 25)]:
        spark.sql(f"CREATE OR REPLACE TEMP VIEW {name} AS SELECT * FROM orders WHERE order_ts >= TIMESTAMP '2026-03-{lo:02d} 00:00:00' AND order_ts < TIMESTAMP '2026-03-{hi:02d} 00:00:00'")
    steps = {}
    for name in ("ca", "cb", "cc"):
        spark.catalog.cacheTable(name, StorageLevel.MEMORY_ONLY)
        spark.table(name).count()
        steps["after_" + name] = storage_info(spark, f"after caching {name}")
    res["steps"] = steps
    res["reread_ca_s"] = timeit(lambda: spark.table("ca").count())
    res["after_reread"] = storage_info(spark, "after re-reading ca")
    res["reread_cc_s"] = timeit(lambda: spark.table("cc").count())
    res["after_reread_cc"] = storage_info(spark, "after re-reading cc")
json.dump(res, open(f"{OUT}/cache3_{mode}.json", "w"), indent=1, default=str)
print("DONE")
