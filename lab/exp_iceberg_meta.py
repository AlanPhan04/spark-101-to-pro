"""Chapter 12, part 1: what the Iceberg metadata tables show for the lab's orders table."""
from labutil import session, show

spark = session("exp-iceberg-meta")
show(spark, "m1_files_summary",
     "SELECT count(*) AS files, round(avg(file_size_in_bytes)/1e6,1) AS avg_mb, min(record_count) AS min_rows, max(record_count) AS max_rows, sum(record_count) AS rows FROM lab.db.orders.files")
show(spark, "m2_partitions",
     "SELECT partition, record_count, file_count FROM lab.db.orders.partitions ORDER BY partition LIMIT 5")
show(spark, "m3_manifests",
     "SELECT path, length, partition_spec_id, added_data_files_count, existing_data_files_count, deleted_data_files_count FROM lab.db.orders.manifests", truncate=50)
show(spark, "m4_snapshots", "SELECT snapshot_id, operation, summary['added-data-files'] AS added, summary['total-data-files'] AS total FROM lab.db.orders.snapshots", truncate=40)
show(spark, "m5_file_bounds",
     "SELECT file_path, record_count, readable_metrics.order_id.lower_bound AS oid_lo, readable_metrics.order_id.upper_bound AS oid_hi, readable_metrics.product_id.lower_bound AS pid_lo, readable_metrics.product_id.upper_bound AS pid_hi, readable_metrics.order_ts.lower_bound AS ts_lo FROM lab.db.orders.files ORDER BY file_path LIMIT 3", truncate=44, vertical=True)
show(spark, "m6_dim_files", "SELECT count(*) AS files, round(sum(file_size_in_bytes)/1e6,1) AS mb FROM lab.db.dim_product.files")
print("DONE")
