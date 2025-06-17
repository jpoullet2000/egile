#!/usr/bin/env python3
"""
Test product details functionality with case-insensitive search
"""

import asyncio
import sys

sys.path.append("/home/jbp/projects/egile/chatbot-agent")

from grok_agent import GrokEcommerceAgent


async def test_product_details():
    """Test product details functionality"""
    agent = GrokEcommerceAgent()

    try:
        await agent.start()
        print("🚀 Testing product details functionality...")

        # Test the fallback intent analysis directly
        print("\n📝 Testing fallback intent analysis:")
        intent1 = await agent.fallback_intent_analysis(
            "show me the details for USB Drive"
        )
        print(f"Intent for 'USB Drive': {intent1}")

        intent2 = await agent.fallback_intent_analysis(
            "show me the details for usb drive"
        )
        print(f"Intent for 'usb drive': {intent2}")

        intent3 = await agent.fallback_intent_analysis("details for USB drive")
        print(f"Intent for 'USB drive': {intent3}")

        # Test the full chatbot response
        print("\n📝 Testing full chatbot responses:")

        print("\n1. Testing: 'show me the details for USB Drive'")
        result1 = await agent.process_message("show me the details for USB Drive")
        print(f"Result: {result1.get('success', False)}")
        if result1.get("message"):
            message = result1["message"]
            print(f"Message preview: {message[:200]}...")

        print("\n2. Testing: 'show me the details for usb drive'")
        result2 = await agent.process_message("show me the details for usb drive")
        print(f"Result: {result2.get('success', False)}")
        if result2.get("message"):
            message = result2["message"]
            print(f"Message preview: {message[:200]}...")

        print("\n✅ Product details testing completed!")

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(test_product_details())
