#!/usr/bin/env python3
"""
Debug the microphone product mapping issue.
"""

import asyncio
import sys

sys.path.append("/home/jbp/projects/egile/chatbot-agent")
from grok_agent import GrokEcommerceAgent


async def debug_microphone_mapping():
    agent = GrokEcommerceAgent()
    await agent.start()

    try:
        print("🧪 Debugging microphone product mapping...\n")

        # Test different search terms
        search_terms = [
            "microphone_egile",
            "microphone egile",
            "microphone",
            "egile",
            "Microphone Egile",
        ]

        for term in search_terms:
            print(f"🔍 Testing search term: '{term}'")

            # Test the MCP search directly
            search_result = await agent.ecommerce_agent.search_products(query=term)
            print(f"  MCP search success: {search_result.success}")
            if search_result.success and search_result.data:
                print(f"  Found {len(search_result.data)} products")
                for product in search_result.data[:3]:
                    if isinstance(product, dict):
                        print(f"    - {product.get('name')} (ID: {product.get('id')})")
            else:
                print(f"  No products found or search failed")

            # Test the dynamic mapping
            mapped_id = await agent._get_dynamic_product_mapping(term)
            print(f"  Dynamic mapping result: {mapped_id}")
            print()

        # Also test listing all products to see what we have
        print("📦 All products in database:")
        all_products = await agent.ecommerce_agent.get_all_products()
        if all_products.success and all_products.data:
            for product in all_products.data[:10]:
                if isinstance(product, dict):
                    print(
                        f"  - {product.get('name')} (ID: {product.get('id')}, SKU: {product.get('sku')})"
                    )

    finally:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(debug_microphone_mapping())
