#!/usr/bin/env python3
"""
Quick test for customer help flow
"""

import asyncio
import sys
import os

# Set up the path and environment
sys.path.insert(0, "/home/jbp/projects/egile/chatbot-agent")
os.chdir("/home/jbp/projects/egile")


async def test_customer_help():
    from grok_agent import GrokEcommerceAgent

    print("🔧 Starting test...")

    try:
        agent = GrokEcommerceAgent()
        await agent.start()

        # Test the exact user input from the issue
        message = "how to create a customer"
        print(f"🔍 Testing: '{message}'")

        result = await agent.process_message(message)
        print("📋 Result:")
        print(f"   Type: {result.get('type')}")
        print(f"   Action: {result.get('action')}")
        print(f"   Success: {result.get('success')}")

        if result.get("message"):
            print(f"   Message: {result['message'][:200]}...")  # First 200 chars

        await agent.stop()

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_customer_help())
