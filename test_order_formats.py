#!/usr/bin/env python3
"""
Test different order creation formats.
"""

import asyncio
import sys

sys.path.append("/home/jbp/projects/egile/chatbot-agent")
from grok_agent import GrokEcommerceAgent


async def test_different_formats():
    agent = GrokEcommerceAgent()
    await agent.start()

    try:
        # Test different order formats
        test_commands = [
            "create order for 2 headset for demo",
            "create order: 2 headsets for demo customer",
            "create order customer demo items 2 headset",
            "place order for demo: 2 gaming headset pro",
            "order 2 headsets for demo user",
        ]

        for i, command in enumerate(test_commands, 1):
            print(f"\n🧪 Test {i}: '{command}'")
            response = await agent.process_message(command)

            intent = response.get("intent", {})
            params = intent.get("parameters", {})

            print(f"   Action: {intent.get('action', 'unknown')}")
            print(f"   Customer: {params.get('customer_id', 'none')}")
            print(f"   Items: {params.get('items', [])}")

            message = response.get("message", "")
            if "Order Created Successfully" in message:
                print("   ✅ Order created")
            elif "Order Creation Failed" in message:
                print("   ❌ Order failed")
            elif "Product not found" in message:
                print("   ⚠️ Product mapping issue")
            else:
                print(f"   📄 Response: {message[:100]}...")

    finally:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(test_different_formats())
