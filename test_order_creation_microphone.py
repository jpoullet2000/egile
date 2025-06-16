#!/usr/bin/env python3
"""Test full order creation with microphone Egile."""

import asyncio
import sys
import os

# Add project directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "chatbot-agent"))
from grok_agent import GrokEcommerceAgent


async def test_order_creation():
    """Test full order creation."""
    agent = GrokEcommerceAgent()
    await agent.start()

    try:
        print("Testing order creation for 2 microphone Egile...")
        response = await agent.chat("create order for demo for 2 microphone Egile")
        print(f"Response: {response}")

    finally:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(test_order_creation())
