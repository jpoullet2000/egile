#!/usr/bin/env python3
"""
Comprehensive stock update verification test.
Tests enhanced confirmation messages and proper operation detection.
"""

import asyncio
import logging
import sys

sys.path.append("/home/jbp/projects/egile/chatbot-agent")
from grok_agent import GrokEcommerceAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_stock_updates_comprehensive():
    """
    Test all stock update scenarios and verify enhanced confirmation messages
    """
    print("🔍 Starting comprehensive stock update verification...")

    agent = GrokEcommerceAgent()

    try:
        await agent.start()
        print("✅ Agent started successfully\n")

        # Test scenarios with different products and operations
        test_cases = [
            # Basic increment operations
            ("update stock laptop by 5", "increment", "laptop"),
            ("increase laptop stock by 10", "increment", "laptop"),
            ("add 15 to laptop stock", "increment", "laptop"),
            # Basic set operations
            ("set laptop stock to 30", "set", "laptop"),
            ("update laptop stock to 25", "set", "laptop"),
            ("change laptop stock to 40", "set", "laptop"),
            # Different product variations
            ("update laptop pro stock by 3", "increment", "laptop pro"),
            ("set laptop pro stock to 20", "set", "laptop pro"),
            # Test Laptop specifically (edge case)
            ("update test laptop stock by 2", "increment", "test laptop"),
            ("set test laptop stock to 15", "set", "test laptop"),
        ]

        print(f"📋 Running {len(test_cases)} comprehensive test cases...\n")

        for i, (user_message, expected_operation, product_name) in enumerate(
            test_cases, 1
        ):
            print(f"🧪 Test {i}: '{user_message}'")
            print(f"   Expected: {expected_operation} operation for {product_name}")

            try:
                response = await agent.process_message(user_message)

                # Verify response structure
                if not isinstance(response, dict):
                    print(f"   ❌ Invalid response type: {type(response)}")
                    continue

                message = response.get("message", "")
                intent = response.get("intent", {})
                action_result = response.get("action_result", {})

                print(f"   📤 Response type: {response.get('type')}")

                # Check if stock update was successful
                success = (
                    action_result.get("success", False) if action_result else False
                )

                if not success:
                    error_msg = (
                        action_result.get("error", "Unknown error")
                        if action_result
                        else "No action result"
                    )
                    print(f"   ❌ Stock update failed: {error_msg}")
                    continue

                # Verify enhanced confirmation message contains all required elements
                required_elements = [
                    "Stock Updated Successfully",
                    "Product Details:",
                    "Name:",
                    "ID:",
                    "Price:",
                    "Category:",
                    "New Stock Level:",
                ]

                missing_elements = []
                found_elements = []
                for element in required_elements:
                    if element in message:
                        found_elements.append(element)
                    else:
                        missing_elements.append(element)

                if missing_elements:
                    print(f"   ⚠️  Missing elements in confirmation: {missing_elements}")
                    print(f"   ✅ Found elements: {found_elements}")
                    print(f"   📄 Message preview: {message[:300]}...")
                else:
                    print(
                        "   ✅ Enhanced confirmation message contains all required elements"
                    )

                # Verify intent analysis detected correct operation
                parameters = intent.get("parameters", {})
                detected_operation = parameters.get("operation", "unknown")

                if expected_operation == "increment" and detected_operation in [
                    "add",
                    "increment",
                ]:
                    print(f"   ✅ Operation correctly detected: {detected_operation}")
                elif expected_operation == "set" and detected_operation == "set":
                    print(f"   ✅ Operation correctly detected: {detected_operation}")
                else:
                    print(
                        f"   ⚠️  Operation detection issue - Expected: {expected_operation}, Got: {detected_operation}"
                    )

                # Check for product mapping
                product_id = parameters.get("product_id")
                if product_id:
                    print(f"   ✅ Product mapped to ID: {product_id}")
                else:
                    print("   ⚠️  No product ID found in parameters")

                print()  # Empty line for readability

            except Exception as e:
                print(f"   ❌ Test failed with exception: {e}")
                import traceback

                traceback.print_exc()
                print()

        print("🔍 Testing edge cases...\n")

        # Test edge cases
        edge_cases = [
            "update nonexistent product stock by 5",
            "set negative stock to -10",
            "update stock with no product name",
            "increase by zero",
            "update stock laptop by abc",  # Non-numeric quantity
        ]

        for edge_case in edge_cases:
            print(f"🧪 Edge case: '{edge_case}'")
            try:
                response = await agent.process_message(edge_case)
                message = response.get("message", "")
                success = response.get("action_result", {}).get("success", False)
                print(f"   Success: {success}")
                print(f"   Response: {message[:150]}...")
            except Exception as e:
                print(f"   Handled exception: {e}")
            print()

        print("✅ Comprehensive verification completed!")

    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        import traceback

        traceback.print_exc()
    finally:
        if agent.ecommerce_agent:
            await agent.stop()
            print("🛑 Agent stopped")


if __name__ == "__main__":
    asyncio.run(test_stock_updates_comprehensive())
