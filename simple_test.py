#!/usr/bin/env python3
"""Simple test for microphone order creation"""

import asyncio
import sys
from pathlib import Path

from egile.agent import EcommerceAgent


async def simple_test():
    agent = EcommerceAgent()

    try:
        print("Starting server...")
        success = await agent.start_server()
        print(f"Server start result: {success}")

        if not success:
            print("Failed to start server")
            return

        print("Server started successfully!")

        # Test basic functionality
        print("Testing product search...")
        products = await agent.search_products("microphone")
        print(f"Search result: {products}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await agent.stop_server()
        print("Server stopped")


if __name__ == "__main__":
    asyncio.run(simple_test())
