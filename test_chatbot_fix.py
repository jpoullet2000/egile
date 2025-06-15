#!/usr/bin/env python3
"""Test the order creation fix in the chatbot"""

import asyncio
import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "chatbot-agent"))

from grok_agent import GrokEcommerceAgent


async def test_chatbot_order_creation():
    """Test that the chatbot can handle order creation correctly"""
    agent = GrokEcommerceAgent()

    try:
        print("🚀 Testing Chatbot Order Creation Fix")
        print("=" * 50)

        # Start the agent
        await agent.start()

        # Test the order creation message that was failing
        test_message = "create order for demo for 2 laptops"
        print(f"\n📝 Testing message: '{test_message}'")

        # First, let's test the intent analysis
        intent_result = agent.fallback_intent_analysis(test_message)
        print(f"\n🔍 Intent Analysis Result:")
        print(f"Intent: {intent_result.get('intent')}")
        print(f"Action: {intent_result.get('action')}")
        print(f"Parameters: {intent_result.get('parameters')}")
        print(f"Requires Action: {intent_result.get('requires_action')}")

        # Test processing the full message
        print(f"\n🤖 Processing message through chatbot...")
        response = await agent.process_message(test_message)
        print(f"\nResponse Type: {response.get('type')}")
        print(f"Message: {response.get('message')}")

        if "error" in response.get("message", "").lower():
            print("❌ Still getting error!")
        else:
            print("✅ No error! The fix worked!")

    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback

        traceback.print_exc()

    finally:
        await agent.stop()
        print("\n🏁 Test completed!")


if __name__ == "__main__":
    asyncio.run(test_chatbot_order_creation())
