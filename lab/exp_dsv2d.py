"""Chapter 19: the statistic Iceberg reports is rows x default width of the PROJECTED columns."""
import json

from labutil import OUT, session

spark = session("dsv2d")
spark.conf.set("spark.sql.adaptive.enabled", "false")
rows = []
for name, q in [("dim_product, all 6 columns", "SELECT * FROM dim_product"),
                ("dim_product, product_id", "SELECT product_id FROM dim_product"),
                ("dim_product, product_id + category", "SELECT product_id, category FROM dim_product"),
                ("dim_product, list_price", "SELECT list_price FROM dim_product"),
                ("orders, order_total", "SELECT order_total FROM orders"),
                ("orders, all 7 columns", "SELECT * FROM orders")]:
    st = spark.sql(q)._jdf.queryExecution().optimizedPlan().stats()
    rows.append({"scan": name, "sizeInBytes": int(str(st.sizeInBytes())), "rowCount": str(st.rowCount())})
    print(rows[-1])
for t in ("orders", "dim_product", "dim_date"):
    print(t, [(f.name(), str(f.dataType().simpleString()), f.dataType().defaultSize()) for f in spark.table(t)._jdf.schema().fields()])
    rows.append({"table": t, "schema_default_sizes": [(f.name(), int(f.dataType().defaultSize())) for f in spark.table(t)._jdf.schema().fields()]})
# on-disk bytes of the same tables
for t in ("orders", "dim_product", "dim_date"):
    b = spark.sql(f"SELECT sum(file_size_in_bytes) FROM lab.db.{t}.files").collect()[0][0]
    rows.append({"table_files_bytes": t, "bytes": int(b)})
    print(t, "files bytes", b)
json.dump(rows, open(f"{OUT}/dsv2d_results.json", "w"), indent=1)
