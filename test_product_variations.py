#!/usr/bin/env python3
"""
Test various ways to reference Test Laptop vs Laptop Pro
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "chatbot-agent"))

from grok_agent import GrokEcommerceAgent


async def test_product_variations():
    """Test various ways to reference the products"""
    agent = GrokEcommerceAgent()

    try:
        await agent.start()
        print("✅ Agent started successfully")

        test_cases = [
            ('update stock of "Test Laptop" by 5', "prod_000008", "Test Laptop"),
            ("update Test Laptop stock by 3", "prod_000008", "Test Laptop"),
            ("update stock test laptop by 2", "prod_000008", "Test Laptop"),
            ('update stock of "Laptop Pro" by 7', "prod_000004", "Laptop Pro"),
            ("update Laptop Pro stock by 4", "prod_000004", "Laptop Pro"),
            ("update stock laptop pro by 1", "prod_000004", "Laptop Pro"),
            (
                "update stock laptop by 6",
                "prod_000004",
                "Laptop Pro (fallback)",
            ),  # This should go to Laptop Pro as fallback
        ]

        for command, expected_product_id, description in test_cases:
            print(f"\n{'=' * 60}")
            print(f"Testing: {command}")
            print(f"Expected to update: {description} ({expected_product_id})")
            print(f"{'=' * 60}")

            response = await agent.process_message(command)
            print(f"Response: {response.get('message', 'No message')}")

            # Check if the response mentions the correct product ID
            if expected_product_id in response.get("message", ""):
                print("✅ CORRECT: Updated the right product")
            else:
                print("❌ INCORRECT: Updated wrong product or unclear response")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(test_product_variations())
