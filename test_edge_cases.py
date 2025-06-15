#!/usr/bin/env python3
"""
Test additional edge cases for stock updates
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
    return results[0]  # Return just Laptop Pro


async def test_edge_cases():
    """Test various edge cases for stock updates"""
    agent = GrokEcommerceAgent()

    try:
        await agent.start()
        print("✅ Agent started successfully")

        test_cases = [
            ("increase laptop stock by 5", "add", 5),
            ("add 10 to laptop stock", "add", 10),
            ("set laptop stock to 50", "set", 50),
            ("change laptop stock to 25", "set", 25),
            ("update stock laptop plus 7", "add", 7),
        ]

        # Set initial stock
        await agent.process_message("update stock laptop to 100")
        print("🔧 Set initial stock to 100")

        for i, (command, expected_op, amount) in enumerate(test_cases, 1):
            print(f"\n{'=' * 60}")
            print(f"TEST {i}: {command}")
            print(f"Expected operation: {expected_op}")
            print(f"{'=' * 60}")

            # Get stock before
            before_id, before_name, before_stock = check_laptop_stock()
            print(f"Before: {before_stock} units")

            # Execute command
            response = await agent.process_message(command)
            print(f"Response: {response.get('message', 'No message')}")

            # Get stock after
            after_id, after_name, after_stock = check_laptop_stock()
            print(f"After: {after_stock} units")

            # Validate result
            if expected_op == "add":
                expected_final = before_stock + amount
                print(f"Expected: {before_stock} + {amount} = {expected_final}")
            else:  # set
                expected_final = amount
                print(f"Expected: set to {amount}")

            if after_stock == expected_final:
                print("✅ PASSED")
            else:
                print("❌ FAILED")
                print(f"   Expected: {expected_final}, Got: {after_stock}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(test_edge_cases())
