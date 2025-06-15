#!/usr/bin/env python3
"""
Test the update_stock functionality with the parameter fix
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "chatbot-agent"))

from grok_agent import GrokEcommerceAgent


async def test_update_stock():
    """Test updating stock for Laptop Pro"""
    agent = GrokEcommerceAgent()

    try:
        await agent.start()
        print("✅ Agent started successfully")

        # Test update stock
        queries = [
            "update stock for laptop pro to 10",
            "set laptop pro stock to 5",
            "change laptop stock to 15",
        ]

        for query in queries:
            print(f"\n📝 Testing: '{query}'")

            response = await agent.process_message(query)

            print(f"Response Type: {response.get('type')}")
            print(f"Message: {response.get('message')}")

            # Check if we got a success message or error
            message = response.get("message", "")
            if "Error:" in message or "unexpected keyword argument" in message:
                print("❌ STILL FAILING: Parameter error persists")
            elif "success" in message.lower() or "updated" in message.lower():
                print("✅ SUCCESS: Stock update worked!")
            else:
                print("⚠️  UNKNOWN: Different response format")

            print("-" * 60)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        if agent.ecommerce_agent:
            await agent.stop()


if __name__ == "__main__":
    asyncio.run(test_update_stock())
