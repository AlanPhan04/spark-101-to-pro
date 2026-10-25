"""Chapter 3: pool sizes per heap, object overhead on the JVM. Run with several DRIVER_MEM values."""
import json
import sys

from labutil import OUT, session

spark = session("memory")
jvm = spark._jvm
rt = jvm.java.lang.Runtime.getRuntime()
mm = spark.sparkContext._jsc.sc().env().memoryManager()
mx = rt.maxMemory()
rec = {"label": sys.argv[1], "jvm_max_mb": round(mx / 1048576, 1), "unified_mb": round(mm.maxOnHeapStorageMemory() / 1048576, 1),
       "formula_mb": round((mx - 300 * 1048576) * 0.6 / 1048576, 1)}
if sys.argv[1] == "4g":
    se = jvm.org.apache.spark.util.SizeEstimator
    n = 1_000_000
    stream = jvm.java.util.stream
    boxed = stream.IntStream.range(0, n).boxed().collect(stream.Collectors.toList())
    prim = stream.IntStream.range(0, n).toArray()
    strs = stream.IntStream.range(0, 100_000).mapToObj(jvm.java.lang.String.valueOf).collect(stream.Collectors.toList()) if False else None
    rec["objects"] = {"int[1M] bytes": int(se.estimate(prim)), "List<Integer>(1M) bytes": int(se.estimate(boxed)),
                      "overhead_x": round(se.estimate(boxed) / se.estimate(prim), 1)}
    s10 = "abcdefghij"
    rec["objects"]["String(10 chars) bytes"] = int(se.estimate(jvm.java.lang.String(s10)))
print("RESULT", json.dumps(rec))
json.dump(rec, open(f"{OUT}/memory_{sys.argv[1]}.json", "w"), indent=1)
