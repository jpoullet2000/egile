#!/usr/bin/env python3
"""
Final verification script to test all the implemented features.
"""

import asyncio
import logging
import sys

sys.path.append("/home/jbp/projects/egile/chatbot-agent")
from grok_agent import GrokEcommerceAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_sorted_products():
    """Test sorted product queries"""
    print("🧪 Testing sorted product queries...")

    agent = GrokEcommerceAgent()
    await agent.start()

    try:
        # Test 1: Most expensive products
        print("\n1. Testing 'most expensive' query...")
        result = await agent.process_message("show me the most expensive products")
        print(f"Result type: {result.get('type')}")
        print(f"Success: {result.get('success')}")
        if result.get("message"):
            print(f"Message (first 200 chars): {result['message'][:200]}...")

        # Test 2: Cheapest products
        print("\n2. Testing 'cheapest' query...")
        result = await agent.process_message("what are the cheapest products?")
        print(f"Result type: {result.get('type')}")
        print(f"Success: {result.get('success')}")
        if result.get("message"):
            print(f"Message (first 200 chars): {result['message'][:200]}...")

        # Test 3: Customer contact query
        print("\n3. Testing customer contact query...")
        result = await agent.process_message("how can I contact customers?")
        print(f"Result type: {result.get('type')}")
        print(f"Success: {result.get('success')}")
        if result.get("message"):
            print(f"Message (first 200 chars): {result['message'][:200]}...")

        # Test 4: Interactive product creation
        print("\n4. Testing interactive product creation...")
        result = await agent.process_message("I want to add a new product")
        print(f"Result type: {result.get('type')}")
        print(f"Success: {result.get('success')}")
        if result.get("message"):
            print(f"Message (first 200 chars): {result['message'][:200]}...")

        print("\n✅ All tests completed!")

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await agent.stop()


async def main():
    await test_sorted_products()


if __name__ == "__main__":
    asyncio.run(main())
