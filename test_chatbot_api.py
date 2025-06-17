#!/usr/bin/env python3
import requests
import json
import time


def test_customer_help():
    """Test customer help via the running chatbot API"""

    # Wait a moment for the server to be fully ready
    time.sleep(2)

    # Test URL
    url = "http://localhost:8081/chat"

    test_messages = ["how to create a customer", "help me create a customer"]

    print("🔍 Testing customer help via chatbot API:")
    print("=" * 50)

    for message in test_messages:
        try:
            print(f"\n📤 Sending: '{message}'")

            response = requests.post(
                url,
                json={"message": message},
                headers={"Content-Type": "application/json"},
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                print("📥 Response:")
                print(f"   Success: {data.get('success')}")
                print(f"   Action: {data.get('action')}")
                message_text = data.get("message", "")

                # Check if it's the help message
                if (
                    "step-by-step guidance" in message_text
                    or "help you create" in message_text
                ):
                    print("   ✅ CORRECT: Got customer help guidance!")
                elif "missing" in message_text and "email" in message_text:
                    print(
                        "   ❌ WRONG: Got error about missing email (tried to create customer)"
                    )
                elif "Try asking me to" in message_text:
                    print("   ❌ WRONG: Got generic fallback response")
                else:
                    print("   ❓ UNKNOWN: Got different response")

                # Show first part of message
                print(f"   Message: {message_text[:150]}...")

            else:
                print(f"   ❌ HTTP Error: {response.status_code}")

        except Exception as e:
            print(f"   ❌ Exception: {e}")


if __name__ == "__main__":
    test_customer_help()
