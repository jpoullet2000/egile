#!/usr/bin/env python3
"""Test customer contact fix quickly"""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "chatbot-agent"))


def test_customer_contact_intent():
    """Test that customer contact intent is detected correctly"""
    from grok_agent import GrokEcommerceAgent

    agent = GrokEcommerceAgent()

    test_message = "how can I contact him?"

    print(f"Testing: {test_message}")
    result = agent.fallback_intent_analysis(test_message)
    print(f"Intent: {result.get('intent')}")
    print(f"Action: {result.get('action')}")
    print(f"Parameters: {result.get('parameters')}")
    print(f"Requires action: {result.get('requires_action')}")

    # Check if it's correctly identifying as help_choose_customer_contact
    expected_action = "help_choose_customer_contact"
    if result.get("action") == expected_action:
        print(f"✅ Correctly identified as {expected_action}")
    else:
        print(f"❌ Expected {expected_action}, got {result.get('action')}")


if __name__ == "__main__":
    test_customer_contact_intent()
