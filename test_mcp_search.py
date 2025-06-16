#!/usr/bin/env python3
"""
Simple test for the MCP search functionality.
"""

import asyncio
import sys

sys.path.append("/home/jbp/projects/egile/chatbot-agent")
from grok_agent import GrokEcommerceAgent


async def test_mcp_search():
    agent = GrokEcommerceAgent()
    await agent.start()

    try:
        print("🧪 Testing MCP search functionality...\n")

        # Test the search function directly
        print("🔍 Testing direct search...")
        search_result = await agent.ecommerce_agent.search_products(query="laptop")
        print(f"Search result success: {search_result.success}")
        print(
            f"Search result data: {search_result.data[:3] if search_result.data else 'None'}"
        )

        # Test dynamic mapping
        print("\n🎯 Testing dynamic mapping...")
        mapped_id = await agent._get_dynamic_product_mapping("laptop")
        print(f"Mapped ID: {mapped_id}")

        # Test product name retrieval
        if mapped_id:
            print("\n📛 Testing product name retrieval...")
            product_name = await agent._get_product_name_by_id(mapped_id)
            print(f"Product name: {product_name}")

    finally:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(test_mcp_search())
