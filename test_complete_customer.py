#!/usr/bin/env python3
"""
Complete test for customer creation with proper agent initialization
"""

import asyncio
import sys
import os

# Add the chatbot-agent directory to the path
sys.path.insert(0, "/home/jbp/projects/egile/chatbot-agent")

try:
    from grok_agent import GrokEcommerceAgent

    print("✅ Import successful!")

    async def test_customer_creation():
        agent = GrokEcommerceAgent()

        # Initialize the agent
        print("🔧 Starting agent...")
        await agent.start()

        message = "create a new customer John Doe"

        print(f"🔍 Testing message: '{message}'")

        # Test full processing
        result = await agent.process_message(message)
        print(f"Result: {result}")

        print("\n" + "=" * 60)

        # Test with email included
        message2 = "create customer Jane Smith with email jane.smith@example.com"
        print(f"🔍 Testing message with email: '{message2}'")

        result2 = await agent.process_message(message2)
        print(f"Result: {result2}")

    asyncio.run(test_customer_creation())

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
