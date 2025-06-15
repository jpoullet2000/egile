#!/usr/bin/env python3
"""
Test different stock update syntaxes to debug the issue
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
        "SELECT name, stock_quantity FROM products WHERE name LIKE '%Laptop%'"
    )
    results = cursor.fetchall()
    conn.close()
    return results


async def test_stock_update_syntax():
    """Test different stock update syntaxes"""
    agent = GrokEcommerceAgent()

    try:
        await agent.start()
        print("✅ Agent started successfully")

        # Check initial stock
        print("\n📊 Initial Laptop Stock:")
        for name, stock in check_laptop_stock():
            print(f"  • {name}: {stock} units")

        # Test different syntaxes
        test_commands = [
            "update stock laptop by 5",  # increment by 5
            "set laptop stock to 20",  # set to 20
            "increase laptop stock by 3",  # increment by 3
            "update laptop pro stock to 25",  # set to 25
        ]

        for i, command in enumerate(test_commands, 1):
            print(f"\n{'=' * 60}")
            print(f"Test {i}: '{command}'")
            print("=" * 60)

            # Get stock before
            before_stock = check_laptop_stock()
            print("Stock before:")
            for name, stock in before_stock:
                print(f"  • {name}: {stock} units")

            # Execute command
            response = await agent.process_message(command)
            print(f"\nResponse: {response.get('message')}")

            # Get stock after
            after_stock = check_laptop_stock()
            print("\nStock after:")
            for name, stock in after_stock:
                print(f"  • {name}: {stock} units")

            # Check if stock changed
            if before_stock != after_stock:
                print("✅ Stock was updated!")
            else:
                print("❌ Stock was NOT updated!")

            # Small delay between tests
            await asyncio.sleep(1)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        if agent.ecommerce_agent:
            await agent.stop()


if __name__ == "__main__":
    asyncio.run(test_stock_update_syntax())
