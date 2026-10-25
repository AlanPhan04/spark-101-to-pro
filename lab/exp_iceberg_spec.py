"""Chapter 9: the metadata tree of a table built by three commits, sequence numbers, time travel, copy-on-write vs merge-on-read deletes."""
import json

from labutil import OUT, session, show

spark = session("exp-iceberg-spec")
T = "TIMESTAMP"
res = {}
for t in ("t_meta",):
    spark.sql(f"DROP TABLE IF EXISTS {t}")
spark.sql(f"CREATE TABLE t_meta USING iceberg PARTITIONED BY (days(order_ts)) AS SELECT * FROM orders WHERE order_ts < {T} '2026-03-04 00:00:00'")
spark.sql(f"INSERT INTO t_meta SELECT * FROM orders WHERE order_ts >= {T} '2026-03-04 00:00:00' AND order_ts < {T} '2026-03-05 00:00:00'")
spark.sql(f"INSERT INTO t_meta SELECT * FROM orders WHERE order_ts >= {T} '2026-03-05 00:00:00' AND order_ts < {T} '2026-03-06 00:00:00'")

show(spark, "s1_snapshots", "SELECT committed_at, snapshot_id, parent_id, operation, regexp_extract(manifest_list, '(snap-[^/]*)$', 1) AS manifest_list FROM lab.db.t_meta.snapshots ORDER BY committed_at", truncate=40)
show(spark, "s2_all_manifests", "SELECT reference_snapshot_id AS snap, regexp_extract(path, '([^/]*)$', 1) AS manifest, added_data_files_count AS added, existing_data_files_count AS existing, added_snapshot_id AS added_by FROM lab.db.t_meta.all_manifests ORDER BY snap, added_by", truncate=48, n=40)
show(spark, "s3_metadata_log", "SELECT regexp_extract(file, '([^/]*)$', 1) AS metadata_file, latest_sequence_number AS seq FROM lab.db.t_meta.metadata_log_entries", truncate=60)
show(spark, "s4_entries", "SELECT status, sequence_number, file_sequence_number, data_file.record_count AS rows FROM lab.db.t_meta.entries ORDER BY sequence_number, rows", n=12)

# time travel
snaps = [r.snapshot_id for r in spark.sql("SELECT snapshot_id FROM lab.db.t_meta.snapshots ORDER BY committed_at").collect()]
counts = []
for sid in snaps:
    counts.append(spark.sql(f"SELECT count(*) FROM t_meta VERSION AS OF {sid}").collect()[0][0])
counts.append(spark.sql("SELECT count(*) FROM t_meta").collect()[0][0])
res["time_travel_counts"] = counts
print("time travel counts per snapshot, then current:", counts)

# one row to delete
victim = spark.sql("SELECT order_id FROM t_meta WHERE order_ts >= TIMESTAMP '2026-03-02 00:00:00' LIMIT 1").collect()[0][0]
before_files = spark.sql("SELECT count(*) AS n, sum(file_size_in_bytes) AS b FROM lab.db.t_meta.files").collect()[0]
# --- copy-on-write (the default) ---------------------------------------------------------------------------------------
spark.sql(f"DELETE FROM t_meta WHERE order_id = '{victim}'")
show(spark, "s5_after_cow_delete", "SELECT snapshot_id, operation, summary['added-data-files'] AS added_files, summary['deleted-data-files'] AS deleted_files, summary['added-files-size'] AS added_bytes, summary['added-delete-files'] AS added_delete_files FROM lab.db.t_meta.snapshots ORDER BY committed_at DESC LIMIT 1", truncate=30)
show(spark, "s6_files_after_cow", "SELECT content, count(*) AS files, round(sum(file_size_in_bytes)/1e6,1) AS mb FROM lab.db.t_meta.files GROUP BY content ORDER BY content")
# --- merge-on-read ---------------------------------------------------------------------------------------------------------------------------
spark.sql("ALTER TABLE t_meta SET TBLPROPERTIES ('write.delete.mode'='merge-on-read','write.update.mode'='merge-on-read','write.merge.mode'='merge-on-read')")
victim2 = spark.sql("SELECT order_id FROM t_meta WHERE order_ts >= TIMESTAMP '2026-03-02 00:00:00' LIMIT 1").collect()[0][0]
spark.sql(f"DELETE FROM t_meta WHERE order_id = '{victim2}'")
show(spark, "s7_after_mor_delete", "SELECT snapshot_id, operation, summary['added-data-files'] AS added_files, summary['added-delete-files'] AS added_delete_files, summary['added-position-delete-files'] AS pos_delete_files, summary['added-position-deletes'] AS pos_deletes, summary['added-files-size'] AS added_bytes FROM lab.db.t_meta.snapshots ORDER BY committed_at DESC LIMIT 1", truncate=30)
show(spark, "s8_files_after_mor", "SELECT content, count(*) AS files, round(sum(file_size_in_bytes)/1e6,3) AS mb FROM lab.db.t_meta.files GROUP BY content ORDER BY content")
show(spark, "s9_delete_file", "SELECT content, record_count, file_size_in_bytes, regexp_extract(file_path, '([^/]*)$', 1) AS f FROM lab.db.t_meta.delete_files", truncate=70)
show(spark, "s10_seq_numbers", "SELECT status, sequence_number, data_file.content AS content, data_file.record_count AS rows FROM lab.db.t_meta.entries ORDER BY sequence_number DESC, content LIMIT 6")
res["rows_after"] = spark.sql("SELECT count(*) FROM t_meta").collect()[0][0]
json.dump({k: v for k, v in res.items()}, open(f"{OUT}/spec_results.json", "w"), indent=1, default=str)
print("DONE")
