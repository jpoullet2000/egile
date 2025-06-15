#!/usr/bin/env python3
"""Test interactive product creation"""

import asyncio
import sys
import signal
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "chatbot-agent"))

from grok_agent import GrokEcommerceAgent


async def test_interactive_creation():
    """Test the interactive product creation flow"""
    agent = GrokEcommerceAgent()

    try:
        print("Starting ecommerce agent...")
        await agent.start()
        print("Agent started successfully!")

        # Start product creation
        print("\n=== Starting interactive product creation ===")
        response1 = await agent.process_message("Help me create a new product")
        print(f"Step 1 - Response: {response1.get('message', 'No message')[:200]}...")

        # Step 1: Name
        print("\n=== Providing product name ===")
        response2 = await agent.process_message("Gaming Headset Pro")
        print(f"Step 2 - Response: {response2.get('message', 'No message')[:200]}...")

        # Step 2: Description
        print("\n=== Providing description ===")
        response3 = await agent.process_message(
            "Premium wireless gaming headset with noise cancellation"
        )
        print(f"Step 3 - Response: {response3.get('message', 'No message')[:200]}...")

        # Step 3: Price
        print("\n=== Providing price ===")
        response4 = await agent.process_message("149.99")
        print(f"Step 4 - Response: {response4.get('message', 'No message')[:200]}...")

        # Step 4: SKU
        print("\n=== Providing SKU ===")
        response5 = await agent.process_message("GH-PRO-001")
        print(f"Step 5 - Response: {response5.get('message', 'No message')[:200]}...")

        # Step 5: Category
        print("\n=== Providing category ===")
        response6 = await agent.process_message("Electronics")
        print(f"Step 6 - Response: {response6.get('message', 'No message')[:200]}...")

        # Step 6: Stock
        print("\n=== Providing stock quantity ===")
        response7 = await agent.process_message("25")
        print(f"Final - Response: {response7.get('message', 'No message')[:400]}...")
        print(f"Response type: {response7.get('type')}")

        print("\n✅ Interactive product creation test completed!")

    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback

        traceback.print_exc()
    finally:
        print("Stopping agent...")
        await agent.stop()
        print("Agent stopped.")


if __name__ == "__main__":
    asyncio.run(test_interactive_creation())
