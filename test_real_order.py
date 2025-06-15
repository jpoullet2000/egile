#!/usr/bin/env python3
"""Test order creation with real data"""

import asyncio
import json
from grok_agent import GrokEcommerceAgent


async def test_real_order_creation():
    """Test order creation with actual customer and product IDs"""
    agent = GrokEcommerceAgent()

    try:
        print("🚀 Testing Real Order Creation")
        print("=" * 40)

        await agent.start()

        # First, get real customer and product data
        print("📋 Getting real customer and product data...")

        # Test with a message that should work with real data
        customers_response = await agent.process_message("show me customers")
        print(f"Customers response type: {customers_response.get('type')}")

        products_response = await agent.process_message("show me products")
        print(f"Products response type: {products_response.get('type')}")

        # Now test with the problematic order creation message
        print(f"\n🛒 Testing order creation with 'demo' and 'laptop'...")

        # Let's see what the intent analysis produces
        intent = agent.fallback_intent_analysis("create order for demo for 2 laptops")
        print(f"Intent: {intent}")

        # Now let's try to actually execute this
        try:
            if intent.get("requires_action") and intent.get("action") == "create_order":
                result = await agent.execute_ecommerce_action(intent)
                print(f"Execution result: {result}")
                print(f"Success: {result.get('success')}")
                print(f"Error: {result.get('error')}")
                print(f"Data: {result.get('data')}")
        except Exception as e:
            print(f"❌ Execution failed: {e}")
            import traceback

            traceback.print_exc()

        # Let's try with valid IDs
        print(f"\n🔧 Testing with valid customer and product IDs...")
        valid_intent = {
            "intent": "Create order with valid IDs",
            "action": "create_order",
            "parameters": {
                "customer_id": "cust_000001",
                "items": [{"product_id": "prod_000004", "quantity": 2}],
                "currency": "USD",
            },
            "requires_action": True,
        }

        try:
            valid_result = await agent.execute_ecommerce_action(valid_intent)
            print(f"Valid execution result: {valid_result}")
            print(f"Success: {valid_result.get('success')}")
            print(f"Error: {valid_result.get('error')}")
            print(f"Data: {valid_result.get('data')}")
        except Exception as e:
            print(f"❌ Valid execution failed: {e}")
            import traceback

            traceback.print_exc()

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()

    finally:
        await agent.stop()
        print("\n🏁 Test completed!")


if __name__ == "__main__":
    asyncio.run(test_real_order_creation())
