#!/usr/bin/env python3
"""
Test price range functionality end-to-end with the Grok agent
"""

import asyncio
import sys

sys.path.append("/home/jbp/projects/egile/chatbot-agent")

from grok_agent import GrokEcommerceAgent


async def test_end_to_end():
    """Test price range functionality end-to-end"""
    agent = GrokEcommerceAgent()

    try:
        await agent.start()
        print("🚀 Testing end-to-end price range functionality...")

        # Test the fallback intent analysis directly
        print("\n📝 Testing fallback intent analysis:")
        intent1 = await agent.fallback_intent_analysis(
            "what are the products between $10 and $30"
        )
        print(f"Intent for '$10-$30': {intent1}")

        intent2 = await agent.fallback_intent_analysis("show me products under $50")
        print(f"Intent for 'under $50': {intent2}")

        intent3 = await agent.fallback_intent_analysis("products over $100")
        print(f"Intent for 'over $100': {intent3}")

        # Test the full chatbot response
        print("\n📝 Testing full chatbot responses:")

        print("\n1. Testing: 'what are the products between $10 and $30'")
        result1 = await agent.process_message(
            "what are the products between $10 and $30"
        )
        print(f"Result: {result1.get('success', False)}")
        if result1.get("message"):
            # Print first 200 chars of the message
            message = result1["message"]
            print(f"Message preview: {message[:200]}...")

        print("\n✅ End-to-end testing completed!")

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(test_end_to_end())
