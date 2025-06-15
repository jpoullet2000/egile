#!/usr/bin/env python3
"""Integration test for product creation"""

import asyncio
import sys
import signal
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "chatbot-agent"))

from grok_agent import GrokEcommerceAgent


async def test_integration():
    """Test actual product creation with the agent"""
    agent = GrokEcommerceAgent()

    # Set up signal handler for clean shutdown
    def signal_handler(signum, frame):
        print("\nShutting down...")
        asyncio.create_task(agent.stop())
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        print("Starting ecommerce agent...")
        await agent.start()
        print("Agent started successfully!")

        # Test 1: Ask for help creating a product
        print("\n=== Test 1: Asking for help ===")
        response1 = await agent.process_message("Help me create a new product")
        print(f"Response type: {response1.get('type', 'unknown')}")
        print(f"Message preview: {response1.get('message', 'No message')[:300]}...")

        # Test 2: Create a product with all details
        print("\n=== Test 2: Creating product with details ===")
        response2 = await agent.process_message(
            'Create product "Test Laptop" with description "Gaming laptop for testing", price $1299.99, SKU TL-2024-001, category Electronics, stock 5'
        )
        print(f"Response type: {response2.get('type', 'unknown')}")
        print(f"Message preview: {response2.get('message', 'No message')[:300]}...")

        # Test 3: List products to see if it was created
        print("\n=== Test 3: Listing products ===")
        response3 = await agent.process_message("show me all products")
        print(f"Response type: {response3.get('type', 'unknown')}")
        print(f"Message preview: {response3.get('message', 'No message')[:300]}...")

        print("\n✅ All tests completed successfully!")

    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback

        traceback.print_exc()
    finally:
        print("Stopping agent...")
        await agent.stop()
        print("Agent stopped.")


if __name__ == "__main__":
    asyncio.run(test_integration())
