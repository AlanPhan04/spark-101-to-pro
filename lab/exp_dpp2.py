"""DPP when the fact table is partitioned by the join column itself (identity partition on order_date)."""
from labutil import run, session

spark = session("exp-dpp2")
C = spark.conf.set
spark.sql("DROP TABLE IF EXISTS orders_d")
spark.sql("CREATE TABLE orders_d USING iceberg PARTITIONED BY (order_date) AS "
          "SELECT *, CAST(order_ts AS DATE) AS order_date FROM orders")
DPP = """SELECT count(*) AS n, sum(o.order_total) AS total
         FROM orders_d o
         JOIN dim_date d ON o.order_date = d.date
         WHERE d.day_of_week = 'Sat' AND d.month = 3"""
C("spark.sql.optimizer.dynamicPartitionPruning.enabled", "false")
run(spark, "e5c_dpp_off_identity", DPP)
C("spark.sql.optimizer.dynamicPartitionPruning.enabled", "true")
run(spark, "e5d_dpp_on_identity", DPP)
# DPP requires broadcast reuse: disable broadcasting and see
C("spark.sql.autoBroadcastJoinThreshold", "-1")
run(spark, "e5e_dpp_on_nobroadcast", DPP)
print("DONE")
