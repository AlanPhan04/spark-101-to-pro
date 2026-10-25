"""Chapter 19: which DSv2 interfaces Iceberg 1.6.1 implements, read from the live classes by reflection."""
import json

from labutil import OUT, session

spark = session("dsv2c")
jvm = spark._jvm
cm = spark._jsparkSession.sessionState().catalogManager()
cat = cm.catalog("lab")
gw = spark.sparkContext._gateway
ns = gw.new_array(gw.jvm.java.lang.String, 1)
ns[0] = "db"
ident = jvm.org.apache.spark.sql.connector.catalog.Identifier.of(ns, "orders")
tbl = cat.loadTable(ident)


def ifaces(o):
    seen, out, stack = set(), [], [o.getClass()]
    while stack:
        c = stack.pop()
        if c is None or str(c.getName()) in seen:
            continue
        seen.add(str(c.getName()))
        for i in c.getInterfaces():
            n = str(i.getName())
            if "connector" in n:
                out.append(n.split(".")[-1])
            stack.append(i)
        stack.append(c.getSuperclass())
    return sorted(set(out))


opts = jvm.org.apache.spark.sql.util.CaseInsensitiveStringMap(jvm.java.util.HashMap())
sb = tbl.newScanBuilder(opts)
scan = sb.build()
res = {"table_class": str(tbl.getClass().getSimpleName()), "table_interfaces": ifaces(tbl),
       "scan_builder_class": str(sb.getClass().getSimpleName()), "scan_builder_interfaces": ifaces(sb),
       "scan_class": str(scan.getClass().getSimpleName()), "scan_interfaces": ifaces(scan),
       "catalog_class": str(cat.getClass().getName()), "catalog_interfaces": ifaces(cat)}
print("RESULT", json.dumps(res, indent=1))
json.dump(res, open(f"{OUT}/dsv2_interfaces.json", "w"), indent=1)
