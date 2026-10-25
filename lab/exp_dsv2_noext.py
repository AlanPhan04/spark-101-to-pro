"""Chapter 19: the same SQL with the Iceberg session extension absent. Run with EXTRA_CONF='--conf spark.sql.extensions='"""
import json

from labutil import OUT, session

spark = session("dsv2-noext")
res = {"spark.sql.extensions": spark.conf.get("spark.sql.extensions", "<unset>")}
for name, q in [("CALL rewrite_data_files", "CALL lab.system.rewrite_data_files(table => 'db.orders')"),
                ("ADD PARTITION FIELD", "ALTER TABLE orders ADD PARTITION FIELD bucket(4, customer_id)"),
                ("plain SELECT", "SELECT count(*) FROM orders"),
                ("metadata table", "SELECT count(*) FROM lab.db.orders.snapshots")]:
    try:
        spark.sql(q).collect(); res[name] = "ok"
    except Exception as e:
        res[name] = str(e).strip().splitlines()[0][:220]
    print(name, "->", res[name])
json.dump(res, open(f"{OUT}/dsv2_noext.json", "w"), indent=1)
