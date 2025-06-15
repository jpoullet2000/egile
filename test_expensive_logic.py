#!/usr/bin/env python3
"""Test expensive products logic"""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "chatbot-agent"))

def test_expensive_products():
    """Test the expensive products pattern matching"""
    from grok_agent import GrokEcommerceAgent
    
    agent = GrokEcommerceAgent()
    
    test_messages = [
        "what are the most expensive products?",
        "show me most expensive products",
        "what are my priciest items?",
        "top 5 most expensive products"
    ]
    
    for message in test_messages:
        print(f"\n=== Testing: {message} ===")
        result = agent.fallback_intent_analysis(message)
        print(f"Intent: {result.get('intent')}")
        print(f"Action: {result.get('action')}")
        print(f"Parameters: {result.get('parameters')}")
        print(f"Requires action: {result.get('requires_action')}")

if __name__ == "__main__":
    test_expensive_products()
