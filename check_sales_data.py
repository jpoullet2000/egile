#!/usr/bin/env python3
import sqlite3
import json

# Check order items to understand sales data
conn = sqlite3.connect("/home/jbp/projects/egile/ecommerce.db")

print("=== ORDER ITEMS ANALYSIS ===")

# Get total quantity sold per product
cursor = conn.execute("""
    SELECT oi.product_id, p.name, SUM(oi.quantity) as total_sold, COUNT(DISTINCT oi.order_id) as order_count
    FROM order_items oi 
    LEFT JOIN products p ON oi.product_id = p.id
    GROUP BY oi.product_id 
    ORDER BY total_sold DESC
    LIMIT 10
""")

print("Most sold products by quantity:")
for row in cursor:
    product_id, product_name, total_sold, order_count = row
    print(
        f"  {product_name or 'Unknown'} ({product_id}): {total_sold} units in {order_count} orders"
    )

print("\n=== SAMPLE ORDER ITEMS ===")
cursor = conn.execute("SELECT order_id, product_id, quantity FROM order_items LIMIT 5")
for row in cursor:
    print(f"Order {row[0]}: Product {row[1]} - Qty: {row[2]}")

conn.close()
