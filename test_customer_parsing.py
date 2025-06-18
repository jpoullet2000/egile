#!/usr/bin/env python3
"""
Test script for natural language customer parsing functionality.
"""

import asyncio
import sys
import os

# Add the egile package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

from egile.smart_agent import SmartAgent


async def test_customer_parsing():
    """Test various natural language customer creation inputs."""

    print("🧪 Testing Natural Language Customer Parsing")
    print("=" * 50)

    # Initialize the agent
    agent = SmartAgent()

    test_cases = [
        # Basic patterns
        "create customer John Doe john@email.com",
        "add customer Jane Smith jane.smith@company.org",
        "new customer Bob Wilson bob.wilson@test.net",
        # More natural language
        "create customer John Doe with email john@example.com and phone (555) 123-4567",
        "add a customer named Alice Brown, email alice@test.com, phone 555-234-5678",
        "register customer Mike Davis mike.davis@company.com address 123 Main St",
        # Just names and emails
        "Sarah Johnson sarah.johnson@email.com",
        "David Lee david@company.org (555) 345-6789",
        # More complex
        "create customer Mary Wilson mary@test.com phone 555-456-7890 address 456 Oak Avenue",
        "add customer Tom Brown email tom.brown@company.net phone (555) 567-8901 lives at 789 Pine Street",
        # Edge cases
        "customer Robert Jones",  # Missing email
        "create customer email@test.com",  # Missing name
        "just some random text",  # No customer info
    ]

    for i, test_input in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: '{test_input}'")
        print("-" * 30)

        # Test intent analysis
        intent = agent._analyze_intent(test_input)
        print(f"Intent: {intent.get('type')} -> {intent.get('action', 'N/A')}")

        # Test customer parsing
        parsed_info = agent._parse_customer_from_text(test_input)
        formatted_info = agent._format_parsed_info(parsed_info)
        print(f"Parsed: {formatted_info}")

        # Check if we would detect as customer creation
        if intent.get("action") == "create_customer":
            print("✅ Correctly identified as customer creation")
        else:
            print("❌ Not identified as customer creation")

    print("\n" + "=" * 50)
    print("🎯 Testing Complete!")

    # Test a full customer creation flow
    print("\n🚀 Testing Full Customer Creation Flow")
    print("-" * 30)

    try:
        # Start the agent
        await agent.start()

        # Test with a complete customer
        response = await agent.process_request(
            "create customer John Doe john.doe@test.com phone (555) 123-4567"
        )
        print(f"Full flow response: {response.get('message', 'No message')}")

        # Test with missing information
        response = await agent.process_request("create customer John Doe")
        print(f"Missing info response: {response.get('message', 'No message')}")

    except Exception as e:
        print(f"Error during full flow test: {e}")
    finally:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(test_customer_parsing())
