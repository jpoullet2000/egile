#!/usr/bin/env python3
"""Debug order creation response"""

import asyncio
import sys
from pathlib import Path

from egile.agent import EcommerceAgent


async def debug_order():
    agent = EcommerceAgent()

    try:
        print("Starting server...")
        await agent.start_server()

        # Create order for debugging
        order_items = [{"product_id": "prod_000010", "quantity": 2}]

        order_response = await agent.create_order(
            customer_id="cust_000001", items=order_items, currency="USD"
        )

        print(f"Order response success: {order_response.success}")
        print(f"Order response data: {order_response.data}")
        print(f"Order response message: {order_response.message}")
        print(f"Order response error: {order_response.error}")

        if order_response.data:
            print(f"Data type: {type(order_response.data)}")
            print(f"Data length: {len(order_response.data)}")
            if len(order_response.data) > 0:
                print(f"First item: {order_response.data[0]}")
                if isinstance(order_response.data[0], dict):
                    print(
                        f"Text content: {order_response.data[0].get('text', 'No text')}"
                    )

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await agent.stop_server()


if __name__ == "__main__":
    asyncio.run(debug_order())
