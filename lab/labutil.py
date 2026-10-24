"""Shared helpers for the lab experiments."""
import os

from pyspark.sql import SparkSession

OUT = "/lab/out"


def session(name):
    spark = (SparkSession.builder.appName(name)
             .config("spark.sql.session.timeZone", "UTC").getOrCreate())
    spark.sparkContext.setLogLevel("ERROR")
    spark.sql("USE lab.db")
    return spark


def plan_text(df, mode="formatted"):
    qe = df._jdf.queryExecution()
    jmode = df.sparkSession._jvm.org.apache.spark.sql.execution.ExplainMode.fromString(mode)
    return qe.explainString(jmode)


def run(spark, group, sql, show_plan=True, mode="formatted"):
    """Run a query to completion under a job group, then save the plan AS EXECUTED."""
    spark.sparkContext.setJobGroup(group, group)
    df = spark.sql(sql)
    rows = df.collect()
    text = plan_text(df, mode) if show_plan else ""
    os.makedirs(OUT, exist_ok=True)
    with open(f"{OUT}/{group}.plan.txt", "w", encoding="utf-8") as f:
        f.write(f"-- {group}\n-- {' '.join(sql.split())}\n\n{text}\n")
    simple = plan_text(df, "simple") if show_plan else ""
    with open(f"{OUT}/{group}.simple.txt", "w", encoding="utf-8") as f:
        f.write(simple)
    print(f"=== {group}: {len(rows)} result rows")
    return df, rows


def set_conf(spark, **kv):
    for k, v in kv.items():
        spark.conf.set(k.replace("__", "."), str(v))
