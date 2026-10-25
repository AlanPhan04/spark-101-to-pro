"""Why did read.split.target-size not change the task count?"""
from labutil import run_scan as run, session, show

spark = session("exp-split-diag")
spark.conf.set("spark.sql.adaptive.enabled", "false")
FULL = "SELECT sum(order_total) AS s FROM {t}"
# t_plain: 10 unpartitioned files of ~35 MB
show(spark, "sp0_props", "SHOW TBLPROPERTIES t_plain")
run(spark, "sp1_default", FULL.format(t="t_plain"))
spark.sql("ALTER TABLE t_plain SET TBLPROPERTIES ('read.split.target-size'='536870912')")
run(spark, "sp2_prop_512mb", FULL.format(t="t_plain"))
spark.sql("ALTER TABLE t_plain SET TBLPROPERTIES ('read.split.target-size'='8388608')")
run(spark, "sp3_prop_8mb", FULL.format(t="t_plain"))
spark.sql("ALTER TABLE t_plain UNSET TBLPROPERTIES ('read.split.target-size')")
df = spark.read.option("split-size", str(536870912)).table("t_plain").selectExpr("sum(order_total)")
spark.sparkContext.setJobGroup("sp4_option_512mb", "sp4_option_512mb"); df.collect()
from labutil import scan_metrics
print("option 512mb:", {k: v for k, v in list(scan_metrics(df).values())[0].items() if k in ("numSplits", "resultDataFiles")})
df = spark.read.option("split-size", str(8388608)).table("t_plain").selectExpr("sum(order_total)")
spark.sparkContext.setJobGroup("sp5_option_8mb", "sp5_option_8mb"); df.collect()
print("option 8mb:", {k: v for k, v in list(scan_metrics(df).values())[0].items() if k in ("numSplits", "resultDataFiles")})
print("DONE")
