#!/usr/bin/env python3
"""Test the enhanced order creation patterns"""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "chatbot-agent"))

from grok_agent import GrokEcommerceAgent


def test_order_patterns():
    """Test different order creation patterns"""
    agent = GrokEcommerceAgent()

    test_messages = [
        "create order for demo for 2 laptops",
        "create order for demo for 1 microphone",
        "place order for test for 3 headsets",
        "order 2 laptops for demo",
        "make order for john for 1 iphone",
        "create order customer: cust_000001 product: prod_000004 quantity: 2",
    ]

    print("🧪 Testing Order Creation Patterns")
    print("=" * 50)

    for message in test_messages:
        print(f"\n📝 Message: '{message}'")
        result = agent.fallback_intent_analysis(message)
        print(f"   Intent: {result.get('intent')}")
        print(f"   Action: {result.get('action')}")
        print(f"   Parameters: {result.get('parameters')}")
        print(f"   Requires Action: {result.get('requires_action')}")


if __name__ == "__main__":
    test_order_patterns()
