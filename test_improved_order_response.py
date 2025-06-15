#!/usr/bin/env python3
"""Test the enhanced order creation response"""

import asyncio
import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "chatbot-agent"))

from grok_agent import GrokEcommerceAgent


async def test_order_response():
    """Test the enhanced order creation response"""
    agent = GrokEcommerceAgent()

    try:
        print("🧪 Testing Enhanced Order Creation Response")
        print("=" * 50)

        await agent.start()

        # Test order creation with the new response format
        test_message = "create order for demo for 1 microphone"
        print(f"\n📝 Testing: '{test_message}'")

        response = await agent.process_message(test_message)
        print(f"\nResponse Type: {response.get('type')}")
        print(f"\nMessage:\n{response.get('message')}")

        # Test with laptops too
        print(f"\n" + "=" * 50)
        test_message2 = "create order for demo for 2 laptops"
        print(f"\n📝 Testing: '{test_message2}'")

        response2 = await agent.process_message(test_message2)
        print(f"\nResponse Type: {response2.get('type')}")
        print(f"\nMessage:\n{response2.get('message')}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()

    finally:
        await agent.stop()
        print("\n🏁 Test completed!")


if __name__ == "__main__":
    asyncio.run(test_order_response())
