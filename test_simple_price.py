#!/usr/bin/env python3
"""
Simple test to verify price range functionality
"""

import asyncio
import sys
import os

sys.path.append("/home/jbp/projects/egile/chatbot-agent")

from grok_agent import GrokEcommerceAgent


async def test_simple():
    agent = GrokEcommerceAgent()
    await agent.start()

    print("Testing fallback intent analysis...")
    result = await agent.fallback_intent_analysis(
        "what are the products between $10 and $30"
    )
    print(f"Intent analysis result: {result}")

    await agent.stop()


if __name__ == "__main__":
    asyncio.run(test_simple())
