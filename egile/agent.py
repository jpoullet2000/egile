#!/usr/bin/env python3
"""
E-commerce Agent - A client that communicates with the E-commerce MCP Server

This agent provides a high-level interface for interacting with the e-commerce
MCP server, making it easy to perform common e-commerce operations.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List
from dataclasses import dataclass
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ecommerce-agent")


@dataclass
class AgentResponse:
    """Response from agent operations."""

    success: bool
    data: Any = None
    message: str = ""
    error: str = ""


class EcommerceAgent:
    """
    Agent for interacting with the E-commerce MCP Server.

    This agent provides a convenient interface for performing e-commerce operations
    like managing products, customers, orders, and inventory.
    """

    def __init__(self, server_command: List[str] = None):
        """
        Initialize the e-commerce agent.

        Args:
            server_command: Command to start the MCP server. Defaults to running the local server.
        """
        self.server_command = server_command or [
            sys.executable,
            "/home/jbp/projects/egile/egile/server_sqlite.py",
        ]
        self.server_process = None
        self.is_connected = False
        self.is_initialized = False
        self.request_id = 0

    async def start_server(self):
        """Start the MCP server process."""
        try:
            self.server_process = await asyncio.create_subprocess_exec(
                *self.server_command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            self.is_connected = True
            logger.info("MCP server started successfully")

            # Wait a bit for server to start
            await asyncio.sleep(2)

            # Check if process is still running
            if self.server_process.returncode is not None:
                # Process has already exited
                stderr = await self.server_process.stderr.read()
                logger.error(
                    f"Server process exited with code {self.server_process.returncode}"
                )
                logger.error(f"Server stderr: {stderr.decode()}")
                return False

            # Initialize the server
            await self._initialize_server()
            return True
        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}")
            # Try to get stderr if process exists
            if hasattr(self, "server_process") and self.server_process:
                try:
                    stderr = await self.server_process.stderr.read()
                    if stderr:
                        logger.error(f"Server stderr: {stderr.decode()}")
                except Exception:
                    pass
            return False

    async def stop_server(self):
        """Stop the MCP server process."""
        if self.server_process:
            try:
                # Check if process is still running
                if self.server_process.returncode is None:
                    self.server_process.terminate()
                    await self.server_process.wait()
                self.is_connected = False
                self.is_initialized = False
                logger.info("MCP server stopped")
            except ProcessLookupError:
                # Process already terminated
                logger.info("MCP server was already stopped")
                self.is_connected = False
                self.is_initialized = False
            except Exception as e:
                logger.error(f"Error stopping server: {e}")
                self.is_connected = False
                self.is_initialized = False

    def get_next_id(self):
        """Get next request ID."""
        self.request_id += 1
        return self.request_id

    async def _initialize_server(self):
        """Initialize the MCP server with the required handshake."""
        try:
            # Wait a moment for server to start
            await asyncio.sleep(1)

            # Send initialize request
            init_request = {
                "jsonrpc": "2.0",
                "id": self.get_next_id(),
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}, "resources": {}},
                    "clientInfo": {"name": "ecommerce-agent", "version": "0.1.0"},
                },
            }

            request_data = json.dumps(init_request) + "\n"
            self.server_process.stdin.write(request_data.encode())
            await self.server_process.stdin.drain()

            # Read initialize response
            response_data = await asyncio.wait_for(
                self.server_process.stdout.readline(), timeout=5.0
            )

            if response_data:
                init_response = json.loads(response_data.decode().strip())
                logger.info(f"Server initialized: {init_response}")
            else:
                raise RuntimeError("No response from server during initialization")

            # Send initialized notification
            initialized_notification = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
            }

            notification_data = json.dumps(initialized_notification) + "\n"
            self.server_process.stdin.write(notification_data.encode())
            await self.server_process.stdin.drain()

            self.is_initialized = True
            logger.info("MCP server initialization completed")

        except Exception as e:
            logger.error(f"Server initialization failed: {e}")
            raise

    async def send_request(self, method: str, params: Dict = None) -> Dict:
        """
        Send a request to the MCP server.

        Args:
            method: The MCP method to call
            params: Parameters for the method

        Returns:
            Response from the server
        """
        if not self.is_connected:
            raise RuntimeError("Agent not connected to server")

        if not self.is_initialized:
            raise RuntimeError("Agent not initialized")

        request = {
            "jsonrpc": "2.0",
            "id": self.get_next_id(),
            "method": method,
            "params": params or {},
        }

        try:
            # Send request
            request_data = json.dumps(request) + "\n"
            self.server_process.stdin.write(request_data.encode())
            await self.server_process.stdin.drain()

            # Read response
            response_data = await asyncio.wait_for(
                self.server_process.stdout.readline(), timeout=10.0
            )

            if response_data:
                response = json.loads(response_data.decode().strip())
                return response
            else:
                logger.error("No response from server")
                return {"error": {"message": "No response from server"}}

        except asyncio.TimeoutError:
            logger.error("Timeout waiting for server response")
            return {"error": {"message": "Timeout waiting for server response"}}
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return {"error": {"message": str(e)}}

    async def call_tool(self, tool_name: str, arguments: Dict) -> AgentResponse:
        """
        Call a tool on the MCP server.

        Args:
            tool_name: Name of the tool to call
            arguments: Arguments for the tool

        Returns:
            AgentResponse with the result
        """
        try:
            response = await self.send_request(
                "tools/call", {"name": tool_name, "arguments": arguments}
            )

            if "error" in response:
                return AgentResponse(success=False, error=response["error"]["message"])

            # Extract the content from the MCP response format
            result = response.get("result", {})
            content = result.get("content", [])

            # Parse JSON from text content if it's in MCP format
            parsed_data = None
            if content and isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text_content = item.get("text", "")
                        try:
                            import json

                            parsed_data = json.loads(text_content)
                            break
                        except json.JSONDecodeError:
                            # If it's not JSON, keep the raw text
                            parsed_data = text_content
                            break

            # If we couldn't parse JSON, use the original content
            if parsed_data is None:
                parsed_data = content

            return AgentResponse(
                success=True,
                data=parsed_data,
                message=f"Tool {tool_name} executed successfully",
            )
        except Exception as e:
            return AgentResponse(success=False, error=str(e))

    async def get_resource(self, resource_uri: str) -> AgentResponse:
        """
        Get a resource from the MCP server.

        Args:
            resource_uri: URI of the resource to fetch

        Returns:
            AgentResponse with the resource data
        """
        try:
            response = await self.send_request("resources/read", {"uri": resource_uri})

            if "error" in response:
                return AgentResponse(success=False, error=response["error"]["message"])

            # Handle MCP resource response format
            result = response.get("result")
            if result is None:
                return AgentResponse(success=False, error="No result in response")

            # MCP should return a list of TextContent objects directly
            if isinstance(result, list):
                # Expected format: list of TextContent objects
                content = result
            elif isinstance(result, str):
                # Fallback: direct string response
                content = [{"text": result}]
            else:
                # Unexpected format, try to extract text
                content = [{"text": json.dumps(result)}]

            return AgentResponse(
                success=True,
                data=content,
                message=f"Resource {resource_uri} retrieved successfully",
            )
        except Exception as e:
            return AgentResponse(success=False, error=str(e))

    # Product Management Methods

    async def create_product(
        self,
        name: str,
        description: str,
        price: float,
        sku: str,
        category: str,
        stock_quantity: int,
        currency: str = "USD",
    ) -> AgentResponse:
        """Create a new product."""
        return await self.call_tool(
            "create_product",
            {
                "name": name,
                "description": description,
                "price": price,
                "currency": currency,
                "sku": sku,
                "category": category,
                "stock_quantity": stock_quantity,
            },
        )

    async def get_product(
        self, identifier: str, search_by: str = "id"
    ) -> AgentResponse:
        """Get product by ID or SKU."""
        return await self.call_tool(
            "get_product", {"identifier": identifier, "search_by": search_by}
        )

    async def update_product(self, product_id: str, updates: Dict) -> AgentResponse:
        """Update product information."""
        return await self.call_tool(
            "update_product", {"product_id": product_id, "updates": updates}
        )

    async def search_products(
        self,
        query: str,
        category: str = None,
        min_price: float = None,
        max_price: float = None,
        in_stock_only: bool = False,
    ) -> AgentResponse:
        """Search products with filters."""
        params = {"query": query}
        if category:
            params["category"] = category
        if min_price is not None:
            params["min_price"] = min_price
        if max_price is not None:
            params["max_price"] = max_price
        if in_stock_only:
            params["in_stock_only"] = in_stock_only

        return await self.call_tool("search_products", params)

    # Customer Management Methods

    async def create_customer(
        self,
        email: str,
        first_name: str,
        last_name: str,
        phone: str = None,
        address: Dict = None,
    ) -> AgentResponse:
        """Create a new customer."""
        params = {"email": email, "first_name": first_name, "last_name": last_name}
        if phone:
            params["phone"] = phone
        if address:
            params["address"] = address

        return await self.call_tool("create_customer", params)

    async def get_customer(
        self, identifier: str, search_by: str = "id"
    ) -> AgentResponse:
        """Get customer by ID or email."""
        return await self.call_tool(
            "get_customer", {"identifier": identifier, "search_by": search_by}
        )

    # Order Management Methods

    async def create_order(
        self, customer_id: str, items: List[Dict], currency: str = "USD"
    ) -> AgentResponse:
        """Create a new order."""
        return await self.call_tool(
            "create_order",
            {"customer_id": customer_id, "items": items, "currency": currency},
        )

    async def get_order(self, order_id: str) -> AgentResponse:
        """Get order details."""
        return await self.call_tool("get_order", {"order_id": order_id})

    async def update_order_status(self, order_id: str, status: str) -> AgentResponse:
        """Update order status."""
        return await self.call_tool(
            "update_order_status", {"order_id": order_id, "status": status}
        )

    # Inventory Management Methods

    async def update_stock(
        self, product_id: str, quantity: int, operation: str = "set"
    ) -> AgentResponse:
        """Update product stock."""
        return await self.call_tool(
            "update_stock",
            {"product_id": product_id, "quantity": quantity, "operation": operation},
        )

    async def get_low_stock_products(self, threshold: int = 10) -> AgentResponse:
        """Get products with low stock."""
        return await self.call_tool("get_low_stock_products", {"threshold": threshold})

    # Resource Access Methods (fallback to tools if resources don't work)

    async def get_all_products(self) -> AgentResponse:
        """Get all products from the database."""
        # Try resource first, fallback to tool
        resource_response = await self.get_resource("ecommerce://products")
        if resource_response.success:
            return resource_response

        # Fallback to tool
        return await self.call_tool("get_all_products", {})

    async def get_all_customers(self) -> AgentResponse:
        """Get all customers from the database."""
        # Try resource first, fallback to tool
        resource_response = await self.get_resource("ecommerce://customers")
        if resource_response.success:
            return resource_response

        # Fallback to tool
        return await self.call_tool("get_all_customers", {})

    async def get_all_orders(self) -> AgentResponse:
        """Get all orders from the database."""
        # Try resource first, fallback to tool
        resource_response = await self.get_resource("ecommerce://orders")
        if resource_response.success:
            return resource_response

        # Fallback to tool
        return await self.call_tool("get_all_orders", {})

    # High-level Business Operations

    async def complete_purchase_flow(
        self, customer_email: str, product_skus: List[str], quantities: List[int]
    ) -> AgentResponse:
        """
        Complete a full purchase flow: find customer, check products, create order.

        Args:
            customer_email: Customer's email address
            product_skus: List of product SKUs to purchase
            quantities: List of quantities for each product

        Returns:
            AgentResponse with order details or error
        """
        try:
            # Get customer
            customer_response = await self.get_customer(customer_email, "email")
            if not customer_response.success:
                return AgentResponse(
                    success=False, error=f"Customer not found: {customer_email}"
                )

            customer_data = json.loads(customer_response.data[0]["text"])
            customer_id = customer_data["id"]

            # Build order items
            order_items = []
            for sku, qty in zip(product_skus, quantities):
                product_response = await self.get_product(sku, "sku")
                if not product_response.success:
                    return AgentResponse(
                        success=False, error=f"Product not found: {sku}"
                    )

                product_data = json.loads(product_response.data[0]["text"])
                order_items.append({"product_id": product_data["id"], "quantity": qty})

            # Create order
            order_response = await self.create_order(customer_id, order_items)

            if order_response.success:
                return AgentResponse(
                    success=True,
                    data=order_response.data,
                    message="Purchase completed successfully",
                )
            else:
                return order_response

        except Exception as e:
            return AgentResponse(success=False, error=f"Purchase flow failed: {str(e)}")

    async def restock_low_inventory(self, restock_quantity: int = 50) -> AgentResponse:
        """
        Automatically restock products that are low on inventory.

        Args:
            restock_quantity: Amount to add to low stock products

        Returns:
            AgentResponse with restocking details
        """
        try:
            # Get low stock products
            low_stock_response = await self.get_low_stock_products()
            if not low_stock_response.success:
                return low_stock_response

            low_stock_products = json.loads(low_stock_response.data[0]["text"])

            if not low_stock_products:
                return AgentResponse(
                    success=True, message="No products need restocking"
                )

            restocked_products = []
            for product in low_stock_products:
                product_id = product["id"]
                current_stock = product["stock_quantity"]

                # Add restock quantity
                restock_response = await self.update_stock(
                    product_id, restock_quantity, "add"
                )

                if restock_response.success:
                    restocked_products.append(
                        {
                            "id": product_id,
                            "name": product["name"],
                            "old_stock": current_stock,
                            "new_stock": current_stock + restock_quantity,
                        }
                    )

            return AgentResponse(
                success=True,
                data=restocked_products,
                message=f"Restocked {len(restocked_products)} products",
            )

        except Exception as e:
            return AgentResponse(success=False, error=f"Restocking failed: {str(e)}")


# Example usage and testing
async def demonstrate_agent():
    """Demonstrate the agent's capabilities."""

    agent = EcommerceAgent()

    try:
        print("Starting E-commerce Agent Demo")
        print("=" * 50)

        # Start the server
        print("1. Starting MCP server...")
        if not await agent.start_server():
            print("Failed to start server")
            return

        # Wait a moment for server to initialize
        await asyncio.sleep(3)

        print("2. Creating sample products...")

        # Create some products
        products = [
            (
                "Laptop Pro",
                "High-performance laptop",
                1299.99,
                "LAPTOP-001",
                "Electronics",
                15,
            ),
            (
                "Wireless Mouse",
                "Ergonomic wireless mouse",
                29.99,
                "MOUSE-001",
                "Accessories",
                8,
            ),
            ("USB Drive", "32GB USB 3.0 drive", 19.99, "USB-001", "Accessories", 3),
        ]

        for name, desc, price, sku, category, stock in products:
            response = await agent.create_product(
                name, desc, price, sku, category, stock
            )
            if response.success:
                print(f"   ✓ Created: {name}")
            else:
                print(f"   ✗ Failed to create {name}: {response.error}")

        print("\n3. Creating a customer...")
        customer_response = await agent.create_customer(
            email="demo@example.com",
            first_name="Demo",
            last_name="User",
            phone="+1-555-0100",
            address={
                "street": "123 Demo Street",
                "city": "Demo City",
                "state": "DC",
                "zip": "12345",
                "country": "US",
            },
        )

        if customer_response.success:
            print("   ✓ Customer created")
        else:
            print(f"   ✗ Failed to create customer: {customer_response.error}")

        print("\n4. Searching for products...")
        search_response = await agent.search_products("wireless", in_stock_only=True)
        if search_response.success:
            products_found = json.loads(search_response.data[0]["text"])
            print(f"   ✓ Found {len(products_found)} wireless products in stock")

        print("\n5. Checking low stock items...")
        low_stock_response = await agent.get_low_stock_products(threshold=10)
        if low_stock_response.success:
            low_stock_items = json.loads(low_stock_response.data[0]["text"])
            print(f"   ✓ Found {len(low_stock_items)} low stock items")
            for item in low_stock_items:
                print(f"     - {item['name']}: {item['stock_quantity']} units")

        print("\n6. Creating an order...")
        order_response = await agent.complete_purchase_flow(
            customer_email="demo@example.com",
            product_skus=["LAPTOP-001", "MOUSE-001"],
            quantities=[1, 2],
        )

        if order_response.success:
            print("   ✓ Order created successfully")
        else:
            print(f"   ✗ Order failed: {order_response.error}")

        print("\n7. Restocking low inventory...")
        restock_response = await agent.restock_low_inventory(restock_quantity=25)
        if restock_response.success:
            if restock_response.data:
                print(f"   ✓ Restocked {len(restock_response.data)} products")
                for item in restock_response.data:
                    print(
                        f"     - {item['name']}: {item['old_stock']} → {item['new_stock']}"
                    )
            else:
                print("   ✓ No restocking needed")

        print("\n" + "=" * 50)
        print("Demo completed successfully!")

    except Exception as e:
        print(f"Demo failed: {e}")
        logger.exception("Demo error")

    finally:
        # Stop the server
        await agent.stop_server()


if __name__ == "__main__":
    asyncio.run(demonstrate_agent())
