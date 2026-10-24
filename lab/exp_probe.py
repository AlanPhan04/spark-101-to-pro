from labutil import run, session
spark = session("exp-probe")
Q = """SELECT p.category, count(*) AS orders
       FROM orders o JOIN dim_product p ON o.product_id = p.product_id
       WHERE o.order_ts >= TIMESTAMP '2026-03-01 00:00:00' AND o.order_ts < TIMESTAMP '2026-03-08 00:00:00'
         AND p.category = 'books'
       GROUP BY p.category"""
run(spark, "x1_filtered_defaults", Q)
print("DONE")
