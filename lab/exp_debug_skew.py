"""Chapter 15: the four task metrics on a real skewed stage. DRIVER_MEM=1g CORES=4, 40 shuffle partitions, AQE off, sort-merge join on the hot product."""
import time

from labutil import session

spark = session("debug-skew")
spark.conf.set("spark.sql.adaptive.enabled", "false")
spark.conf.set("spark.sql.shuffle.partitions", "40")
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")
spark.sparkContext.setJobGroup("debug_skew", "debug_skew")
t = time.time()
spark.sql("""SELECT /*+ MERGE(p) */ p.category, count(*), sum(o.order_total)
             FROM orders o JOIN dim_product p ON o.product_id = p.product_id GROUP BY p.category""").collect()
print("RESULT seconds", round(time.time() - t, 1))
