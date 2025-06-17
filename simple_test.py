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

        # Test price range functionality
        print("\nTesting price range functionality...")

        print("All products:")
        all_products = await agent.search_products("")
        print(f"All products result: {all_products}")

        print("\nProducts between $10 and $30:")
        range_products = await agent.search_products("", min_price=10, max_price=30)
        print(f"Price range result: {range_products}")

        print("\nProducts under $50:")
        under_50 = await agent.search_products("", max_price=50)
        print(f"Under $50 result: {under_50}")

        print("\nProducts over $100:")
        over_100 = await agent.search_products("", min_price=100)
        print(f"Over $100 result: {over_100}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await agent.stop_server()
        print("Server stopped")


if __name__ == "__main__":
    asyncio.run(simple_test())
