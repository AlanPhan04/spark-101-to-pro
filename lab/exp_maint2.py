"""Chapter 13, part 2: expire_snapshots and remove_orphan_files on the t_mor table left by exp_maint.py."""
import json
import os
import time

from labutil import OUT, session

spark = session("exp-maint2")
WH = "/lab/warehouse/db"


def dir_mb(t):
    total = 0
    for root, _, files in os.walk(f"{WH}/{t}"):
        for f in files:
            total += os.path.getsize(os.path.join(root, f))
    return round(total / 1e6, 1)


def count(sql):
    return spark.sql(sql).collect()[0][0]


res = {}
res["dir_mb_before"] = dir_mb("t_mor")
res["snapshots_before"] = count("SELECT count(*) FROM lab.db.t_mor.snapshots")
res["data_files_before"] = count("SELECT count(*) FROM lab.db.t_mor.files")
future = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time() + 3600))
r = spark.sql(f"CALL lab.system.expire_snapshots(table => 'db.t_mor', older_than => TIMESTAMP '{future}', retain_last => 1)").collect()[0]
res["expire_row"] = [str(x) for x in r]
res["snapshots_after"] = count("SELECT count(*) FROM lab.db.t_mor.snapshots")
res["dir_mb_after_expire"] = dir_mb("t_mor")
with open(f"{WH}/t_mor/data/stray-orphan.parquet", "wb") as f:
    f.write(os.urandom(5000000))
res["dir_mb_with_orphan"] = dir_mb("t_mor")
future = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time() + 3600))
dry = spark.sql(f"CALL lab.system.remove_orphan_files(table => 'db.t_mor', older_than => TIMESTAMP '{future}', dry_run => true)").collect()
res["orphans_found"] = [str(x[0]).split("/")[-1] for x in dry]
spark.sql(f"CALL lab.system.remove_orphan_files(table => 'db.t_mor', older_than => TIMESTAMP '{future}')").collect()
res["dir_mb_after_orphans"] = dir_mb("t_mor")
res["rows_ok"] = count("SELECT count(*) FROM t_mor")
print("M5", res)
json.dump(res, open(f"{OUT}/maint2_results.json", "w"), indent=1)
print("DONE")
