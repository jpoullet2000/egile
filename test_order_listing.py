#!/usr/bin/env python3
"""
Test the improved order listing functionality
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "chatbot-agent"))

from grok_agent import GrokEcommerceAgent


async def test_list_orders():
    """Test the improved order listing"""
    agent = GrokEcommerceAgent()

    try:
        await agent.start()
        print("✅ Agent started successfully")

        # Test list orders
        query = "show me recent orders"
        print(f"\n📝 Testing: '{query}'")

        response = await agent.process_message(query)

        print(f"\n📋 Response Type: {response.get('type')}")
        print(f"\n💬 Message:")
        print("-" * 80)
        print(response.get("message"))
        print("-" * 80)

        # Check if we got proper order details
        message = response.get("message", "")
        if "microphone Egile" in message and "Demo User" in message:
            print("\n✅ SUCCESS: Orders are showing proper customer and product names!")
        elif "Unknown" in message:
            print("\n⚠️  PARTIAL: Still showing some unknown values")
        else:
            print("\n❓ DIFFERENT: Response format changed")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        if agent.ecommerce_agent:
            await agent.stop()


if __name__ == "__main__":
    asyncio.run(test_list_orders())
