#!/usr/bin/env python3
"""
Simple test to check intent analysis for most sold products
"""

import asyncio
import sys

sys.path.append("/home/jbp/projects/egile/chatbot-agent")

from grok_agent import GrokEcommerceAgent


async def simple_intent_test():
    """Test just the intent analysis"""
    agent = GrokEcommerceAgent()

    try:
        print("Testing intent analysis for 'most sold products'...")

        # Test without starting the full agent
        intent = await agent.fallback_intent_analysis(
            "what are the most sold products?"
        )
        print(f"Intent result: {intent}")

        print("Intent analysis test completed!")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(simple_intent_test())
