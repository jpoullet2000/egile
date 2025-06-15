#!/usr/bin/env python3
"""
Test the new order creation help functionality
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the GrokEcommerceAgent class
import importlib.util

spec = importlib.util.spec_from_file_location(
    "grok_agent", "chatbot-agent/grok_agent.py"
)
grok_agent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grok_agent)


def test_order_creation_patterns():
    """Test the order creation intent analysis"""
    agent = grok_agent.GrokEcommerceAgent()

    # Test messages
    test_messages = [
        "how to create a new order",
        "help me create order",
        "new order",
        "create order customer: john@example.com product: laptop quantity: 2",
        "place order for customer 1 with 3 of product 5",
    ]

    for message in test_messages:
        print(f"\n--- Testing: '{message}' ---")
        result = agent.fallback_intent_analysis(message)
        print(f"Intent: {result.get('intent')}")
        print(f"Action: {result.get('action')}")
        print(f"Parameters: {result.get('parameters')}")
        print(f"Confidence: {result.get('confidence')}")


if __name__ == "__main__":
    test_order_creation_patterns()
