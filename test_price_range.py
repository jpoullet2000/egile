#!/usr/bin/env python3
"""
Test script to verify price range filtering functionality.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.append("/home/jbp/projects/egile/chatbot-agent")

from grok_agent import GrokEcommerceAgent


async def test_price_range():
    """Test price range functionality"""
    agent = GrokEcommerceAgent()

    try:
        await agent.start()
        print("🚀 Testing price range filtering...")

        # Test 1: Between $10 and $30
        print("\n📝 Test 1: 'what are the products between $10 and $30'")
        result = await agent.process_message(
            "what are the products between $10 and $30"
        )
        print(f"Response: {result.get('message', 'No message')}")

        # Test 2: Under $50
        print("\n📝 Test 2: 'show me products under $50'")
        result = await agent.process_message("show me products under $50")
        print(f"Response: {result.get('message', 'No message')}")

        # Test 3: Over $100
        print("\n📝 Test 3: 'products over $100'")
        result = await agent.process_message("products over $100")
        print(f"Response: {result.get('message', 'No message')}")

        print("\n✅ Price range testing completed!")

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(test_price_range())
