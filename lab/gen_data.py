"""Generate the book's running example (orders star schema) into a local Iceberg warehouse.

Mirrors book/appendices/a-reference-environment.tex:
  orders        Iceberg, partitioned by days(order_ts), one month of rows, one viral hot product
  dim_product   small (broadcastable)
  dim_customer  large (not broadcast by default)
  dim_date      calendar attributes

Usage (inside the container, see run.sh):  gen_data.py [orders_rows]
"""
import sys

from pyspark.sql import SparkSession, functions as F

N_ORDERS = int(sys.argv[1]) if len(sys.argv) > 1 else 30_000_000
N_PRODUCTS = 50_000
N_CUSTOMERS = 2_000_000
HOT_PRODUCT = "p000042"      # the viral, heavily discounted item
MARCH_1 = 1772323200        # 2026-03-01 00:00:00 UTC, epoch seconds
HOT_SHARE = 0.30             # share of orders that hit the hot product

spark = (SparkSession.builder.appName("gen-data")
    .config("spark.sql.session.timeZone", "UTC").getOrCreate())
spark.sql("CREATE NAMESPACE IF NOT EXISTS lab.db")

categories = ["books", "toys", "garden", "grocery", "beauty", "sports", "pets", "tools",
              "music", "movies", "office", "baby", "auto", "health", "home", "kitchen",
              "shoes", "jewelry", "games", "outdoor"]
cat_arr = F.array(*[F.lit(c) for c in categories])

# dim_product -----------------------------------------------------------------------------
dim_product = (spark.range(N_PRODUCTS)
    .select(F.format_string("p%06d", F.col("id").cast("int")).alias("product_id"),
            cat_arr[(F.col("id") % len(categories)).cast("int")].alias("category"),
            F.round(F.rand(1) * 200 + 5, 2).alias("list_price")))
dim_product.writeTo("lab.db.dim_product").using("iceberg").createOrReplace()

# dim_customer ------------------------------------------------------------------------------
segments = F.array(F.lit("bronze"), F.lit("silver"), F.lit("gold"), F.lit("platinum"))
dim_customer = (spark.range(N_CUSTOMERS)
    .select(F.format_string("c%08d", F.col("id").cast("int")).alias("customer_id"),
            F.date_add(F.lit("2020-01-01").cast("date"), (F.rand(2) * 2000).cast("int")).alias("signup_date"),
            segments[(F.rand(3) * 4).cast("int")].alias("segment"),
            F.sha2(F.col("id").cast("string"), 256).alias("profile_hash")))
dim_customer.writeTo("lab.db.dim_customer").using("iceberg").createOrReplace()

# dim_date -----------------------------------------------------------------------------------
dim_date = (spark.range(365)
    .select(F.date_add(F.lit("2026-01-01").cast("date"), F.col("id").cast("int")).alias("date"))
    .select("date", F.year("date").alias("year"), F.month("date").alias("month"),
            F.date_format("date", "E").alias("day_of_week")))
dim_date.writeTo("lab.db.dim_date").using("iceberg").createOrReplace()

# orders ---------------------------------------------------------------------------------------
promised = (F.rand(4) * 6 + 1).cast("int")
orders = (spark.range(N_ORDERS)
    .select(F.expr("uuid()").alias("order_id"),
            F.timestamp_seconds(F.lit(MARCH_1) + (F.rand(5) * 31 * 86400).cast("long")).alias("order_ts"),
            F.when(F.rand(6) < HOT_SHARE, F.lit(HOT_PRODUCT))
             .otherwise(F.format_string("p%06d", (F.rand(7) * N_PRODUCTS).cast("int"))).alias("product_id"),
            F.format_string("c%08d", (F.rand(8) * N_CUSTOMERS).cast("int")).alias("customer_id"),
            promised.alias("promised_days"))
    .withColumn("delivery_days", F.greatest(F.lit(1), F.col("promised_days") + (F.rand(9) * 5 - 2).cast("int")))
    .withColumn("order_total", F.round(F.rand(10) * 300 + 5, 2)))

(orders.writeTo("lab.db.orders").using("iceberg")
    .partitionedBy(F.days("order_ts"))
    .tableProperty("write.spark.fanout.enabled", "true")
    .createOrReplace())

for t in ["orders", "dim_product", "dim_customer", "dim_date"]:
    n = spark.table(f"lab.db.{t}").count()
    print(f"ROWS {t} = {n}")
print("DONE")
