#!/usr/bin/env python3
"""
Direct test of MCP server price range functionality
"""

import asyncio
import sys
import json
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from egile.agent import EcommerceAgent


async def test_mcp_price_range():
    """Test MCP server price range functionality"""
    agent = EcommerceAgent()

    try:
        await agent.start_server()
        print("🚀 Testing MCP server price range filtering...")

        # Test 1: All products
        print("\n📝 Test 1: All products")
        result = await agent.search_products("*")
        if result.success:
            data = json.loads(result.data)
            print(f"Total products: {len(data)}")
            for product in data[:3]:  # Show first 3
                print(f"  - {product['name']}: ${product['price']}")

        # Test 2: Products between $10 and $30
        print("\n📝 Test 2: Products between $10 and $30")
        result = await agent.search_products("*", min_price=10, max_price=30)
        if result.success:
            data = json.loads(result.data)
            print(f"Products in range: {len(data)}")
            for product in data:
                print(f"  - {product['name']}: ${product['price']}")
        else:
            print(f"Error: {result.error}")

        # Test 3: Products under $50
        print("\n📝 Test 3: Products under $50")
        result = await agent.search_products("*", max_price=50)
        if result.success:
            data = json.loads(result.data)
            print(f"Products under $50: {len(data)}")
            for product in data:
                print(f"  - {product['name']}: ${product['price']}")

        # Test 4: Products over $100
        print("\n📝 Test 4: Products over $100")
        result = await agent.search_products("*", min_price=100)
        if result.success:
            data = json.loads(result.data)
            print(f"Products over $100: {len(data)}")
            for product in data:
                print(f"  - {product['name']}: ${product['price']}")

        print("\n✅ MCP price range testing completed!")

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await agent.stop_server()


if __name__ == "__main__":
    asyncio.run(test_mcp_price_range())
