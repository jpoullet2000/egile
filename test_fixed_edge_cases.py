#!/usr/bin/env python3
"""
Test the specific edge cases that were failing before
"""

import asyncio
import sys
import sqlite3
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "chatbot-agent"))

from grok_agent import GrokEcommerceAgent


async def test_fixed_edge_cases():
    """Test the edge cases that were failing before"""
    agent = GrokEcommerceAgent()

    try:
        await agent.start()
        print("✅ Agent started successfully")

        # Set initial stock
        await agent.process_message("update stock laptop to 100")
        print("🔧 Set initial stock to 100")

        # Test the cases that were failing
        test_cases = [
            "add 10 to laptop stock",
            "update stock laptop plus 7",
        ]

        for command in test_cases:
            print(f"\n{'=' * 60}")
            print(f"Testing: {command}")
            print(f"{'=' * 60}")

            response = await agent.process_message(command)
            print(f"Response: {response.get('message', 'No message')}")

            if "error" in response.get("message", "").lower():
                print("❌ Still has errors")
            else:
                print("✅ No errors!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(test_fixed_edge_cases())
