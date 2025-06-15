#!/usr/bin/env python3
"""Test the Grok agent directly"""

import asyncio
import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "chatbot-agent"))

# Import with correct path structure
sys.path.insert(0, str(project_root / "chatbot-agent"))
from grok_agent import GrokEcommerceAgent


async def test_grok_agent():
    print("Starting Grok agent test...")

    agent = GrokEcommerceAgent()
    await agent.start()

    try:
        print("\n=== Testing product creation help ===")
        response = await agent.process_message("Help me create a new product")
        print(f"Response type: {type(response)}")
        print(
            f"Response keys: {response.keys() if isinstance(response, dict) else 'Not a dict'}"
        )
        if isinstance(response, dict):
            print(f"Message: {response.get('message', 'No message')}")
            print(f"Type: {response.get('type', 'No type')}")

        print("\n=== Testing product creation with details ===")
        response2 = await agent.process_message(
            'Create product "Test iPhone" with description "Latest smartphone", price $999.99, SKU IP-TEST-001, category Electronics, stock 25'
        )
        print(f"Response type: {type(response2)}")
        print(
            f"Response keys: {response2.keys() if isinstance(response2, dict) else 'Not a dict'}"
        )
        if isinstance(response2, dict):
            print(f"Message: {response2.get('message', 'No message')}")
            print(f"Type: {response2.get('type', 'No type')}")

        print("\n=== Testing simple product listing ===")
        response3 = await agent.process_message("show me all products")
        print(f"Response type: {type(response3)}")
        if isinstance(response3, dict):
            print(f"Message: {response3.get('message', 'No message')[:200]}...")

    except Exception as e:
        print(f"Error during test: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await agent.stop()
        print("Test completed.")


if __name__ == "__main__":
    asyncio.run(test_grok_agent())
