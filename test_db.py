#!/usr/bin/env python3
import sqlite3
import sys
from pathlib import Path

# Test basic database connection
try:
    db_path = "/home/jbp/projects/egile/ecommerce.db"
    print(f"Testing database at: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get products
    cursor.execute("SELECT name, sku, price, stock_quantity FROM products LIMIT 2")
    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]

    print(f"Columns: {columns}")
    print(f"Number of rows: {len(rows)}")

    for i, row in enumerate(rows):
        print(f"Row {i}: {row}")
        row_dict = dict(zip(columns, row))
        print(f"Row dict {i}: {row_dict}")

    conn.close()
    print("Database test completed successfully")

except Exception as e:
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()
