#!/usr/bin/env python3
"""Simple test for the interactive product creation logic"""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "chatbot-agent"))


def test_help_create_product():
    """Test the help_create_product method logic"""
    from grok_agent import GrokEcommerceAgent

    agent = GrokEcommerceAgent()

    print("=== Testing help_create_product method ===")

    # Test initial state
    print(f"Initial product_creation_state: {agent.product_creation_state}")

    # Test fallback intent analysis
    result = agent.fallback_intent_analysis("Help me create a new product")
    print(f"Intent analysis result: {result}")

    print("\n✅ Basic logic test completed!")


if __name__ == "__main__":
    test_help_create_product()
