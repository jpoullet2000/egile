#!/usr/bin/env python3
"""
Test both "by" (add) and "to" (set) stock operations
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
        "SELECT id, name, stock_quantity FROM products WHERE name LIKE '%Laptop%'"
    )
    results = cursor.fetchall()
    conn.close()
    return results


async def test_stock_operations():
    """Test both 'by' and 'to' operations"""
    agent = GrokEcommerceAgent()

    try:
        await agent.start()
        print("✅ Agent started successfully")

        # Test 1: "by" operation (should increment)
        print("\n" + "=" * 60)
        print("TEST 1: INCREMENT OPERATION ('by')")
        print("=" * 60)

        # Check initial stock
        before_stock = check_laptop_stock()
        print("\n📊 Initial Stock:")
        for prod_id, name, stock in before_stock:
            print(f"  • {name} ({prod_id}): {stock} units")

        # Test increment by 15
        command1 = "update stock laptop by 15"
        print(f"\n🔍 Testing: '{command1}'")
        response1 = await agent.process_message(command1)
        print(f"📋 Response: {response1.get('message', 'No message')}")

        # Check stock after increment
        after_increment = check_laptop_stock()
        print("\n📊 Stock After Increment:")
        for prod_id, name, stock in after_increment:
            print(f"  • {name} ({prod_id}): {stock} units")

        # Test 2: "to" operation (should set)
        print("\n" + "=" * 60)
        print("TEST 2: SET OPERATION ('to')")
        print("=" * 60)

        # Test set to 100
        command2 = "update stock laptop to 100"
        print(f"\n🔍 Testing: '{command2}'")
        response2 = await agent.process_message(command2)
        print(f"📋 Response: {response2.get('message', 'No message')}")

        # Check final stock
        final_stock = check_laptop_stock()
        print("\n📊 Final Stock:")
        for prod_id, name, stock in final_stock:
            print(f"  • {name} ({prod_id}): {stock} units")

        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Test 1 - Before 'by 15': {before_stock[0][2]} units")
        print(f"Test 1 - After 'by 15': {after_increment[0][2]} units")
        print(
            f"Expected change: +15, Actual change: {after_increment[0][2] - before_stock[0][2]}"
        )
        print(
            f"✅ Increment test: {'PASSED' if (after_increment[0][2] - before_stock[0][2]) == 15 else 'FAILED'}"
        )

        print(f"\nTest 2 - Before 'to 100': {after_increment[0][2]} units")
        print(f"Test 2 - After 'to 100': {final_stock[0][2]} units")
        print(f"Expected final: 100, Actual final: {final_stock[0][2]}")
        print(f"✅ Set test: {'PASSED' if final_stock[0][2] == 100 else 'FAILED'}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(test_stock_operations())
