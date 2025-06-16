#!/usr/bin/env python3
"""Direct order creation test."""

import asyncio
import sys
import os

# Add project directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "egile"))

from egile.agent import EcommerceAgent


async def direct_order_test():
    """Test direct order creation using MCP agent."""
    agent = EcommerceAgent()

    try:
        success = await agent.start_server()
        if not success:
            print("Failed to start server")
            return

        print("Server started successfully")

        # First, find the microphone product
        print("1. Searching for microphone product...")
        search_result = await agent.search_products("microphone")
        if not search_result.success or not search_result.data:
            print("Failed to find microphone product")
            return

        microphone = search_result.data[0]
        print(f"Found microphone: {microphone['name']} (ID: {microphone['id']})")

        # Create an order for demo customer
        print("2. Creating order...")
        order_result = await agent.create_order(
            customer_id="cust_000001",  # demo@example.com
            items=[{"product_id": microphone["id"], "quantity": 2}],
        )

        if order_result.success:
            print("✅ Order created successfully!")
            print(f"Order data: {order_result.data}")
        else:
            print(f"❌ Order creation failed: {order_result.error}")

    finally:
        await agent.stop_server()


if __name__ == "__main__":
    asyncio.run(direct_order_test())
