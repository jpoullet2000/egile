#!/usr/bin/env python3
"""
Test the exact command from user's issue: "update laptop Pro by 20"
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


async def test_exact_user_command():
    """Test the exact command from user's issue"""
    agent = GrokEcommerceAgent()

    try:
        await agent.start()
        print("✅ Agent started successfully")

        # First, let's set the laptop stock to 10 to match the user's scenario
        print("\n🔧 Setting up initial state (stock = 10)...")
        setup_response = await agent.process_message("update stock laptop to 10")
        print(f"Setup result: {setup_response.get('message', 'No message')}")

        # Check initial stock
        before_stock = check_laptop_stock()
        print("\n📊 Initial Stock (should be 10):")
        for prod_id, name, stock in before_stock:
            print(f"  • {name} ({prod_id}): {stock} units")

        # Test the exact command from user's issue
        print("\n" + "=" * 60)
        print("TESTING USER'S EXACT COMMAND")
        print("=" * 60)

        command = "update laptop Pro by 20"
        print(f"\n🔍 Testing: '{command}'")
        print("Expected result: 10 + 20 = 30 units")

        response = await agent.process_message(command)
        print(f"📋 Response: {response.get('message', 'No message')}")

        # Check final stock
        after_stock = check_laptop_stock()
        print("\n📊 Final Stock:")
        for prod_id, name, stock in after_stock:
            print(f"  • {name} ({prod_id}): {stock} units")

        # Verify the result
        laptop_pro_before = before_stock[0][2]  # Laptop Pro is first result
        laptop_pro_after = after_stock[0][2]
        expected_after = laptop_pro_before + 20

        print("\n" + "=" * 60)
        print("RESULT ANALYSIS")
        print("=" * 60)
        print(f"Before 'by 20': {laptop_pro_before} units")
        print(f"After 'by 20': {laptop_pro_after} units")
        print(f"Expected: {expected_after} units")
        print(f"Actual change: {laptop_pro_after - laptop_pro_before}")

        if laptop_pro_after == expected_after:
            print("🎉 SUCCESS: Stock was correctly incremented by 20!")
        else:
            print("❌ FAILED: Stock was not incremented correctly")
            if laptop_pro_after == 20:
                print("   (Stock was set to 20 instead of incremented by 20)")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(test_exact_user_command())
