#!/usr/bin/env python3
"""
Test the new dynamic product mapping system.
"""

import asyncio
import sys

sys.path.append("/home/jbp/projects/egile/chatbot-agent")
from grok_agent import GrokEcommerceAgent


async def test_dynamic_mapping():
    agent = GrokEcommerceAgent()
    await agent.start()

    try:
        print("🧪 Testing dynamic product mapping system...\n")

        # Test existing products
        test_commands = [
            "create order for 2 gaming headset pro for demo user",
            "create order for 1 laptop for demo",
            "order 2 microphone egile for demo customer",
            "place order: 1 test laptop for demo",
            "create order for 3 usb drive for demo user",
        ]

        for i, command in enumerate(test_commands, 1):
            print(f"🧪 Test {i}: '{command}'")
            response = await agent.process_message(command)

            message = response.get("message", "")
            intent = response.get("intent", {})
            params = intent.get("parameters", {})

            # Check if order succeeded
            if "Order Created Successfully" in message and "order_" in message:
                print("   ✅ Order created successfully")

                # Extract product ID from parameters
                items = params.get("items", [])
                if items and items[0].get("product_id", "").startswith("prod_"):
                    product_id = items[0].get("product_id")
                    quantity = items[0].get("quantity")
                    print(
                        f"   ✅ Product mapped to {product_id} (quantity: {quantity})"
                    )
                else:
                    print(f"   ❌ Product mapping issue: {items}")

            elif "Product not found" in message:
                print("   ❌ Product not found error")
                print(f"   Items: {params.get('items', [])}")
            else:
                print(f"   ⚠️ Unexpected response: {message[:100]}...")

            print()  # Empty line

        # Test the mapping function directly
        print("🔧 Testing dynamic mapping function directly...")
        test_terms = ["headset", "gaming headset pro", "laptop", "microphone"]

        for term in test_terms:
            mapped_id = await agent._get_dynamic_product_mapping(term)
            if mapped_id:
                print(f"   ✅ '{term}' → {mapped_id}")
            else:
                print(f"   ❌ '{term}' → No mapping found")

    finally:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(test_dynamic_mapping())
