#!/usr/bin/env python3
"""
Test that stock updates work with dynamic product mapping.
"""

import asyncio
import sys

sys.path.append("/home/jbp/projects/egile/chatbot-agent")
from grok_agent import GrokEcommerceAgent


async def test_stock_update_dynamic():
    agent = GrokEcommerceAgent()
    await agent.start()

    try:
        print("🧪 Testing stock updates with dynamic mapping...\n")

        # Test stock updates for various products
        test_commands = [
            "update stock for gaming headset to 100",
            "increase stock for laptop by 20",
            "set microphone stock to 75",
            "add 30 to usb drive stock",
            "increase wireless keyboard stock by 25",  # This should use the newly created product
        ]

        for i, command in enumerate(test_commands, 1):
            print(f"🧪 Test {i}: '{command}'")
            response = await agent.process_message(command)

            message = response.get("message", "")
            if (
                "Stock updated successfully" in message
                or "successfully updated" in message
            ):
                print("   ✅ Stock update succeeded")
            else:
                print(f"   ⚠️ Response: {message[:100]}...")

            print()  # Empty line

        # Test listing products to see current stock levels
        print("📦 Checking current stock levels...")
        stock_response = await agent.process_message("show me all products")
        print(f"Stock info: {stock_response.get('message', '')[:200]}...")

    finally:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(test_stock_update_dynamic())
