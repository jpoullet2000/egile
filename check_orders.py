#!/usr/bin/env python3
import sqlite3

# Check orders and stock
conn = sqlite3.connect("/home/jbp/projects/egile/ecommerce.db")

print("=== STOCK CHECK ===")
cursor = conn.execute(
    "SELECT name, stock_quantity FROM products WHERE id = 'prod_000010'"
)
for row in cursor:
    print(f"Product: {row[0]}, Stock: {row[1]}")

print("\n=== RECENT ORDERS ===")
cursor = conn.execute(
    "SELECT id, customer_id, total_amount, created_at FROM orders ORDER BY created_at DESC LIMIT 3"
)
for row in cursor:
    print(f"Order: {row[0]}, Customer: {row[1]}, Amount: ${row[2]}, Time: {row[3]}")

print("\n=== ORDER COUNT ===")
cursor = conn.execute("SELECT COUNT(*) FROM orders")
count = cursor.fetchone()[0]
print(f"Total orders: {count}")

conn.close()
