#!/usr/bin/env python3
"""Final working demo - Create order for 2 microphones"""

import asyncio
import json
from egile.agent import EcommerceAgent


async def create_microphone_order():
    """Create an order for 2 Egile microphones"""
    agent = EcommerceAgent()

    try:
        print("🚀 Starting Egile E-commerce Demo")
        print("=" * 40)

        # Start the server
        print("Starting ecommerce server...")
        await agent.start_server()
        print("✅ Server started successfully!")

        # Find microphone products
        print("\n📦 Finding microphone products...")
        products_response = await agent.search_products("microphone")

        if products_response.success and products_response.data:
            text_data = products_response.data[0].get("text", "[]")
            microphones = json.loads(text_data)

            if microphones:
                microphone = microphones[0]
                microphone_id = microphone["id"]
                microphone_name = microphone["name"]
                microphone_price = microphone["price"]

                print(
                    f"Found: {microphone_name} (ID: {microphone_id}) - ${microphone_price}"
                )
            else:
                print("No microphone products found")
                return
        else:
            print("Failed to search for products")
            return

        # Get customer
        print("\n👤 Finding customer...")
        customers_response = await agent.get_all_customers()

        if customers_response.success and customers_response.data:
            text_data = customers_response.data[0].get("text", "[]")
            customers = json.loads(text_data)

            if customers:
                customer = customers[0]
                customer_id = customer["id"]
                print(f"Using customer ID: {customer_id}")
            else:
                print("No customers found")
                return
        else:
            print("Failed to get customers")
            return

        # Create the order
        print(f"\n🛒 Creating order for 2x {microphone_name}...")
        order_items = [{"product_id": microphone_id, "quantity": 2}]

        order_response = await agent.create_order(
            customer_id=customer_id, items=order_items, currency="USD"
        )

        if order_response.success:
            text_data = order_response.data[0].get("text", "")

            # Extract JSON from response
            json_start = text_data.find("{")
            if json_start >= 0:
                json_part = text_data[json_start:]
                order_data = json.loads(json_part)

                print("🎉 ORDER CREATED SUCCESSFULLY!")
                print("=" * 40)
                print(f"Order ID: {order_data['id']}")
                print(f"Customer ID: {order_data['customer_id']}")
                print(f"Status: {order_data['status']}")
                print(f"Total Amount: ${order_data['total_amount']}")
                print(f"Currency: {order_data['currency']}")
                print(f"Created: {order_data['created_at']}")

                print("\nOrder Items:")
                for item in order_data["items"]:
                    print(f"  • Product ID: {item['product_id']}")
                    print(f"    Quantity: {item['quantity']}")
                    print(f"    Unit Price: ${item['unit_price']}")
                    print(f"    Total: ${item['total_price']}")

                print(
                    f"\n✅ Successfully ordered 2 Egile microphones for ${order_data['total_amount']}!"
                )

            else:
                print(f"Order created with response: {text_data}")
        else:
            print(f"❌ Order creation failed: {order_response.error}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()

    finally:
        await agent.stop_server()
        print("\n🏁 Demo completed!")


if __name__ == "__main__":
    asyncio.run(create_microphone_order())
