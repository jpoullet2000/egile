#!/usr/bin/env python3
"""
Test script to add a customer and then test the contact functionality.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import importlib.util

spec = importlib.util.spec_from_file_location(
    "grok_agent", "chatbot-agent/grok_agent.py"
)
grok_agent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grok_agent)
GrokEcommerceAgent = grok_agent.GrokEcommerceAgent


async def test_customer_contact():
    """Test customer contact functionality"""
    print("🧪 Testing customer contact functionality...")

    agent = GrokEcommerceAgent()
    await agent.start()

    try:
        # First, add a customer
        print("\n1. Adding a test customer...")
        result = await agent.process_message(
            "add customer John Doe, email: demo@example.com, phone: 555-1234"
        )
        print(f"Add customer result: {result.get('success')}")
        if result.get("message"):
            print(f"Message: {result['message'][:200]}...")

        # Now test contact query
        print("\n2. Testing contact query...")
        result = await agent.process_message("contact demo@example.com")
        print(f"Contact result: {result.get('success')}")
        print(f"Result type: {result.get('type')}")
        if result.get("message"):
            print(f"Message: {result['message'][:300]}...")

        print("\n✅ Test completed!")

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(test_customer_contact())
