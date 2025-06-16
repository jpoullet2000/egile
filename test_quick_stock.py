#!/usr/bin/env python3
"""
Quick test for Test Laptop stock update scenario.
"""

import asyncio
import logging
import sys

sys.path.append("/home/jbp/projects/egile/chatbot-agent")
from grok_agent import GrokEcommerceAgent

logging.basicConfig(level=logging.WARNING)  # Reduce noise


async def quick_test():
    agent = GrokEcommerceAgent()
    await agent.start()

    try:
        # Test the exact scenario from the user
        print('Testing: update stock "test laptop" by 10')
        response = await agent.process_message('update stock "test laptop" by 10')
        message = response.get("message", "")
        print(f"\nResponse:\n{message}")

        print("\n" + "=" * 50)

        print("Checking product list...")
        list_response = await agent.process_message("show me all products")
        list_message = list_response.get("message", "")

        # Extract Test Laptop line from the list
        for line in list_message.split("\n"):
            if "Test Laptop" in line:
                print(f"Product list shows: {line.strip()}")
                break

    finally:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(quick_test())
