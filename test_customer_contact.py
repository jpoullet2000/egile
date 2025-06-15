#!/usr/bin/env python3
"""Test customer contact logic"""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "chatbot-agent"))


def test_customer_contact():
    """Test the customer contact pattern matching"""
    from grok_agent import GrokEcommerceAgent

    agent = GrokEcommerceAgent()

    test_messages = [
        "how can I contact the customer?",
        "how to contact customer john@example.com?",
        "contact customer cust_123",
        "customer contact info",
        "get customer details for sarah@company.com",
    ]

    for message in test_messages:
        print(f"\n=== Testing: {message} ===")
        result = agent.fallback_intent_analysis(message)
        print(f"Intent: {result.get('intent')}")
        print(f"Action: {result.get('action')}")
        print(f"Parameters: {result.get('parameters')}")
        print(f"Requires action: {result.get('requires_action')}")


if __name__ == "__main__":
    test_customer_contact()
