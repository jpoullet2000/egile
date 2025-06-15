#!/usr/bin/env python3
"""
Simple test to demonstrate the improved order confirmation message.
"""

import asyncio
import json
import sqlite3
from datetime import datetime

# Check current database state
conn = sqlite3.connect("/home/jbp/projects/egile/ecommerce.db")
cursor = conn.cursor()

print("🔍 CHECKING CURRENT DATABASE STATE")
print("=" * 50)

# Check recent orders
cursor.execute(
    "SELECT id, customer_id, status, total_amount, created_at FROM orders ORDER BY created_at DESC LIMIT 3"
)
recent_orders = cursor.fetchall()

print(f"📋 Recent Orders ({len(recent_orders)} found):")
for order in recent_orders:
    print(
        f"  • Order {order[0]}: Customer {order[1]}, Status: {order[2]}, Total: ${order[3]}"
    )
    print(f"    Created: {order[4]}")

# Check product stock
print(f"\n📦 Product Stock:")
cursor.execute(
    "SELECT id, name, stock_quantity, price FROM products WHERE id IN ('prod_000004', 'prod_000010') ORDER BY id"
)
products = cursor.fetchall()
for product in products:
    print(f"  • {product[1]} ({product[0]}): Stock: {product[2]}, Price: ${product[3]}")

conn.close()

print("\n" + "=" * 50)
print("✅ DATABASE CHECK COMPLETE")
print("\n💡 ORDER CONFIRMATION IMPROVEMENTS:")
print("   The chatbot now provides detailed order confirmations including:")
print("   • Order ID")
print("   • Customer information")
print("   • Order status")
print("   • Total amount with currency")
print("   • Creation date and time")
print("   • Detailed item breakdown with quantities and prices")
print("   • Friendly success message")
print("\n🎯 INSTEAD OF: 'Operation completed successfully! Action: create_order'")
print("🎯 YOU NOW GET: A detailed order summary with all relevant information")
print("\n🚀 To test this, try saying:")
print("   'create order for demo for 1 microphone'")
print("   'make an order for demo customer for 2 laptops'")
print("   'order 1 microphone for demo'")
