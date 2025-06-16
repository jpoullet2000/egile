#!/usr/bin/env python3
"""
Test multiple gaming headset pro orders to ensure consistency.
"""

import asyncio
import sys

sys.path.append("/home/jbp/projects/egile/chatbot-agent")
from grok_agent import GrokEcommerceAgent


async def test_multiple_orders():
    agent = GrokEcommerceAgent()
    await agent.start()

    try:
        test_commands = [
            "create order for 2 gaming headset pro for demo user",
            "create order for 1 gaming_headset_pro for demo",
            "order 3 gaming headset pro for demo customer",
            "place order: 1 gaming headset pro for demo",
        ]

        for i, command in enumerate(test_commands, 1):
            print(f"\n🧪 Test {i}: '{command}'")
            response = await agent.process_message(command)

            message = response.get("message", "")
            intent = response.get("intent", {})
            params = intent.get("parameters", {})

            # Check if order succeeded
            if "Order Created Successfully" in message and "order_" in message:
                print("   ✅ Order created successfully")

                # Extract product ID from parameters
                items = params.get("items", [])
                if items and items[0].get("product_id") == "prod_000009":
                    print("   ✅ Product mapped correctly to prod_000009")
                else:
                    print(f"   ❌ Product mapping issue: {items}")

            elif "Product not found" in message:
                print("   ❌ Product not found error")
                print(f"   Items: {params.get('items', [])}")
            else:
                print(f"   ⚠️ Unexpected response: {message[:100]}...")

    finally:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(test_multiple_orders())
