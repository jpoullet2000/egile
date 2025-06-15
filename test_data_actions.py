#!/usr/bin/env python3
"""Test data retrieval actions"""

import asyncio
import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "chatbot-agent"))

from grok_agent import GrokEcommerceAgent


async def test_data_actions():
    """Test that data actions show proper results"""
    agent = GrokEcommerceAgent()

    try:
        print("Starting ecommerce agent...")
        await agent.start()
        print("Agent started successfully!")

        # Test list orders
        print("\n=== Testing 'Show me recent orders' ===")
        response1 = await agent.process_message("Show me recent orders")
        print(f"Response type: {response1.get('type')}")
        print(f"Message preview: {response1.get('message', 'No message')[:400]}...")

        # Test list products
        print("\n=== Testing 'Show me all products' ===")
        response2 = await agent.process_message("Show me all products")
        print(f"Response type: {response2.get('type')}")
        print(f"Message preview: {response2.get('message', 'No message')[:400]}...")

        print("\n✅ Data action tests completed!")

    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback

        traceback.print_exc()
    finally:
        print("Stopping agent...")
        await agent.stop()
        print("Agent stopped.")


if __name__ == "__main__":
    asyncio.run(test_data_actions())
