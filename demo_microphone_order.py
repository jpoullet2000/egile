#!/usr/bin/env python3
"""Demo script to create an order for 2 microphones"""

import asyncio
import sys
from pathlib import Path

from egile.agent import EcommerceAgent

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "chatbot-agent"))


async def demo_microphone_order():
    """Demo: Create an order for 2 microphones"""
    agent = EcommerceAgent()

    try:
        # Start the server
        print("Starting ecommerce server...")
        server_started = await agent.start_server()
        print(f"Server started: {server_started}")

        if not server_started:
            print("Failed to start server")
            return

        # First, let's find microphone products
        print("\n=== Searching for microphone products ===")
        products_response = await agent.search_products("microphone")

        if not products_response.success:
            print(f"Failed to search products: {products_response.error}")
            return

        # Parse the response data which comes as a list with text content
        microphones = []
        if products_response.data and len(products_response.data) > 0:
            import json

            text_data = products_response.data[0].get("text", "[]")
            try:
                microphones = json.loads(text_data)
            except json.JSONDecodeError:
                microphones = []

        print(f"Found {len(microphones)} microphone products:")

        for product in microphones:
            print(
                f"- {product.get('name', 'Unknown')} (ID: {product.get('id')}) - ${product.get('price', 0)}"
            )

        # If no microphones found, create one for demo
        if not microphones:
            print("\n=== Creating demo microphone product ===")
            create_response = await agent.create_product(
                name="Egile Professional Microphone",
                description="High-quality professional microphone for recording and streaming",
                price=199.99,
                category="Electronics",
                stock_quantity=50,
            )

            if create_response.success:
                microphone_id = create_response.data.get("id")
                print(f"Created microphone product with ID: {microphone_id}")
            else:
                print(f"Failed to create product: {create_response.error}")
                return
        else:
            # Use the first microphone found
            microphone_id = microphones[0]["id"]
            print(f"\nUsing microphone: {microphones[0]['name']} (ID: {microphone_id})")

        # Get or create a customer for the demo
        print("\n=== Finding or creating demo customer ===")
        customers_response = await agent.get_all_customers()

        customers = []
        if customers_response.success and customers_response.data:
            # Parse the response data which comes as a list with text content
            if len(customers_response.data) > 0:
                import json

                text_data = customers_response.data[0].get("text", "[]")
                try:
                    customers = json.loads(text_data)
                except json.JSONDecodeError:
                    customers = []

        if customers:
            # Use the first customer
            customer_id = customers[0]["id"]
            customer_name = customers[0].get("name", "Unknown")
            print(f"Using existing customer: {customer_name} (ID: {customer_id})")
        else:
            # Create a demo customer
            print("Creating demo customer...")
            customer_response = await agent.create_customer(
                name="Demo Customer",
                email="demo@egile.com",
                phone="555-0123",
                address="123 Demo Street, Demo City, DC 12345",
            )

            if customer_response.success:
                # Parse the customer creation response
                if customer_response.data and len(customer_response.data) > 0:
                    import json

                    text_data = customer_response.data[0].get("text", "{}")
                    try:
                        customer_data = json.loads(text_data)
                        customer_id = customer_data.get("id")
                    except json.JSONDecodeError:
                        print("Failed to parse customer creation response")
                        return
                else:
                    print("No customer data returned")
                    return
                print(f"Created customer with ID: {customer_id}")
            else:
                print(f"Failed to create customer: {customer_response.error}")
                return

        # Create the order for 2 microphones
        print("\n=== Creating order for 2 microphones ===")
        order_items = [{"product_id": microphone_id, "quantity": 2}]

        order_response = await agent.create_order(
            customer_id=customer_id, items=order_items, currency="USD"
        )

        if order_response.success:
            # Parse the order creation response
            import json

            if order_response.data and len(order_response.data) > 0:
                text_data = order_response.data[0].get("text", "{}")

                # The response might have descriptive text before JSON, extract JSON part
                json_start = text_data.find("{")
                if json_start >= 0:
                    json_part = text_data[json_start:]
                    try:
                        order_data = json.loads(json_part)
                    except json.JSONDecodeError:
                        print(f"Order creation response: {text_data}")
                        print(
                            "✅ Order created successfully (response format not parseable as JSON)"
                        )
                        return
                else:
                    print(f"Order creation response: {text_data}")
                    if "Order created" in text_data or "order_" in text_data:
                        print("✅ Order created successfully!")
                    return
            else:
                print("No order data returned")
                return

            print("✅ Order created successfully!")
            print(f"Order ID: {order_data.get('id')}")
            print(f"Customer ID: {customer_id}")
            print(f"Items: 2x Microphone (Product ID: {microphone_id})")
            print(f"Total: ${order_data.get('total_amount', 0)}")
            print(f"Status: {order_data.get('status', 'Unknown')}")

            # Display the order details
            print("\n=== Order Details ===")
            order_id = order_data.get("id")
            order_details = await agent.get_order(order_id)

            if order_details.success:
                # Parse the order details response
                if order_details.data and len(order_details.data) > 0:
                    text_data = order_details.data[0].get("text", "{}")
                    try:
                        details = json.loads(text_data)
                    except json.JSONDecodeError:
                        print("Failed to parse order details response")
                        return
                else:
                    print("No order details returned")
                    return

                print(f"Order ID: {details.get('id')}")
                print(f"Customer: {details.get('customer_name', 'Unknown')}")
                print(f"Status: {details.get('status')}")
                print(f"Total: ${details.get('total')}")
                print("Items:")
                for item in details.get("items", []):
                    print(
                        f"  - {item.get('product_name')} x{item.get('quantity')} @ ${item.get('price')} each"
                    )
                print(f"Created: {details.get('created_at')}")

        else:
            print(f"❌ Failed to create order: {order_response.error}")

    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Stop the server
        await agent.stop_server()
        print("\nDemo completed.")


if __name__ == "__main__":
    asyncio.run(demo_microphone_order())
