#!/usr/bin/env python3
"""
Debug resource handling issues
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the project root to path
sys.path.insert(0, str(Path(__file__).parent))

from egile.agent import EcommerceAgent


async def test_resources():
    """Test resource handling."""
    agent = EcommerceAgent()

    try:
        print("🔧 Starting MCP server...")
        if not await agent.start_server():
            print("❌ Failed to start server")
            return

        print("✅ Server started successfully")

        # First create a test product
        print("\n📦 Creating test product...")
        product_response = await agent.create_product(
            name="Debug Product",
            description="Test product for debugging",
            price=99.99,
            sku="DEBUG-001",
            category="Debug",
            stock_quantity=10,
        )

        if product_response.success:
            print("✅ Test product created")
        else:
            print(f"❌ Failed to create product: {product_response.error}")

        # Test resource access
        print("\n📋 Testing resource access...")
        response = await agent.get_all_products()

        print(f"Response success: {response.success}")
        print(f"Response message: {response.message}")
        print(f"Response error: {response.error}")
        print(f"Response data type: {type(response.data)}")

        if response.success and response.data:
            print(f"Data length: {len(response.data)}")
            print(f"First data item: {response.data[0]}")

            # Try to parse the data
            try:
                if isinstance(response.data[0], dict) and "text" in response.data[0]:
                    products_json = response.data[0]["text"]
                    products = json.loads(products_json)
                    print(f"✅ Found {len(products)} products")
                    for product in products:
                        print(
                            f"   - {product.get('name', 'Unknown')} ({product.get('sku', 'No SKU')})"
                        )
                else:
                    print(f"❌ Unexpected data format: {response.data}")
            except Exception as e:
                print(f"❌ Failed to parse data: {e}")
        else:
            print("❌ No data or failed response")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await agent.stop_server()


if __name__ == "__main__":
    asyncio.run(test_resources())
