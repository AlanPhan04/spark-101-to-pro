"""Chapter 15: three OOM signatures. arg = driver | task. Container kill is run_oom.sh."""
import sys

from labutil import session

spark = session("debug-oom-" + sys.argv[1])
spark.conf.set("spark.sql.adaptive.enabled", "false")
if sys.argv[1] == "driver":
    spark.table("orders").collect()                                  # 30M rows pulled into the driver JVM
elif sys.argv[1] == "sort":
    spark.conf.set("spark.sql.shuffle.partitions", "4")
    spark.sql("SELECT * FROM orders ORDER BY order_total").write.format("noop").mode("overwrite").save()
else:
    spark.conf.set("spark.sql.shuffle.partitions", "8")
    spark.sql("SELECT product_id, collect_list(order_id) FROM orders GROUP BY product_id").write.format("noop").mode("overwrite").save()
