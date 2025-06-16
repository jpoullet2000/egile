#!/usr/bin/env python3
"""
Test the best customer functionality.
"""

import asyncio
import sys

sys.path.append("/home/jbp/projects/egile/chatbot-agent")
from grok_agent import GrokEcommerceAgent


async def test_best_customer():
    agent = GrokEcommerceAgent()
    await agent.start()

    try:
        print("🧪 Testing 'who is my best customer' functionality...\n")

        # Test the query
        response = await agent.process_message("who is my best customer?")

        print(f"Response type: {response.get('type')}")
        print(f"Message: {response.get('message', '')[:200]}...")

        if "Error" in response.get("message", ""):
            print("❌ Error occurred")
            print(f"Full message: {response.get('message')}")
        else:
            print("✅ Query processed successfully")

    finally:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(test_best_customer())
