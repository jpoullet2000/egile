#!/usr/bin/env python3
"""
Debug the specific gaming headset pro order issue.
"""

import asyncio
import sys

sys.path.append("/home/jbp/projects/egile/chatbot-agent")
from grok_agent import GrokEcommerceAgent


async def debug_gaming_headset():
    agent = GrokEcommerceAgent()
    await agent.start()

    try:
        print("🔍 Debug: 'create order for 2 gaming headset pro for demo user'")
        response = await agent.process_message(
            "create order for 2 gaming headset pro for demo user"
        )

        intent = response.get("intent", {})
        params = intent.get("parameters", {})
        action_result = response.get("action_result", {})

        print(f"\n📋 Intent Analysis:")
        print(f"   Action: {intent.get('action')}")
        print(f"   Parameters: {params}")

        print(f"\n📤 Action Result:")
        print(f"   Success: {action_result.get('success')}")
        print(f"   Data: {action_result.get('data', [])[:1]}")  # Show first item only
        print(f"   Error: {action_result.get('error', 'None')}")

        message = response.get("message", "")
        print(f"\n📄 Response Message:\n{message}")

    finally:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(debug_gaming_headset())
