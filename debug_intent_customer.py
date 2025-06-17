#!/usr/bin/env python3
"""
Debug script to test intent analysis for customer help requests
"""

import asyncio
import sys

sys.path.append("/home/jbp/projects/egile/chatbot-agent")
from grok_agent import GrokEcommerceAgent


async def test_intent_analysis():
    """Test intent analysis for customer help requests"""
    print("🔧 Starting intent analysis debug...")

    agent = GrokEcommerceAgent()
    await agent.start()

    test_messages = [
        "how to create a customer",
        "help me create a customer",
        "how do I add a customer",
        "customer creation help",
        "how to create customer",
    ]

    for message in test_messages:
        print(f"\n{'=' * 60}")
        print(f"🔍 Testing: '{message}'")

        # Test fallback intent analysis directly
        try:
            intent = await agent.fallback_intent_analysis(message)
            print(f"📋 Intent Analysis Result:")
            print(f"   Action: {intent.get('action')}")
            print(f"   Intent: {intent.get('intent')}")
            print(f"   Confidence: {intent.get('confidence')}")
            print(f"   Parameters: {intent.get('parameters')}")
        except Exception as e:
            print(f"❌ Error in intent analysis: {e}")

    await agent.stop()


if __name__ == "__main__":
    asyncio.run(test_intent_analysis())
