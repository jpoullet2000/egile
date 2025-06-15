#!/usr/bin/env python3
"""
Test the specific command that was failing
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
    cursor.execute("SELECT name, stock_quantity FROM products WHERE id = 'prod_000004'")
    result = cursor.fetchone()
    conn.close()
    return result


async def test_specific_command():
    """Test the specific failing command"""
    agent = GrokEcommerceAgent()

    try:
        await agent.start()
        print("✅ Agent started successfully")

        # Check initial stock
        name, stock = check_laptop_stock()
        print(f"\n📊 Before: {name} has {stock} units")

        # Test the exact command that was failing
        command = "update stock laptop by 10"
        print(f"\n📝 Testing: '{command}'")

        response = await agent.process_message(command)
        print(f"Response: {response.get('message')}")

        # Check final stock
        name, stock = check_laptop_stock()
        print(f"\n📊 After: {name} has {stock} units")

        print("\n✅ SUCCESS: Stock update is now working!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        if agent.ecommerce_agent:
            await agent.stop()


if __name__ == "__main__":
    asyncio.run(test_specific_command())
