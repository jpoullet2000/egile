#!/usr/bin/env python3
"""
Test the current customer creation behavior
"""

import asyncio
import sys
import os

# Set up the path and environment
sys.path.insert(0, "/home/jbp/projects/egile/chatbot-agent")
os.chdir("/home/jbp/projects/egile")


async def test_customer_scenarios():
    from grok_agent import GrokEcommerceAgent

    print("🔧 Testing current customer creation scenarios...")
    print("=" * 60)

    try:
        agent = GrokEcommerceAgent()
        await agent.start()

        test_cases = [
            "how can I create a new customer",
            "I'd like to create a new customer Pierre Dupont",
            "create customer John Smith with email john@test.com",
        ]

        for i, message in enumerate(test_cases, 1):
            print(f"\n{i}. Testing: '{message}'")
            print("-" * 40)

            try:
                result = await agent.process_message(message)
                print(f"✅ Action: {result.get('action')}")
                print(f"✅ Success: {result.get('success')}")

                message_text = result.get("message", "")
                if "step-by-step guidance" in message_text:
                    print("✅ Got help guidance")
                elif (
                    "Customer Details" in message_text
                    or "created successfully" in message_text
                ):
                    print("✅ Customer created")
                elif "Unknown action" in message_text:
                    print("❌ Unknown action error")
                elif "missing" in message_text:
                    print("❌ Missing parameter error")
                else:
                    print(f"ℹ️ Other response: {message_text[:100]}...")

            except Exception as e:
                print(f"❌ Error: {e}")

        await agent.stop()

    except Exception as e:
        print(f"❌ Setup error: {e}")


if __name__ == "__main__":
    asyncio.run(test_customer_scenarios())
