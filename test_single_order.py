#!/usr/bin/env python3
"""
Quick test to verify order confirmation message format
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import from the chatbot-agent directory
sys.path.insert(0, str(project_root / "chatbot-agent"))
from grok_agent import GrokEcommerceAgent


async def test_single_order():
    """Test a single order creation to see the response format"""
    agent = GrokEcommerceAgent()

    try:
        await agent.start()
        print("✅ Agent started successfully")

        # Test simple order creation
        query = "create order for demo for 1 microphone"
        print(f"\n📝 Testing: '{query}'")

        response = await agent.process_message(query)

        print(f"\n📋 Response Type: {response.get('type')}")
        print(f"\n💬 Message:")
        print("-" * 50)
        print(response.get("message"))
        print("-" * 50)

        # Check if it's the detailed response we want
        message = response.get("message", "")
        if (
            "Order ID:" in message
            and "Customer:" in message
            and "Total Amount:" in message
        ):
            print("\n✅ SUCCESS: Detailed order confirmation provided!")
        elif "Operation completed successfully" in message:
            print("\n❌ ISSUE: Still getting generic confirmation message")
        else:
            print("\n⚠️  UNKNOWN: Different response format")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        if agent.ecommerce_agent:
            await agent.stop()


if __name__ == "__main__":
    asyncio.run(test_single_order())
