#!/usr/bin/env python3
"""
Quick test for customer listing and name display.
"""

import asyncio
import sys
import os

# Add the egile package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

from egile.smart_agent import SmartAgent


async def test_customer_listing():
    """Test customer listing to verify names are displayed correctly."""

    print("🧪 Testing Customer Listing")
    print("=" * 40)

    agent = SmartAgent()

    try:
        # Start the agent
        await agent.start()

        # Create a test customer first
        print("📝 Creating test customer...")
        create_response = await agent.process_request(
            "create customer John Doe john.doe@test.com"
        )
        print(f"Create result: {create_response.get('message', 'No message')}")

        # List customers
        print("\n📋 Listing customers...")
        list_response = await agent.process_request("list customers")
        print(f"List result: {list_response.get('message', 'No message')}")

        # Test the formatting function directly
        print("\n🔍 Testing direct customer formatting...")
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
            {
                "name": "Bob Wilson",
                "email": "bob@test.com",
                "created_at": "2025-06-18",
            },  # Legacy format
        ]

        formatted = agent._format_customers(test_customers)
        print("Formatted customers:")
        print(formatted)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(test_customer_listing())
