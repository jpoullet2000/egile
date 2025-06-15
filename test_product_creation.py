#!/usr/bin/env python3
"""Quick test for product creation logic"""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "chatbot-agent"))

from grok_agent import GrokEcommerceAgent


def test_intent_analysis():
    """Test the intent analysis for product creation"""
    agent = GrokEcommerceAgent()

    # Test cases
    test_messages = [
        "Help me create a new product",
        "I want to add a product",
        'Create product "iPhone 15" 999.99 IP15-128 Electronics 50',
        'Create product "Test Phone" with description "Test smartphone", price $199.99, SKU TP-001, category Electronics, stock 10',
    ]

    for message in test_messages:
        print(f"\n=== Testing: {message} ===")
        try:
            result = agent.fallback_intent_analysis(message)
            print(f"Intent: {result.get('intent')}")
            print(f"Action: {result.get('action')}")
            print(f"Parameters: {result.get('parameters')}")
            print(f"Requires action: {result.get('requires_action')}")

            # Test parameter extraction separately
            if result.get("action") in ["create_product", "request_product_details"]:
                params = agent.extract_product_params(message)
                print(f"Extracted params: {params}")

        except Exception as e:
            print(f"Error: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    test_intent_analysis()
