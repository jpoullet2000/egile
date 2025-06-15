#!/usr/bin/env python3
"""
Test the BY vs TO operation detection for stock updates
"""

import asyncio
import sys
import sqlite3
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "chatbot-agent"))

from grok_agent import GrokEcommerceAgent


def check_laptop_stock():
    """Check current laptop stock in database"""
    conn = sqlite3.connect("/home/jbp/projects/egile/ecommerce.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, stock_quantity FROM products WHERE id = 'prod_000004'"
    )
    result = cursor.fetchone()
    conn.close()
    return result


async def test_by_vs_to_operations():
    """Test BY (add) vs TO (set) operations"""
    agent = GrokEcommerceAgent()

    try:
        await agent.start()
        print("✅ Agent started successfully")

        # Reset stock to a known value first
        print("\n🔄 Setting initial stock to 10...")
        await agent.process_message("update laptop stock to 10")

        prod_id, name, initial_stock = check_laptop_stock()
        print(f"📊 Initial: {name} has {initial_stock} units")

        # Test 1: "BY" operation (should ADD to existing stock)
        print(
            f"\n🧪 Test 1: 'update laptop by 5' (should add 5 to {initial_stock} = {initial_stock + 5})"
        )
        response1 = await agent.process_message("update laptop by 5")
        prod_id, name, stock_after_by = check_laptop_stock()

        print(f"📋 Response: {response1.get('message')}")
        print(f"📊 Result: {stock_after_by} units")
        print(
            f"✅ Expected: {initial_stock + 5}, Got: {stock_after_by} - {'CORRECT' if stock_after_by == initial_stock + 5 else 'WRONG'}"
        )

        # Test 2: "TO" operation (should SET to specific value)
        print(f"\n🧪 Test 2: 'update laptop to 25' (should set to 25)")
        response2 = await agent.process_message("update laptop to 25")
        prod_id, name, stock_after_to = check_laptop_stock()

        print(f"📋 Response: {response2.get('message')}")
        print(f"📊 Result: {stock_after_to} units")
        print(
            f"✅ Expected: 25, Got: {stock_after_to} - {'CORRECT' if stock_after_to == 25 else 'WRONG'}"
        )

        # Test 3: "BY" operation again (should ADD to current stock)
        print(
            f"\n🧪 Test 3: 'increase laptop stock by 10' (should add 10 to {stock_after_to} = {stock_after_to + 10})"
        )
        response3 = await agent.process_message("increase laptop stock by 10")
        prod_id, name, final_stock = check_laptop_stock()

        print(f"📋 Response: {response3.get('message')}")
        print(f"📊 Result: {final_stock} units")
        print(
            f"✅ Expected: {stock_after_to + 10}, Got: {final_stock} - {'CORRECT' if final_stock == stock_after_to + 10 else 'WRONG'}"
        )

        print(f"\n{'=' * 60}")
        print("📊 SUMMARY:")
        print(f"Initial stock: {initial_stock}")
        print(f"After 'by 5': {stock_after_by} (should be {initial_stock + 5})")
        print(f"After 'to 25': {stock_after_to} (should be 25)")
        print(f"After 'by 10': {final_stock} (should be {stock_after_to + 10})")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        if agent.ecommerce_agent:
            await agent.stop()


if __name__ == "__main__":
    asyncio.run(test_by_vs_to_operations())
