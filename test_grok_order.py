#!/usr/bin/env python3
"""Test Grok agent order processing."""

import asyncio
import sys
import os

# Add project directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "chatbot-agent"))
from grok_agent import GrokEcommerceAgent


async def test_grok_order():
    """Test Grok agent order processing."""
    agent = GrokEcommerceAgent()

    try:
        await agent.start()
        print("Grok agent started successfully")

        # Test order creation with debug
        message = "create order for demo for 2 microphone Egile"
        print(f"Processing message: '{message}'")

        # Call the process_message method directly
        response = await agent.process_message(message)
        print(f"Response: {response}")

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
    asyncio.run(test_grok_order())
