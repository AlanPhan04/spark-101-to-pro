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


def show(spark, name, sql, n=20, truncate=60, vertical=False):
    """Run a metadata query and save its table-formatted output to out/<name>.txt."""
    df = spark.sql(sql)
    text = df._jdf.showString(n, truncate, vertical)
    os.makedirs(OUT, exist_ok=True)
    with open(f"{OUT}/{name}.txt", "w", encoding="utf-8") as f:
        f.write("-- " + name + "\n-- " + " ".join(sql.split()) + "\n\n" + text + "\n")
    print(f"=== {name}")
    print(text)
    return df


def enable_scan_reports(spark):
    """Make Iceberg's LoggingMetricsReporter print each ScanReport (INFO) to the console."""
    spark.sparkContext.setLogLevel("WARN")
    jvm = spark._jvm
    jvm.org.apache.logging.log4j.core.config.Configurator.setLevel(
        "org.apache.iceberg.metrics.LoggingMetricsReporter", jvm.org.apache.logging.log4j.Level.INFO)


def scan_metrics(df):
    """SQL metrics of every leaf scan node of the executed plan (AQE must be off)."""
    plan = df._jdf.queryExecution().executedPlan()
    out = {}
    leaves = plan.collectLeaves()
    it = leaves.iterator()
    jvm = df.sparkSession._jvm
    while it.hasNext():
        leaf = it.next()
        name = leaf.nodeName()
        mm = jvm.scala.collection.JavaConverters.mapAsJavaMapConverter(leaf.metrics()).asJava()
        vals = {}
        for k in mm.keySet():
            vals[str(k)] = int(mm.get(k).value())
        out[name + "#" + str(len(out))] = vals
    return out


def run_scan(spark, group, sql):
    """Like run(), but also writes the scan nodes' SQL metrics (Iceberg's scan report counters)."""
    df, rows = run(spark, group, sql)
    m = scan_metrics(df)
    lines = []
    for node, vals in m.items():
        lines.append(node)
        for k in sorted(vals):
            lines.append(f"  {k} = {vals[k]}")
    with open(f"{OUT}/{group}.metrics.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return df, rows


def storage_info(spark, label=""):
    """Rows of (name, level, cached/total partitions, memory MB, disk MB) for every cached RDD."""
    infos = spark.sparkContext._jsc.sc().getRDDStorageInfo()
    rows = []
    for i in range(len(infos)):
        r = infos[i]
        rows.append((str(r.name())[:44], str(r.storageLevel().description()), f"{r.numCachedPartitions()}/{r.numPartitions()}",
                     round(r.memSize() / 1e6, 1), round(r.diskSize() / 1e6, 1)))
    print(f"--- storage {label}")
    for row in rows:
        print("   ", row)
    return rows
