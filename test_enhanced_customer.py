#!/usr/bin/env python3
"""
Test the improved customer creation handling for incomplete requests
"""

import asyncio
import sys
import os

# Set up the path and environment
sys.path.insert(0, "/home/jbp/projects/egile/chatbot-agent")
os.chdir("/home/jbp/projects/egile")


async def test_incomplete_customer_requests():
    from grok_agent import GrokEcommerceAgent

    print("🔧 Testing incomplete customer creation requests...")
    print("=" * 60)

    try:
        agent = GrokEcommerceAgent()
        await agent.start()

        test_cases = [
            "I'd like to create a new customer",
            "I want to create a customer",
            "create a new customer",
            "add a new customer",
        ]

        for i, message in enumerate(test_cases, 1):
            print(f"\n{i}. Testing: '{message}'")
            print("-" * 40)

            # Test fallback intent analysis directly first
            try:
                intent = await agent.fallback_intent_analysis(message)
                print(f"📋 Intent Analysis:")
                print(f"   Action: {intent.get('action')}")
                print(f"   Intent: {intent.get('intent')}")
                print(f"   Confidence: {intent.get('confidence')}")

                # Check if it routes to help
                if intent.get("action") == "help_create_customer":
                    print("   ✅ CORRECT: Routes to help_create_customer")
                elif intent.get("action") == "create_customer":
                    print("   ❌ WRONG: Routes to create_customer (will cause error)")
                else:
                    print(f"   ❓ UNKNOWN: Routes to {intent.get('action')}")

            except Exception as e:
                print(f"   ❌ Intent analysis error: {e}")

            # Test full message processing
            try:
                result = await agent.process_message(message)
                print(f"📤 Full Processing:")
                print(f"   Action: {result.get('action')}")
                print(f"   Success: {result.get('success')}")

                message_text = result.get("message", "")
                if (
                    "step-by-step guidance" in message_text
                    or "help you create" in message_text
                ):
                    print("   ✅ CORRECT: Got customer help guidance!")
                elif "missing" in message_text and (
                    "email" in message_text or "arguments" in message_text
                ):
                    print("   ❌ WRONG: Got error about missing fields")
                elif "Try asking me to" in message_text:
                    print("   ❌ WRONG: Got generic fallback response")
                else:
                    print("   ❓ UNKNOWN: Got different response")

            except Exception as e:
                print(f"   ❌ Processing error: {e}")

        await agent.stop()

    except Exception as e:
        print(f"❌ Setup error: {e}")


if __name__ == "__main__":
    asyncio.run(test_incomplete_customer_requests())
