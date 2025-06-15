#!/usr/bin/env python3
"""
Test the specific issue: updating "Test Laptop" should not update "Laptop Pro"
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


def check_all_laptop_stock():
    """Check current stock for all laptop products"""
    conn = sqlite3.connect("/home/jbp/projects/egile/ecommerce.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, stock_quantity FROM products WHERE name LIKE '%laptop%' OR name LIKE '%Laptop%'"
    )
    results = cursor.fetchall()
    conn.close()
    return results


async def test_specific_product_update():
    """Test updating Test Laptop specifically"""
    agent = GrokEcommerceAgent()

    try:
        await agent.start()
        print("✅ Agent started successfully")

        # Set initial stock for both laptops to known values
        print("\n🔧 Setting up initial state...")
        await agent.process_message("update stock laptop pro to 100")
        await agent.process_message("update stock test laptop to 50")

        # Check initial stock
        before_stock = check_all_laptop_stock()
        print("\n📊 Initial Stock:")
        for prod_id, name, stock in before_stock:
            print(f"  • {name} ({prod_id}): {stock} units")

        # Test the user's exact command
        print("\n" + "=" * 60)
        print('TESTING: update stock of "Test Laptop" by 10')
        print("Expected: Test Laptop should go from 50 to 60")
        print("Expected: Laptop Pro should remain at 100")
        print("=" * 60)

        command = 'update stock of "Test Laptop" by 10'
        response = await agent.process_message(command)
        print(f"\n📋 Response: {response.get('message', 'No message')}")

        # Check final stock
        after_stock = check_all_laptop_stock()
        print("\n📊 Final Stock:")
        for prod_id, name, stock in after_stock:
            print(f"  • {name} ({prod_id}): {stock} units")

        # Analyze results
        print("\n" + "=" * 60)
        print("RESULT ANALYSIS")
        print("=" * 60)

        # Find the specific products
        laptop_pro_before = next(
            (stock for pid, name, stock in before_stock if "Laptop Pro" in name), None
        )
        laptop_pro_after = next(
            (stock for pid, name, stock in after_stock if "Laptop Pro" in name), None
        )
        test_laptop_before = next(
            (stock for pid, name, stock in before_stock if "Test Laptop" in name), None
        )
        test_laptop_after = next(
            (stock for pid, name, stock in after_stock if "Test Laptop" in name), None
        )

        print(f"Laptop Pro - Before: {laptop_pro_before}, After: {laptop_pro_after}")
        print(f"Test Laptop - Before: {test_laptop_before}, After: {test_laptop_after}")

        # Check if Test Laptop was updated correctly
        if test_laptop_after == test_laptop_before + 10:
            print("✅ SUCCESS: Test Laptop was correctly updated (+10)")
        else:
            print("❌ FAILED: Test Laptop was not updated correctly")

        # Check if Laptop Pro remained unchanged
        if laptop_pro_after == laptop_pro_before:
            print("✅ SUCCESS: Laptop Pro was not affected")
        else:
            print("❌ FAILED: Laptop Pro was incorrectly updated")

        # Overall result
        if (test_laptop_after == test_laptop_before + 10) and (
            laptop_pro_after == laptop_pro_before
        ):
            print("\n🎉 OVERALL: PERFECT! The fix is working correctly!")
        else:
            print("\n❌ OVERALL: Still needs work")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(test_specific_product_update())
