#!/usr/bin/env python3
"""Test parameter mapping directly"""

import asyncio
import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "chatbot-agent"))

from grok_agent import GrokEcommerceAgent


async def test_parameter_mapping():
    """Test that parameter mapping works correctly"""
    agent = GrokEcommerceAgent()

    try:
        await agent.start()

        # Create a test intent with unmapped parameters
        test_intent = {
            "action": "create_order",
            "parameters": {
                "customer_id": "demo",
                "items": [{"product_id": "laptop", "quantity": 2}],
                "currency": "USD",
            },
        }

        print("🧪 Testing Parameter Mapping")
        print("Before mapping:", test_intent["parameters"])

        # Execute the action (this should trigger parameter mapping)
        result = await agent.execute_ecommerce_action(test_intent)
        print("Result:", result)

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()

    finally:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(test_parameter_mapping())
