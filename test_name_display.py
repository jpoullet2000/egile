#!/usr/bin/env python3
"""
Test script to verify customer names are displayed correctly in both customer and order listings.
"""

import asyncio
import sys
import os

# Add the egile package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

from egile.smart_agent import SmartAgent


async def test_name_display():
    """Test that customer names display correctly in listings."""

    print("🧪 Testing Customer and Order Name Display")
    print("=" * 50)

    agent = SmartAgent()

    try:
        # Start the agent
        print("🚀 Starting Smart Agent...")
        await agent.start()

        # Test customer listing
        print("\n📋 Testing customer listing...")
        customer_response = await agent.process_request("list customers")
        print("Customer listing result:")
        print(
            customer_response.get("message", "No message")[:500] + "..."
            if len(customer_response.get("message", "")) > 500
            else customer_response.get("message", "No message")
        )

        # Test order listing
        print("\n📦 Testing order listing...")
        order_response = await agent.process_request("show recent orders")
        print("Order listing result:")
        print(
            order_response.get("message", "No message")[:500] + "..."
            if len(order_response.get("message", "")) > 500
            else order_response.get("message", "No message")
        )

        print("\n✅ Test completed!")

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(test_name_display())
