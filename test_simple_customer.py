#!/usr/bin/env python3
"""
Simple test for customer creation intent analysis
"""

import asyncio
import sys
import os

# Add the chatbot-agent directory to the path
sys.path.insert(0, "/home/jbp/projects/egile/chatbot-agent")

try:
    from grok_agent import GrokEcommerceAgent

    print("✅ Import successful!")

    async def test_intent():
        agent = GrokEcommerceAgent()
        message = "create a new customer John Doe"

        print(f"🔍 Testing message: '{message}'")

        # Test intent analysis
        result = await agent.analyze_intent_with_grok(message)
        print(f"Intent result: {result}")

        # Test full processing
        full_result = await agent.process_message(message)
        print(f"Full result: {full_result}")

    asyncio.run(test_intent())

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
