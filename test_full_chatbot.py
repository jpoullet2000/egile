#!/usr/bin/env python3
"""Test full chatbot order creation"""

import asyncio
import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "chatbot-agent"))

from grok_agent import GrokEcommerceAgent


async def test_full_order_creation():
    """Test full order creation flow"""
    agent = GrokEcommerceAgent()

    try:
        print("🚀 Testing Full Chatbot Order Creation")
        print("=" * 50)

        await agent.start()

        # Test the original failing message
        test_message = "create order for demo for 2 laptops"
        print(f"\n📝 Testing: '{test_message}'")

        response = await agent.process_message(test_message)
        print(f"Response Type: {response.get('type')}")
        print(f"Message: {response.get('message')}")

        # Check if an order was actually created
        if "error" not in response.get("message", "").lower():
            print("✅ Success! No error in response")

            # Let's check if order was created by listing orders
            orders_response = await agent.process_message("show me orders")
            print(f"\nOrders check: {orders_response.get('type')}")
            if "order_" in orders_response.get("message", ""):
                print("✅ Order appears to be created!")
            else:
                print("❌ No orders found")
        else:
            print("❌ Still getting error!")

        # Test with microphone
        print(f"\n📝 Testing: 'create order for demo for 1 microphone'")
        mic_response = await agent.process_message(
            "create order for demo for 1 microphone"
        )
        print(f"Microphone order: {mic_response.get('message')}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()

    finally:
        await agent.stop()
        print("\n🏁 Test completed!")


if __name__ == "__main__":
    asyncio.run(test_full_order_creation())
