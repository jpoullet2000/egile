#!/usr/bin/env python3
"""Test the expensive products sorting end-to-end"""

import asyncio
import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "chatbot-agent"))

from grok_agent import GrokEcommerceAgent


async def test_expensive_products_full():
    """Test the full expensive products flow"""
    agent = GrokEcommerceAgent()

    try:
        print("Starting ecommerce agent...")
        await agent.start()
        print("Agent started successfully!")

        # Test the intent analysis first
        print("\n=== Testing intent analysis ===")
        intent = agent.fallback_intent_analysis("what are the most expensive products?")
        print(f"Intent result: {intent}")

        # Test the full process_message flow
        print("\n=== Testing full process_message flow ===")
        response = await agent.process_message("what are the most expensive products?")
        print(f"Response type: {response.get('type')}")
        print(f"Message preview: {response.get('message', 'No message')[:400]}...")

        print("\n✅ Full test completed!")

    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback

        traceback.print_exc()
    finally:
        print("Stopping agent...")
        await agent.stop()
        print("Agent stopped.")


if __name__ == "__main__":
    asyncio.run(test_expensive_products_full())
