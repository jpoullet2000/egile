#!/usr/bin/env python3
"""
Debug script to test product search functionality
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from egile.agent import EcommerceAgent


async def debug_product_search():
    """Debug product search to understand the issue."""
    agent = EcommerceAgent()

    print("=== Testing Product Search ===")

    # First, list all products
    print("\n1. Listing all products:")
    result = await agent.list_products()
    print(f"Success: {result.success}")
    print(f"Data type: {type(result.data)}")
    if result.data:
        print(f"Data length: {len(result.data)}")
        print(f"First item type: {type(result.data[0])}")
        print(f"First item: {result.data[0]}")

    # Then search for specific products
    print("\n2. Searching for 'pen':")
    result = await agent.search_products("pen")
    print(f"Success: {result.success}")
    print(f"Data: {result.data}")

    print("\n3. Searching for 'Test':")
    result = await agent.search_products("Test")
    print(f"Success: {result.success}")
    print(f"Data: {result.data}")


if __name__ == "__main__":
    asyncio.run(debug_product_search())
