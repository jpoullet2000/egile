#!/usr/bin/env python3
"""
Test script to debug product search and order creation
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from egile.smart_agent import SmartAgent


async def test_order_creation():
    """Test order creation functionality."""
    try:
        print("=== Testing Order Creation ===")

        # Initialize agent
        agent = SmartAgent()
        print("Agent initialized successfully")

        # Test 1: List products first
        print("\n1. Testing product listing:")
        result = await agent.handle_message("list products")
        print(f"List products result: {result.get('success', False)}")
        print(f"Message: {result.get('message', 'No message')[:200]}...")

        # Test 2: Search for specific product
        print("\n2. Testing product search:")
        result = await agent.handle_message("search for pen")
        print(f"Search result: {result.get('success', False)}")
        print(f"Message: {result.get('message', 'No message')[:200]}...")

        # Test 3: Try order creation
        print("\n3. Testing order creation:")
        result = await agent.handle_message(
            "create order for eli.gile@egile.com for 1 Test Product"
        )
        print(f"Order creation result: {result.get('success', False)}")
        print(f"Message: {result.get('message', 'No message')[:200]}...")

    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_order_creation())
