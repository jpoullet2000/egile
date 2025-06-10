#!/usr/bin/env python3
"""
Simplified E-commerce Agent for debugging

This version focuses on getting basic MCP communication working.
"""

import asyncio
import json
import logging
import sys
from typing import Dict, Any

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("simple-agent")


class SimpleEcommerceAgent:
    """Simplified agent for testing MCP communication."""

    def __init__(self):
        self.server_process = None
        self.is_connected = False
        self.is_initialized = False
        self.request_id = 0

    async def start_server(self):
        """Start the MCP server."""
        try:
            self.server_process = await asyncio.create_subprocess_exec(
                sys.executable,
                "/home/jbp/projects/egile/egile/server_sqlite.py",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            self.is_connected = True
            logger.info("Server started")

            # Initialize the server
            await self.initialize_server()
            return True

        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            return False

    async def initialize_server(self):
        """Initialize the MCP server."""
        try:
            # Send initialize request
            init_request = {
                "jsonrpc": "2.0",
                "id": self.get_next_id(),
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}, "resources": {}},
                    "clientInfo": {
                        "name": "simple-ecommerce-agent",
                        "version": "0.1.0",
                    },
                },
            }

            logger.debug(f"Sending initialize: {init_request}")
            await self.send_message(init_request)

            # Wait for response
            response = await self.receive_message()
            logger.info(f"Initialize response: {response}")

            # Send initialized notification
            initialized_notification = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
            }

            logger.debug("Sending initialized notification")
            await self.send_message(initialized_notification)

            self.is_initialized = True
            logger.info("Server initialized successfully")

        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            raise

    def get_next_id(self):
        """Get next request ID."""
        self.request_id += 1
        return self.request_id

    async def send_message(self, message: Dict):
        """Send a message to the server."""
        if not self.server_process:
            raise RuntimeError("Server not started")

        message_data = json.dumps(message) + "\n"
        self.server_process.stdin.write(message_data.encode())
        await self.server_process.stdin.drain()

    async def receive_message(self, timeout: float = 5.0):
        """Receive a message from the server."""
        if not self.server_process:
            raise RuntimeError("Server not started")

        try:
            response_data = await asyncio.wait_for(
                self.server_process.stdout.readline(), timeout=timeout
            )

            if response_data:
                return json.loads(response_data.decode().strip())
            else:
                raise RuntimeError("No response from server")

        except asyncio.TimeoutError:
            raise RuntimeError(f"Timeout waiting for response after {timeout}s")

    async def call_tool(self, tool_name: str, arguments: Dict) -> Dict:
        """Call a tool on the server."""
        if not self.is_initialized:
            raise RuntimeError("Server not initialized")

        request = {
            "jsonrpc": "2.0",
            "id": self.get_next_id(),
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments},
        }

        logger.debug(f"Calling tool {tool_name} with args: {arguments}")
        await self.send_message(request)

        response = await self.receive_message()
        logger.debug(f"Tool response: {response}")

        return response

    async def create_product(
        self,
        name: str,
        description: str,
        price: float,
        sku: str,
        category: str,
        stock_quantity: int,
    ) -> Dict:
        """Create a product."""
        return await self.call_tool(
            "create_product",
            {
                "name": name,
                "description": description,
                "price": price,
                "sku": sku,
                "category": category,
                "stock_quantity": stock_quantity,
            },
        )

    async def list_tools(self) -> Dict:
        """List available tools."""
        request = {"jsonrpc": "2.0", "id": self.get_next_id(), "method": "tools/list"}

        await self.send_message(request)
        return await self.receive_message()

    async def stop_server(self):
        """Stop the server."""
        if self.server_process:
            self.server_process.terminate()
            await self.server_process.wait()
            self.is_connected = False
            self.is_initialized = False
            logger.info("Server stopped")


async def test_simple_agent():
    """Test the simple agent."""
    agent = SimpleEcommerceAgent()

    try:
        print("Starting simple agent test...")

        # Start server
        if not await agent.start_server():
            print("❌ Failed to start server")
            return

        print("✅ Server started and initialized")

        # List available tools
        print("📋 Listing available tools...")
        tools_response = await agent.list_tools()
        print(f"Tools response: {tools_response}")

        # Create a test product
        print("🛍️ Creating test product...")
        product_response = await agent.create_product(
            name="Test Widget",
            description="A simple test product",
            price=29.99,
            sku="TEST-WIDGET-001",
            category="Test",
            stock_quantity=100,
        )

        print(f"Product creation response: {product_response}")

        if "error" in product_response:
            print(f"❌ Product creation failed: {product_response['error']}")
        else:
            print("✅ Product created successfully!")

        print("🎉 Test completed!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.exception("Test error")
    finally:
        await agent.stop_server()


if __name__ == "__main__":
    asyncio.run(test_simple_agent())
