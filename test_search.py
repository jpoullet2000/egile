#!/usr/bin/env python3
"""
Quick test for search functionality.
"""

import asyncio
import sys
import os

# Add the egile package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

from egile.smart_agent import SmartAgent


async def test_search():
    """Test product search functionality."""

    print("🔍 Testing Product Search")
    print("=" * 30)

    agent = SmartAgent()

    try:
        # Start the agent
        await agent.start()

        # Test search functionality
        print("🔍 Searching for 'wireless'...")
        response = await agent.process_request("search wireless")
        print(f"Search result: {response.get('message', 'No message')[:200]}...")
        print(f"Success: {response.get('success', False)}")

        # Test another search
        print("\n🔍 Searching for 'laptop'...")
        response = await agent.process_request("search laptop")
        print(f"Search result: {response.get('message', 'No message')[:200]}...")
        print(f"Success: {response.get('success', False)}")

        # Test search with no results
        print("\n🔍 Searching for 'nonexistent'...")
        response = await agent.process_request("search nonexistent")
        print(f"Search result: {response.get('message', 'No message')}")
        print(f"Success: {response.get('success', False)}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(test_search())
