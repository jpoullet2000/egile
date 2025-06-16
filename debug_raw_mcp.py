#!/usr/bin/env python3
"""Debug script to check raw MCP server responses."""

import asyncio
import logging
import sys
import os

# Add project directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "egile"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "chatbot-agent"))

from egile.agent import EcommerceAgent

# Set up logging
logging.basicConfig(level=logging.INFO)


async def debug_raw_mcp_responses():
    """Debug raw MCP server responses."""
    # Initialize the ecommerce agent
    ecommerce_agent = EcommerceAgent()

    print("=== Raw MCP Server Responses ===")

    print("\n1. Testing search_products with 'microphone':")
    result = await ecommerce_agent.search_products(query="microphone")
    print(f"Success: {result.success}")
    print(f"Data type: {type(result.data)}")
    print(f"Data: {result.data}")

    print("\n2. Testing get_all_products:")
    result = await ecommerce_agent.get_all_products()
    print(f"Success: {result.success}")
    print(f"Data type: {type(result.data)}")
    if result.data:
        print(f"Number of items: {len(result.data)}")
        print(f"First item: {result.data[0] if result.data else 'None'}")
        print(f"First item type: {type(result.data[0]) if result.data else 'None'}")
    print(f"Full data: {result.data}")


if __name__ == "__main__":
    asyncio.run(debug_raw_mcp_responses())
