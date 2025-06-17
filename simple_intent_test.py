#!/usr/bin/env python3
"""
Simple test to see what happens with customer help requests
"""

import asyncio
import os
import sys


# Test just the intent analysis directly
async def test_customer_help():
    # Add the chatbot-agent directory to path
    sys.path.insert(0, "/home/jbp/projects/egile/chatbot-agent")

    from grok_agent import GrokEcommerceAgent

    print("🔧 Starting intent analysis test...")

    agent = GrokEcommerceAgent()
    await agent.start()

    test_message = "how to create a customer"
    print(f"\n🔍 Testing: '{test_message}'")

    # Test the fallback intent analysis
    intent = await agent.fallback_intent_analysis(test_message)
    print("📋 Fallback Intent Analysis Result:")
    for key, value in intent.items():
        print(f"   {key}: {value}")

    await agent.stop()


if __name__ == "__main__":
    asyncio.run(test_customer_help())
