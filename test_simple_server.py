#!/usr/bin/env python3
"""
Simple test server without MCP dependencies for debugging
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the project root to path
sys.path.insert(0, str(Path(__file__).parent))

from egile.database import EcommerceDatabase, Product


class SimpleTestServer:
    """Simple server for testing database functionality."""

    def __init__(self):
        self.db = EcommerceDatabase("test_server.db")

    def test_basic_operations(self):
        """Test basic database operations."""
        print("Testing basic database operations...")

        # Test product creation
        product = Product(
            id="test_001",
            name="Test Product",
            description="A test product",
            price=99.99,
            currency="USD",
            sku="TEST-001",
            category="Test",
            stock_quantity=10,
        )

        try:
            created = self.db.create_product(product)
            print(f"✅ Created product: {created.name}")

            # Test retrieval
            retrieved = self.db.get_product("test_001")
            if retrieved:
                print(f"✅ Retrieved product: {retrieved.name}")
            else:
                print("❌ Failed to retrieve product")

            # Test search
            results = self.db.search_products("test")
            print(f"✅ Search found {len(results)} products")

            return True

        except Exception as e:
            print(f"❌ Database test failed: {e}")
            return False


async def main():
    """Test the simple server."""
    print("Starting simple test server...")

    try:
        server = SimpleTestServer()
        success = server.test_basic_operations()

        if success:
            print("✅ All tests passed! Database is working correctly.")
            print("The issue is likely with MCP package installation.")
            print("Install MCP with: pip install mcp")
        else:
            print("❌ Database tests failed.")

    except Exception as e:
        print(f"❌ Test server failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
