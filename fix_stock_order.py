#!/usr/bin/env python3
"""Fix stock and create order"""

import asyncio
import json
from egile.agent import EcommerceAgent


async def fix_stock_and_create_order():
    agent = EcommerceAgent()

    try:
        print("Starting server...")
        await agent.start_server()

        # Check current stock
        print("\n=== Checking microphone stock ===")
        product_response = await agent.get_product("prod_000010")
        if product_response.success and product_response.data:
            text_data = product_response.data[0].get("text", "{}")
            try:
                product_data = json.loads(text_data)
                current_stock = product_data.get("stock_quantity", 0)
                print(f"Current stock: {current_stock}")

                if current_stock < 2:
                    print(f"Updating stock to 50...")
                    stock_response = await agent.update_stock("prod_000010", 50, "set")
                    print(f"Stock update result: {stock_response.success}")
                    if not stock_response.success:
                        print(f"Stock update error: {stock_response.error}")

            except json.JSONDecodeError:
                print("Failed to parse product data")

        # Now try to create the order
        print("\n=== Creating order for 2 microphones ===")
        order_items = [{"product_id": "prod_000010", "quantity": 2}]

        order_response = await agent.create_order(
            customer_id="cust_000001", items=order_items, currency="USD"
        )

        print(f"Order creation success: {order_response.success}")

        if order_response.success:
            if order_response.data and len(order_response.data) > 0:
                text_data = order_response.data[0].get("text", "")
                print(f"Response text: {text_data}")

                # Try to parse as JSON
                try:
                    order_data = json.loads(text_data)
                    print("✅ Order created successfully!")
                    print(f"Order ID: {order_data.get('id', 'Unknown')}")
                    print(f"Total: ${order_data.get('total', 0)}")
                    print(f"Status: {order_data.get('status', 'Unknown')}")
                except json.JSONDecodeError:
                    # If it's not JSON, it might be an error message
                    print(f"Order creation message: {text_data}")
        else:
            print(f"Order creation failed: {order_response.error}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await agent.stop_server()
        print("\nDone.")


if __name__ == "__main__":
    asyncio.run(fix_stock_and_create_order())
