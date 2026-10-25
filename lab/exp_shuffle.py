"""Chapter 4: shuffle bytes and time under each compression codec. arg = codec name or 'none'."""
import json
import sys
import time

from labutil import OUT, session

codec = sys.argv[1]
spark = session("shuffle-" + codec)
spark.conf.set("spark.sql.adaptive.enabled", "false")
spark.conf.set("spark.sql.shuffle.partitions", "40")
if codec == "none":
    spark.conf.set("spark.shuffle.compress", "false")
else:
    spark.conf.set("spark.io.compression.codec", codec)
q = "SELECT count(*) FROM (SELECT order_id, product_id, customer_id, order_total FROM orders DISTRIBUTE BY customer_id)"
spark.sparkContext.setJobGroup("shuf_" + codec, "shuf")
t = time.time(); spark.sql(q).collect(); el = round(time.time() - t, 1)
print("RESULT", json.dumps({"codec": codec, "seconds": el}))
json.dump({"codec": codec, "seconds": el}, open(f"{OUT}/shuffle_{codec}.json", "w"))
