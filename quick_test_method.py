#!/usr/bin/env python3
"""
Quick test for order creation
"""

import asyncio
import sys
import os

sys.path.append("/home/jbp/projects/egile/chatbot-agent")

from grok_agent import GrokEcommerceAgent


async def quick_test():
    print("Starting quick test...")
    agent = GrokEcommerceAgent()

    try:
        await agent.start()
        print("Agent started")

        # Simple test
        response = await agent.process_message(
            "create order for demo for 2 microphones"
        )
        print(f"Response type: {response.get('type')}")
        print(f"Message: {response.get('message')}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        try:
            await agent.stop()
        except:
            pass


if __name__ == "__main__":
    asyncio.run(quick_test())
