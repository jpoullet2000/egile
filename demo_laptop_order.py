#!/usr/bin/env python3
"""Demo script to create an order for 2 test laptops"""

import asyncio
import json
from egile.agent import EcommerceAgent


async def demo_laptop_order():
    """Demo: Create an order for 2 test laptops"""
    agent = EcommerceAgent()

    try:
        print("🚀 Starting Egile E-commerce Demo - Laptop Order")
        print("=" * 50)

        # Start the server
        print("Starting ecommerce server...")
        server_started = await agent.start_server()
        print(f"✅ Server started: {server_started}")

        if not server_started:
            print("❌ Failed to start server")
            return

        # Search for laptop products
        print("\n💻 Searching for laptop products...")
        products_response = await agent.search_products("laptop")

        if not products_response.success:
            print(f"❌ Failed to search products: {products_response.error}")
            return

        # Parse the response data
        laptops = []
        if products_response.data and len(products_response.data) > 0:
            text_data = products_response.data[0].get("text", "[]")
            try:
                laptops = json.loads(text_data)
            except json.JSONDecodeError:
                laptops = []

        print(f"Found {len(laptops)} laptop products:")
        for laptop in laptops:
            print(
                f"- {laptop.get('name', 'Unknown')} (ID: {laptop.get('id')}) - ${laptop.get('price', 0)}"
            )

        # If no laptops found, create a test laptop
        if not laptops:
            print("\n🛠️ Creating test laptop product...")
            create_response = await agent.create_product(
                name="Test Laptop Egile Pro",
                description="High-performance test laptop for demonstrations",
                price=999.99,
                category="Electronics",
                stock_quantity=50,
            )

            if create_response.success:
                # Parse creation response
                text_data = create_response.data[0].get("text", "{}")
                json_start = text_data.find("{")
                if json_start >= 0:
                    json_part = text_data[json_start:]
                    laptop_data = json.loads(json_part)
                    laptop_id = laptop_data.get("id")
                    print(f"✅ Created test laptop with ID: {laptop_id}")
                else:
                    print(f"Laptop created: {text_data}")
                    # Extract ID from response if possible
                    if "prod_" in text_data:
                        import re

                        match = re.search(r"prod_\d+", text_data)
                        laptop_id = match.group(0) if match else None
                    else:
                        laptop_id = None

                if not laptop_id:
                    print("❌ Could not determine laptop ID")
                    return
            else:
                print(f"❌ Failed to create laptop: {create_response.error}")
                return
        else:
            # Use the first laptop found
            laptop_id = laptops[0]["id"]
            laptop_name = laptops[0]["name"]
            print(f"\n📦 Using laptop: {laptop_name} (ID: {laptop_id})")

        # Get or create a customer
        print("\n👤 Finding customer...")
        customers_response = await agent.get_all_customers()

        customers = []
        if customers_response.success and customers_response.data:
            text_data = customers_response.data[0].get("text", "[]")
            try:
                customers = json.loads(text_data)
            except json.JSONDecodeError:
                customers = []

        if customers:
            customer_id = customers[0]["id"]
            customer_name = customers[0].get("name", "Unknown")
            print(f"✅ Using customer: {customer_name} (ID: {customer_id})")
        else:
            print("🛠️ Creating demo customer...")
            customer_response = await agent.create_customer(
                name="Demo Laptop Customer",
                email="laptop@egile.com",
                phone="555-0456",
                address="456 Demo Avenue, Test City, TC 54321",
            )

            if customer_response.success:
                text_data = customer_response.data[0].get("text", "{}")
                json_start = text_data.find("{")
                if json_start >= 0:
                    json_part = text_data[json_start:]
                    customer_data = json.loads(json_part)
                    customer_id = customer_data.get("id")
                    print(f"✅ Created customer with ID: {customer_id}")
                else:
                    print(f"❌ Could not parse customer creation response")
                    return
            else:
                print(f"❌ Failed to create customer: {customer_response.error}")
                return

        # Create order for 2 laptops
        print(f"\n🛒 Creating order for 2 test laptops...")

        # IMPORTANT: The create_order method expects:
        # - customer_id: string
        # - items: list of dictionaries with 'product_id' and 'quantity'
        # - currency: string (optional, defaults to "USD")

        order_items = [{"product_id": laptop_id, "quantity": 2}]

        order_response = await agent.create_order(
            customer_id=customer_id, items=order_items, currency="USD"
        )

        if order_response.success:
            print("🎉 ORDER CREATED SUCCESSFULLY!")
            print("=" * 40)

            # Parse the order response
            text_data = order_response.data[0].get("text", "")

            # Extract JSON from response (it usually has descriptive text before JSON)
            json_start = text_data.find("{")
            if json_start >= 0:
                json_part = text_data[json_start:]
                try:
                    order_data = json.loads(json_part)

                    print(f"Order ID: {order_data.get('id')}")
                    print(f"Customer ID: {order_data.get('customer_id')}")
                    print(f"Status: {order_data.get('status')}")
                    print(f"Total Amount: ${order_data.get('total_amount', 0)}")
                    print(f"Currency: {order_data.get('currency')}")
                    print(f"Created: {order_data.get('created_at')}")

                    print("\nOrder Items:")
                    for item in order_data.get("items", []):
                        print(f"  • Product ID: {item.get('product_id')}")
                        print(f"    Quantity: {item.get('quantity')}")
                        print(f"    Unit Price: ${item.get('unit_price', 0)}")
                        print(f"    Total: ${item.get('total_price', 0)}")

                    print(
                        f"\n✅ Successfully ordered 2 test laptops for ${order_data.get('total_amount', 0)}!"
                    )

                except json.JSONDecodeError:
                    print(f"Order created successfully!")
                    print(f"Response: {text_data}")
            else:
                print(f"Order created successfully!")
                print(f"Response: {text_data}")
        else:
            print(f"❌ Failed to create order: {order_response.error}")
            print(f"Response data: {order_response.data}")

    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback

        traceback.print_exc()

    finally:
        await agent.stop_server()
        print("\n🏁 Demo completed!")


if __name__ == "__main__":
    asyncio.run(demo_laptop_order())
