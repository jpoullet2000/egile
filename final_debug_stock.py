#!/usr/bin/env python3
"""
Debug the stock update issue by testing step by step
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


async def debug_stock_update():
    """Debug the stock update issue"""
    agent = GrokEcommerceAgent()

    try:
        await agent.start()
        print("✅ Agent started successfully")

        # Check initial stock
        print("\n📊 Initial Stock:")
        for prod_id, name, stock in check_laptop_stock():
            print(f"  • {name} ({prod_id}): {stock} units")

        # Test the failing command with detailed logging
        command = "update stock laptop by 10"
        print(f"\n🔍 Testing: '{command}'")
        print("=" * 60)

        # Get stock before
        before_stock = check_laptop_stock()

        # Execute command
        response = await agent.process_message(command)

        # Get stock after
        after_stock = check_laptop_stock()

        print(f"\n📋 Response: {response.get('message')}")
        print(f"📋 Response Type: {response.get('type')}")

        print("\n📊 Stock Comparison:")
        print("Before:")
        for prod_id, name, stock in before_stock:
            print(f"  • {name} ({prod_id}): {stock} units")

        print("After:")
        for prod_id, name, stock in after_stock:
            print(f"  • {name} ({prod_id}): {stock} units")

        if before_stock != after_stock:
            print("\n✅ SUCCESS: Stock was updated!")
        else:
            print("\n❌ PROBLEM: Stock was NOT updated!")
            print("\n🔧 Debugging info:")
            if "action_result" in response:
                print(f"Action result: {response['action_result']}")
            if "intent" in response:
                print(f"Intent: {response['intent']}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        if agent.ecommerce_agent:
            await agent.stop()


if __name__ == "__main__":
    asyncio.run(debug_stock_update())
