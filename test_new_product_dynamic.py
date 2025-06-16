#!/usr/bin/env python3
"""
Test that new products can be dynamically mapped after creation.
"""

import asyncio
import sys

sys.path.append("/home/jbp/projects/egile/chatbot-agent")
from grok_agent import GrokEcommerceAgent


async def test_new_product_mapping():
    agent = GrokEcommerceAgent()
    await agent.start()

    try:
        print("🧪 Testing new product creation and dynamic mapping...\n")

        # First, create a new product
        print("📦 Creating a new product...")
        create_response = await agent.process_message(
            "create product: name='Wireless Keyboard Pro', description='High-quality wireless keyboard', price=89.99, sku='WKB-PRO-001', category='Electronics', stock_quantity=50"
        )

        print(f"Create response: {create_response.get('message', '')[:100]}...")

        # Wait a moment for the product to be created
        await asyncio.sleep(1)

        # Now test if we can map to this new product
        print("\n🔍 Testing dynamic mapping for the new product...")

        # Test direct mapping
        mapped_id = await agent._get_dynamic_product_mapping("wireless keyboard pro")
        if mapped_id:
            print(f"   ✅ 'wireless keyboard pro' → {mapped_id}")
        else:
            print(f"   ❌ 'wireless keyboard pro' → No mapping found")

        # Test partial matches
        test_terms = ["wireless keyboard", "keyboard pro", "keyboard"]
        for term in test_terms:
            mapped_id = await agent._get_dynamic_product_mapping(term)
            if mapped_id:
                print(f"   ✅ '{term}' → {mapped_id}")
            else:
                print(f"   ❌ '{term}' → No mapping found")

        # Test order creation with the new product
        print("\n📋 Testing order creation with the new product...")
        order_response = await agent.process_message(
            "create order for 2 wireless keyboard pro for demo user"
        )

        order_message = order_response.get("message", "")
        if "Order Created Successfully" in order_message:
            print("   ✅ Order with new product created successfully")
        else:
            print(f"   ❌ Order creation failed: {order_message[:100]}...")

    finally:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(test_new_product_mapping())
