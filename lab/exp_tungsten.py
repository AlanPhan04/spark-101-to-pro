"""Chapter 17: what whole-stage codegen, radix sort, vectorization and Python UDFs cost on the lab data."""
import json
import re
import statistics
import time

from labutil import OUT, plan_text, session

spark = session("tungsten")
spark.conf.set("spark.sql.adaptive.enabled", "false")
spark.conf.set("spark.sql.shuffle.partitions", "40")
res = {}


def bench(sql_or_df, n=3):
    ts = []
    for _ in range(n):
        df = spark.sql(sql_or_df) if isinstance(sql_or_df, str) else sql_or_df
        t = time.time(); df.collect(); ts.append(time.time() - t)
    return round(statistics.median(ts), 2)


# --- 1. whole-stage codegen on / off
queries = {
    "filter + aggregate": "SELECT sum(order_total) FROM orders WHERE order_total > 100 AND promised_days < 5",
    "arithmetic chain": "SELECT sum((order_total * 1.07 + promised_days) / (delivery_days + 1) - order_total * 0.01) FROM orders",
    "group by": "SELECT customer_id, count(*), sum(order_total) FROM orders GROUP BY customer_id HAVING count(*) > 100000",
}
rows = []
for name, q in queries.items():
    spark.sql(q).collect()   # warm
    out = {"query": name}
    for flag in ("true", "false"):
        spark.conf.set("spark.sql.codegen.wholeStage", flag)
        out["codegen_" + flag] = bench(q)
    spark.conf.set("spark.sql.codegen.wholeStage", "true")
    rows.append(out)
    print(out)
res["wholestage"] = rows

# --- 2. real EXPLAIN CODEGEN of a scan + filter + aggregate stage
df = spark.sql("SELECT sum(order_total) FROM orders WHERE order_total > 100 AND promised_days < 5")
code = plan_text(df, "codegen")
open(f"{OUT}/t_codegen.txt", "w").write(code)
res["codegen_chars"] = len(code)

# --- 3. wide expression: n derived columns, does codegen survive?
wide = []
for n in (10, 50, 100, 200, 400):
    cols = ", ".join(f"order_total * {i + 1} + promised_days AS c{i}" for i in range(n))
    q = f"SELECT sum(c{n - 1}) FROM (SELECT {cols} FROM orders)"
    df = spark.sql(q)
    plan = plan_text(df, "simple")
    starred = len(re.findall(r"\*\(\d+\)", plan))
    wide.append({"columns": n, "starred_nodes": starred, "seconds": bench(q, 1)})
    print(wide[-1])
res["wide"] = wide

# --- 4. Python UDF vs built-in
spark.sql("SELECT 1").collect()
from pyspark.sql.functions import udf
from pyspark.sql.types import DoubleType

py = udf(lambda x: x * 1.07, DoubleType())
spark.udf.register("py_tax", py)
df_builtin = spark.sql("SELECT sum(order_total * 1.07) FROM orders")
df_udf = spark.sql("SELECT sum(py_tax(order_total)) FROM orders")
res["udf"] = {"builtin_s": bench(df_builtin, 2), "python_udf_s": bench(df_udf, 1),
              "udf_plan_has_BatchEvalPython": "BatchEvalPython" in plan_text(df_udf, "simple")}
try:
    import pyarrow  # noqa
    from pyspark.sql.functions import pandas_udf
    pu = pandas_udf(lambda s: s * 1.07, DoubleType())
    spark.udf.register("pd_tax", pu)
    res["udf"]["pandas_udf_s"] = bench("SELECT sum(pd_tax(order_total)) FROM orders", 1)
except Exception as e:
    res["udf"]["pandas_udf_s"] = "unavailable: " + str(e)[:80]
print(res["udf"])

# --- 5. radix sort
spark.conf.set("spark.sql.shuffle.partitions", "40")
rs = {}
for flag in ("true", "false"):
    spark.conf.set("spark.sql.sort.enableRadixSort", flag)
    rs[flag] = bench("SELECT sum(x) FROM (SELECT order_id, row_number() OVER (ORDER BY order_ts) x FROM orders WHERE order_ts < TIMESTAMP '2026-03-10')", 2)
spark.conf.set("spark.sql.sort.enableRadixSort", "true")
res["radix"] = rs
print(res["radix"])
json.dump(res, open(f"{OUT}/tungsten_results.json", "w"), indent=1)
print("DONE")
