#!/usr/bin/env python3
"""Test microphone mapping fix."""

import asyncio
import sys
import os

# Add project directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "chatbot-agent"))
from grok_agent import GrokEcommerceAgent


async def test_microphone_mapping():
    """Test microphone mapping."""
    agent = GrokEcommerceAgent()
    await agent.start()

    try:
        print("Testing microphone_egile mapping...")
        result = await agent._get_dynamic_product_mapping("microphone_egile")
        print(f"Result: {result}")

        if result:
            print("SUCCESS: microphone_egile mapped correctly!")
        else:
            print("FAILED: microphone_egile did not map")

    finally:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(test_microphone_mapping())
