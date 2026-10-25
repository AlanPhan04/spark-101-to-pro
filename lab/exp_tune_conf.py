"""Chapter 14: which layer wins? Same key set in spark-defaults-style file, --conf, application code, and SET at runtime.

run via tune_conf.sh, which passes --properties-file and --conf variants; this script reports what the session sees.
"""
import json
import sys

from pyspark import SparkConf
from pyspark.sql import SparkSession

mode = sys.argv[1]       # "code" sets the key in SparkSession.builder; "plain" does not
b = SparkSession.builder.appName("tune-conf")
if mode == "code":
    b = b.config("spark.sql.shuffle.partitions", "300")
spark = b.getOrCreate()
spark.sparkContext.setLogLevel("ERROR")
seen = {"mode": mode, "initial": spark.conf.get("spark.sql.shuffle.partitions")}
spark.conf.set("spark.sql.shuffle.partitions", "400")
seen["after_runtime_set"] = spark.conf.get("spark.sql.shuffle.partitions")
try:
    spark.conf.set("spark.executor.memory", "9g")
    seen["static_set"] = "accepted: " + spark.conf.get("spark.executor.memory")
except Exception as e:
    seen["static_set"] = "rejected"
seen["executor_memory_in_sparkconf"] = spark.sparkContext.getConf().get("spark.executor.memory", "unset")
print("RESULT", json.dumps(seen))
