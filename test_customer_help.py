#!/usr/bin/env python3
"""
Test the new customer creation help functionality
"""

import asyncio
import sys

# Add the chatbot-agent directory to the path
sys.path.insert(0, "/home/jbp/projects/egile/chatbot-agent")

try:
    from grok_agent import GrokEcommerceAgent

    print("✅ Import successful!")

    async def test_customer_help():
        agent = GrokEcommerceAgent()

        # Start the agent
        print("🔧 Starting agent...")
        await agent.start()

        # Test 1: Ask for help creating a customer
        print("\n" + "=" * 60)
        message1 = "how to create a customer"
        print(f"🔍 Test 1: '{message1}'")
        result1 = await agent.process_message(message1)
        print(f"✅ Result:\n{result1.get('message', 'No message')}")

        print("\n" + "=" * 60)
        # Test 2: Alternative help request
        message2 = "help me create a customer"
        print(f"🔍 Test 2: '{message2}'")
        result2 = await agent.process_message(message2)
        print(f"✅ Result:\n{result2.get('message', 'No message')}")

        print("\n" + "=" * 60)
        # Test 3: Another variation
        message3 = "how do I add a customer"
        print(f"🔍 Test 3: '{message3}'")
        result3 = await agent.process_message(message3)
        print(f"✅ Result:\n{result3.get('message', 'No message')}")

    asyncio.run(test_customer_help())

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
