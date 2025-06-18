#!/usr/bin/env python3
"""
Test script to verify the improved chatbot works correctly without multiple connections.
"""

import asyncio
import sys
import os

# Add the egile package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

from egile.smart_agent import SmartAgent


async def test_basic_functionality():
    """Test basic Smart Agent functionality."""

    print("🧪 Testing Smart Agent Basic Functionality")
    print("=" * 50)

    agent = SmartAgent()

    try:
        # Start the agent
        await agent.start()
        print("✅ Smart Agent started successfully")

        # Test customer listing
        print("\n📋 Testing customer listing...")
        list_response = await agent.process_request("list all customers")
        print(f"Response type: {list_response.get('type', 'unknown')}")
        print(f"Success: {list_response.get('success', False)}")

        # Test customer formatting
        print("\n🔍 Testing customer formatting...")
        test_customers = [
            {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@test.com",
                "created_at": "2025-06-18",
            },
            {
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane@test.com",
                "created_at": "2025-06-18",
            },
        ]

        formatted = agent._format_customers(test_customers)
        print("Formatted customers:")
        print(formatted)

        # Test order listing (if available)
        print("\n📦 Testing order listing...")
        orders_response = await agent.process_request("show me recent orders")
        print(f"Orders response type: {orders_response.get('type', 'unknown')}")
        print(f"Orders success: {orders_response.get('success', False)}")

    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await agent.stop()
        print("🔌 Smart Agent stopped")


if __name__ == "__main__":
    asyncio.run(test_basic_functionality())
