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
        print("\n=== Testing product listing ===")
        response = await agent.process_message("show me all products")
        print(f"Response type: {type(response)}")
        print(
            f"Response keys: {response.keys() if isinstance(response, dict) else 'Not a dict'}"
        )
        if isinstance(response, dict):
            print(f"Message: {response.get('message', 'No message')[:200]}...")
            if "action_result" in response:
                action_result = response["action_result"]
                print(f"Action result success: {action_result.get('success')}")
                print(
                    f"Action result data length: {len(action_result.get('data', []))}"
                )
                if action_result.get("data"):
                    first_item = action_result["data"][0]
                    print(f"First item type: {type(first_item)}")
                    if isinstance(first_item, dict):
                        print(f"First item keys: {first_item.keys()}")

        print("\n=== Testing customer listing ===")
        response2 = await agent.process_message("show me all customers")
        print(f"Response type: {type(response2)}")
        print(
            f"Response keys: {response2.keys() if isinstance(response2, dict) else 'Not a dict'}"
        )
        if isinstance(response2, dict):
            print(f"Message: {response2.get('message', 'No message')[:200]}...")
            if "action_result" in response2:
                action_result = response2["action_result"]
                print(f"Action result success: {action_result.get('success')}")
                print(
                    f"Action result data length: {len(action_result.get('data', []))}"
                )
                if action_result.get("data"):
                    first_item = action_result["data"][0]
                    print(f"First item type: {type(first_item)}")
                    if isinstance(first_item, dict):
                        print(f"First item keys: {first_item.keys()}")

    except Exception as e:
        print(f"Error during test: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await agent.stop()
        print("Test completed.")


if __name__ == "__main__":
    asyncio.run(test_grok_agent())
