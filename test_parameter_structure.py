#!/usr/bin/env python3
"""
Test the fixed parameter structure for get_customer
"""

import sys
import re
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the GrokEcommerceAgent class to test the fallback logic
import importlib.util

spec = importlib.util.spec_from_file_location(
    "grok_agent", "chatbot-agent/grok_agent.py"
)
grok_agent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grok_agent)


def test_fallback_logic():
    """Test the fallback intent analysis for customer contact queries"""
    agent = grok_agent.GrokEcommerceAgent()

    # Test messages
    test_messages = [
        "contact demo@example.com",
        "customer details for demo@example.com",
        "get customer info for demo@example.com",
        "what is the cheapest product",
    ]

    for message in test_messages:
        print(f"\n--- Testing: '{message}' ---")
        result = agent.fallback_intent_analysis(message)
        print(f"Intent: {result.get('intent')}")
        print(f"Action: {result.get('action')}")
        print(f"Parameters: {result.get('parameters')}")
        print(f"Confidence: {result.get('confidence')}")


if __name__ == "__main__":
    test_fallback_logic()
