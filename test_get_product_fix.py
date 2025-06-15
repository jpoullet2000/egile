#!/usr/bin/env python3
"""
Test the get_product functionality to ensure the parameter fix works
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "chatbot-agent"))

from grok_agent import GrokEcommerceAgent


async def test_get_product():
    """Test get_product with the fixed parameters"""
    agent = GrokEcommerceAgent()

    try:
        await agent.start()
        print("✅ Agent started successfully")

        # Test get_product for prod_000010
        query = "what is prod_000010?"
        print(f"\n📝 Testing: '{query}'")

        response = await agent.process_message(query)

        print(f"\n📋 Response Type: {response.get('type')}")
        print(f"\n💬 Message:")
        print("-" * 60)
        print(response.get("message"))
        print("-" * 60)

        # Check if we got product details
        message = response.get("message", "")
        if "Product Details" in message and "microphone Egile" in message:
            print("\n✅ SUCCESS: get_product is working correctly!")
        elif "Error:" in message or "unexpected keyword argument" in message:
            print("\n❌ STILL FAILING: Parameter error persists")
        else:
            print("\n⚠️  UNKNOWN: Different response format")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        if agent.ecommerce_agent:
            await agent.stop()


if __name__ == "__main__":
    asyncio.run(test_get_product())
