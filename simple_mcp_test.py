#!/usr/bin/env python3
"""Simple test of fixed MCP agent."""

import asyncio
import sys
import os

# Add project directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "egile"))

from egile.agent import EcommerceAgent


async def simple_test():
    """Simple test of the fixed agent."""
    agent = EcommerceAgent()

    print("Starting agent...")
    success = await agent.start_server()
    if not success:
        print("Failed to start server")
        return

    print("Testing search_products...")
    result = await agent.search_products("microphone")
    print(f"Success: {result.success}")
    print(f"Data type: {type(result.data)}")
    if result.data:
        print(
            f"Data length: {len(result.data) if isinstance(result.data, list) else 'Not a list'}"
        )
        if isinstance(result.data, list) and result.data:
            print(f"First item: {result.data[0]}")
            print(f"First item type: {type(result.data[0])}")

    await agent.stop_server()


if __name__ == "__main__":
    asyncio.run(simple_test())
