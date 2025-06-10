#!/usr/bin/env python3
"""
Simple CLI interface for the E-commerce Agent

Provides an interactive command-line interface to interact with the e-commerce
MCP server through the agent.
"""

import asyncio
import json
from typing import List
from .agent import EcommerceAgent, AgentResponse


class EcommerceCLI:
    """Command-line interface for the e-commerce agent."""

    def __init__(self):
        self.agent = EcommerceAgent()
        self.is_running = False

    async def start(self):
        """Start the CLI and the MCP server."""
        print("Starting E-commerce CLI...")
        print("Connecting to MCP server...")

        if not await self.agent.start_server():
            print("❌ Failed to start MCP server")
            return

        # Wait for server initialization
        await asyncio.sleep(2)

        print("✅ Connected to E-commerce MCP Server")
        print("Type 'help' for available commands or 'quit' to exit\n")

        self.is_running = True
        await self.run_cli()

    async def stop(self):
        """Stop the CLI and server."""
        print("\nShutting down...")
        await self.agent.stop_server()
        self.is_running = False

    async def run_cli(self):
        """Main CLI loop."""
        while self.is_running:
            try:
                command = input("ecommerce> ").strip()
                if not command:
                    continue

                await self.handle_command(command)

            except KeyboardInterrupt:
                await self.stop()
                break
            except EOFError:
                await self.stop()
                break

    async def handle_command(self, command: str):
        """Handle a CLI command."""
        parts = command.split()
        if not parts:
            return

        cmd = parts[0].lower()

        if cmd == "help":
            self.show_help()
        elif cmd == "quit" or cmd == "exit":
            await self.stop()
        elif cmd == "create":
            await self.handle_create(parts[1:])
        elif cmd == "get":
            await self.handle_get(parts[1:])
        elif cmd == "search":
            await self.handle_search(parts[1:])
        elif cmd == "update":
            await self.handle_update(parts[1:])
        elif cmd == "order":
            await self.handle_order(parts[1:])
        elif cmd == "stock":
            await self.handle_stock(parts[1:])
        elif cmd == "list":
            await self.handle_list(parts[1:])
        elif cmd == "demo":
            await self.run_demo()
        else:
            print(f"Unknown command: {cmd}. Type 'help' for available commands.")

    def show_help(self):
        """Show available commands."""
        help_text = """
Available Commands:

Product Management:
  create product <name> <price> <sku> <category> <stock>  - Create a new product
  get product <id_or_sku>                                 - Get product details
  search products <query>                                 - Search products
  update product <id> <field> <value>                    - Update product field

Customer Management:
  create customer <email> <first_name> <last_name>       - Create customer
  get customer <id_or_email>                             - Get customer details

Order Management:
  order create <customer_id> <product_id> <quantity>     - Create simple order
  order get <order_id>                                   - Get order details
  order status <order_id> <status>                       - Update order status

Inventory:
  stock update <product_id> <quantity>                   - Set stock quantity
  stock low [threshold]                                  - Show low stock items
  stock restock [quantity]                               - Restock low items

Data Access:
  list products                                          - List all products
  list customers                                         - List all customers
  list orders                                            - List all orders

Other:
  demo                                                   - Run demonstration
  help                                                   - Show this help
  quit/exit                                              - Exit the CLI
        """
        print(help_text)

    async def handle_create(self, args: List[str]):
        """Handle create commands."""
        if not args:
            print("Usage: create <type> <args...>")
            return

        entity_type = args[0].lower()

        if entity_type == "product":
            if len(args) < 6:
                print("Usage: create product <name> <price> <sku> <category> <stock>")
                return

            name = args[1]
            try:
                price = float(args[2])
                stock = int(args[5])
            except ValueError:
                print("Price must be a number and stock must be an integer")
                return

            sku = args[3]
            category = args[4]
            description = f"{name} - {category} item"

            response = await self.agent.create_product(
                name, description, price, sku, category, stock
            )
            self.print_response("Create Product", response)

        elif entity_type == "customer":
            if len(args) < 4:
                print("Usage: create customer <email> <first_name> <last_name>")
                return

            email = args[1]
            first_name = args[2]
            last_name = args[3]

            response = await self.agent.create_customer(email, first_name, last_name)
            self.print_response("Create Customer", response)

        else:
            print(f"Unknown entity type: {entity_type}")

    async def handle_get(self, args: List[str]):
        """Handle get commands."""
        if len(args) < 2:
            print("Usage: get <type> <identifier>")
            return

        entity_type = args[0].lower()
        identifier = args[1]

        if entity_type == "product":
            # Determine if it's an ID or SKU
            search_by = "sku" if not identifier.startswith("prod_") else "id"
            response = await self.agent.get_product(identifier, search_by)
            self.print_response("Get Product", response)

        elif entity_type == "customer":
            # Determine if it's an ID or email
            search_by = "email" if "@" in identifier else "id"
            response = await self.agent.get_customer(identifier, search_by)
            self.print_response("Get Customer", response)

        else:
            print(f"Unknown entity type: {entity_type}")

    async def handle_search(self, args: List[str]):
        """Handle search commands."""
        if not args or args[0].lower() != "products":
            print("Usage: search products <query>")
            return

        if len(args) < 2:
            print("Usage: search products <query>")
            return

        query = " ".join(args[1:])
        response = await self.agent.search_products(query)
        self.print_response("Search Products", response)

    async def handle_order(self, args: List[str]):
        """Handle order commands."""
        if not args:
            print("Usage: order <action> <args...>")
            return

        action = args[0].lower()

        if action == "create":
            if len(args) < 4:
                print("Usage: order create <customer_id> <product_id> <quantity>")
                return

            customer_id = args[1]
            product_id = args[2]
            try:
                quantity = int(args[3])
            except ValueError:
                print("Quantity must be an integer")
                return

            items = [{"product_id": product_id, "quantity": quantity}]
            response = await self.agent.create_order(customer_id, items)
            self.print_response("Create Order", response)

        elif action == "get":
            if len(args) < 2:
                print("Usage: order get <order_id>")
                return

            order_id = args[1]
            response = await self.agent.get_order(order_id)
            self.print_response("Get Order", response)

        elif action == "status":
            if len(args) < 3:
                print("Usage: order status <order_id> <status>")
                return

            order_id = args[1]
            status = args[2]
            response = await self.agent.update_order_status(order_id, status)
            self.print_response("Update Order Status", response)

        else:
            print(f"Unknown order action: {action}")

    async def handle_stock(self, args: List[str]):
        """Handle stock commands."""
        if not args:
            print("Usage: stock <action> <args...>")
            return

        action = args[0].lower()

        if action == "update":
            if len(args) < 3:
                print("Usage: stock update <product_id> <quantity>")
                return

            product_id = args[1]
            try:
                quantity = int(args[2])
            except ValueError:
                print("Quantity must be an integer")
                return

            response = await self.agent.update_stock(product_id, quantity)
            self.print_response("Update Stock", response)

        elif action == "low":
            threshold = 10
            if len(args) > 1:
                try:
                    threshold = int(args[1])
                except ValueError:
                    print("Threshold must be an integer")
                    return

            response = await self.agent.get_low_stock_products(threshold)
            self.print_response("Low Stock Products", response)

        elif action == "restock":
            restock_qty = 50
            if len(args) > 1:
                try:
                    restock_qty = int(args[1])
                except ValueError:
                    print("Restock quantity must be an integer")
                    return

            response = await self.agent.restock_low_inventory(restock_qty)
            self.print_response("Restock Inventory", response)

        else:
            print(f"Unknown stock action: {action}")

    async def handle_list(self, args: List[str]):
        """Handle list commands."""
        if not args:
            print("Usage: list <type>")
            return

        entity_type = args[0].lower()

        if entity_type == "products":
            response = await self.agent.get_all_products()
            self.print_response("All Products", response)
        elif entity_type == "customers":
            response = await self.agent.get_all_customers()
            self.print_response("All Customers", response)
        elif entity_type == "orders":
            response = await self.agent.get_all_orders()
            self.print_response("All Orders", response)
        else:
            print(f"Unknown entity type: {entity_type}")
            print("Available types: products, customers, orders")

    async def run_demo(self):
        """Run a quick demonstration."""
        print("Running demonstration...")

        # Create a sample product
        print("\n1. Creating sample product...")
        response = await self.agent.create_product(
            "Demo Widget",
            "A sample product for demonstration",
            99.99,
            "DEMO-001",
            "Demo",
            25,
        )
        print(
            f"   Result: {'✅' if response.success else '❌'} {response.message or response.error}"
        )

        # Search for it
        print("\n2. Searching for demo products...")
        response = await self.agent.search_products("demo")
        if response.success:
            products = json.loads(response.data[0]["text"])
            print(f"   Found {len(products)} products")

        # Check low stock
        print("\n3. Checking inventory...")
        response = await self.agent.get_low_stock_products(30)
        if response.success:
            products = json.loads(response.data[0]["text"])
            print(f"   Found {len(products)} low stock items")

        print("\nDemo completed!")

    def print_response(self, operation: str, response: AgentResponse):
        """Print a formatted response."""
        if response.success:
            print(f"✅ {operation}: {response.message}")
            if response.data:
                # Try to format JSON data nicely
                try:
                    if isinstance(response.data, list) and response.data:
                        data = json.loads(response.data[0]["text"])
                        if isinstance(data, list):
                            print(f"   Found {len(data)} items:")
                            for i, item in enumerate(data[:3]):  # Show first 3 items
                                if isinstance(item, dict):
                                    name = item.get(
                                        "name",
                                        item.get("email", item.get("id", "Unknown")),
                                    )
                                    print(f"   {i + 1}. {name}")
                            if len(data) > 3:
                                print(f"   ... and {len(data) - 3} more")
                        else:
                            # Single item
                            if isinstance(data, dict):
                                name = data.get(
                                    "name", data.get("email", data.get("id", "Item"))
                                )
                                print(f"   {name}")
                except Exception:
                    # Fallback to raw output
                    print(f"   Data: {str(response.data)[:100]}...")
        else:
            print(f"❌ {operation}: {response.error}")


async def main():
    """Main function to run the CLI."""
    cli = EcommerceCLI()
    await cli.start()


if __name__ == "__main__":
    asyncio.run(main())
