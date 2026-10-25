"""read.split.target-size with and without Iceberg's adaptive split size."""
from labutil import run_scan as run, session, show

spark = session("exp-split2")
spark.conf.set("spark.sql.adaptive.enabled", "false")
FULL = "SELECT sum(order_total) AS s FROM t_plain"
show(spark, "sp6_split_offsets", "SELECT count(*) AS files, round(avg(size(split_offsets)),1) AS avg_row_groups FROM lab.db.t_plain.files")
spark.sql("ALTER TABLE t_plain SET TBLPROPERTIES ('read.split.adaptive-size.enabled'='false')")
run(spark, "sp7_adaptive_off_default128", FULL)
spark.sql("ALTER TABLE t_plain SET TBLPROPERTIES ('read.split.target-size'='536870912')")
run(spark, "sp8_adaptive_off_512mb", FULL)
spark.sql("ALTER TABLE t_plain SET TBLPROPERTIES ('read.split.target-size'='8388608')")
run(spark, "sp9_adaptive_off_8mb", FULL)
spark.sql("ALTER TABLE t_plain UNSET TBLPROPERTIES ('read.split.target-size')")
spark.sql("ALTER TABLE t_plain UNSET TBLPROPERTIES ('read.split.adaptive-size.enabled')")
print("DONE")
