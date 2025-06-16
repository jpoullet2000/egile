#!/usr/bin/env python3
"""
Simple test for order creation with customer defaulting.
"""

import asyncio
import sys

sys.path.append("/home/jbp/projects/egile/chatbot-agent")
from grok_agent import GrokEcommerceAgent


async def simple_order_test():
    agent = GrokEcommerceAgent()
    await agent.start()

    try:
        print("Testing: 'create order for demo for 2 microphone Egile'")
        response = await agent.process_message(
            "create order for demo for 2 microphone Egile"
        )

        print(f"Response message: {response.get('message', '')}")

    finally:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(simple_order_test())
