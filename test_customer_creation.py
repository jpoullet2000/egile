#!/usr/bin/env python3
"""
Test customer creation functionality - checking if we can create customers
when only a name is provided (without email).
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the agent - need to navigate to correct path
sys.path.append("/home/jbp/projects/egile/chatbot-agent")
from grok_agent import GrokAgent


async def test_customer_creation():
    """Test various customer creation scenarios"""
    agent = GrokAgent()

    print("🧪 Testing Customer Creation Scenarios...")
    print("=" * 60)

    # Test cases
    test_cases = [
        "create a new customer John Doe",
        "add customer Jane Smith",
        "create customer for Bob Wilson",
        "I want to add a new customer Mary Johnson",
        "new customer: Alice Brown",
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: '{test_case}'")
        print("-" * 40)

        try:
            # First check intent analysis
            intent_result = await agent.analyze_user_intent(test_case)
            print(f"Intent: {intent_result}")

            # Then try full processing
            result = await agent.process_user_message(test_case)
            print(f"Result: {result}")

        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback

            traceback.print_exc()

        print("-" * 40)


if __name__ == "__main__":
    asyncio.run(test_customer_creation())
