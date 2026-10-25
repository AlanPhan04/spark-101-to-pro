"""Free disk: drop the large derived tables of earlier experiments (their scripts recreate them)."""
from labutil import session

spark = session("cleanup")
for t in ("orders_b", "orders_d", "orders_inc", "dim_customer_b", "t_race_r4", "t_race_r0", "t_meta"):
    spark.sql(f"DROP TABLE IF EXISTS {t} PURGE")
print("DONE")
