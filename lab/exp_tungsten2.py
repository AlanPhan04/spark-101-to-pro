"""Chapter 17, part 2: the 100-field codegen limit, and the Arrow-based UDF if pyarrow is importable."""
import json
import re
import time

from labutil import OUT, plan_text, session

spark = session("tungsten2")
spark.conf.set("spark.sql.adaptive.enabled", "false")
res = {"maxFields": spark.conf.get("spark.sql.codegen.maxFields")}
wide = []
for n in (10, 50, 99, 100, 101, 200, 400):
    cols = ", ".join(f"order_total * {i + 1} + promised_days AS c{i}" for i in range(n))
    df = spark.sql(f"SELECT {cols} FROM orders")
    plan = plan_text(df, "simple")
    t = time.time()
    df.write.format("noop").mode("overwrite").save()
    el = round(time.time() - t, 1)
    top = [l for l in plan.splitlines() if "Project" in l][:1]
    wide.append({"columns": n, "wholestage_in_project": bool(top and "*(" in top[0]), "seconds": el})
    print(wide[-1])
res["wide"] = wide
try:
    import pyarrow  # noqa
    from pyspark.sql.functions import pandas_udf
    from pyspark.sql.types import DoubleType
    spark.udf.register("pd_tax", pandas_udf(lambda s: s * 1.07, DoubleType()))
    q = "SELECT sum(pd_tax(order_total)) FROM orders"
    spark.sql(q).collect()
    ts = []
    for _ in range(2):
        t = time.time(); spark.sql(q).collect(); ts.append(time.time() - t)
    res["pandas_udf_s"] = round(sorted(ts)[0], 2)
    res["pandas_plan_node"] = "ArrowEvalPython" if "ArrowEvalPython" in plan_text(spark.sql(q), "simple") else "?"
except Exception as e:
    res["pandas_udf_s"] = "unavailable: " + str(e)[:80]
print("RESULT", json.dumps(res))
json.dump(res, open(f"{OUT}/tungsten2_results.json", "w"), indent=1)
