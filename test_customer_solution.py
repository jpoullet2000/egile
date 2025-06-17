#!/usr/bin/env python3
"""
Test to create a customer with proper email to show the user how it should work
"""

import asyncio
import sys
import os

# Add the chatbot-agent directory to the path
sys.path.insert(0, "/home/jbp/projects/egile/chatbot-agent")

try:
    from grok_agent import GrokEcommerceAgent

    print("✅ Import successful!")

    async def test_fixed_customer_creation():
        agent = GrokEcommerceAgent()

        # Start the agent
        print("🔧 Starting agent...")
        await agent.start()

        # Test 1: Try to create customer with complete info
        message1 = "create customer John Doe with email john.doe@example.com"
        print(f"\n🔍 Test 1: '{message1}'")
        result1 = await agent.process_message(message1)
        print(f"✅ Result 1: {result1.get('message', 'No message')}")

        # Test 2: Show what happens when user only provides name
        print(f"\n📝 **How to create a customer:**")
        print(f"❌ Wrong: 'create a new customer John Doe' (missing email)")
        print(f"✅ Right: 'create customer John Doe with email john.doe@example.com'")
        print(f"✅ Also works: 'add customer Jane Smith jane.smith@email.com'")

        # Test 3: Show database constraint if trying incomplete info
        message2 = "create a new customer Bob Wilson"
        print(f"\n🔍 Test 2 (will fail): '{message2}'")
        result2 = await agent.process_message(message2)

        # Extract just the error info
        action_result = result2.get("action_result", {})
        if "UNIQUE constraint failed" in str(action_result.get("data", "")):
            print(f"❌ Result 2: Database error because email is required but empty")
            print(
                f"💡 **Solution:** Always include an email address when creating customers"
            )
        else:
            print(f"Result 2: {result2.get('message', 'No message')}")

    asyncio.run(test_fixed_customer_creation())

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
