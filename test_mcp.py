#!/usr/bin/env python3
"""
Simple test script to debug MCP server communication
"""

import asyncio
import json
import sys
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("test")


async def test_mcp_server():
    """Test basic communication with MCP server."""

    print("Starting MCP server test...")

    # Start the server
    server_process = await asyncio.create_subprocess_exec(
        sys.executable,
        "/home/jbp/projects/egile/ecommerce-mcp-server.py",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    try:
        # Wait a moment for server to start
        await asyncio.sleep(1)

        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "0.1.0"},
            },
        }

        print("Sending initialize request...")
        request_data = json.dumps(init_request) + "\n"
        server_process.stdin.write(request_data.encode())
        await server_process.stdin.drain()

        # Read response
        response_data = await asyncio.wait_for(
            server_process.stdout.readline(), timeout=5.0
        )

        if response_data:
            response = json.loads(response_data.decode().strip())
            print(f"Initialize response: {response}")
        else:
            print("No response received")

        # Send initialized notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
        }

        print("Sending initialized notification...")
        notification_data = json.dumps(initialized_notification) + "\n"
        server_process.stdin.write(notification_data.encode())
        await server_process.stdin.drain()

        # Try to create a product
        create_product_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "create_product",
                "arguments": {
                    "name": "Test Product",
                    "description": "A test product",
                    "price": 99.99,
                    "sku": "TEST-001",
                    "category": "Test",
                    "stock_quantity": 10,
                },
            },
        }

        print("Sending create product request...")
        request_data = json.dumps(create_product_request) + "\n"
        server_process.stdin.write(request_data.encode())
        await server_process.stdin.drain()

        # Read response
        response_data = await asyncio.wait_for(
            server_process.stdout.readline(), timeout=5.0
        )

        if response_data:
            response = json.loads(response_data.decode().strip())
            print(f"Create product response: {response}")
        else:
            print("No response received for create product")

        # Check stderr for any errors
        stderr_data = await server_process.stderr.read()
        if stderr_data:
            print(f"Server stderr: {stderr_data.decode()}")

    except asyncio.TimeoutError:
        print("Timeout waiting for server response")
    except Exception as e:
        print(f"Error: {e}")
        logger.exception("Test failed")
    finally:
        # Stop the server
        server_process.terminate()
        await server_process.wait()
        print("Server stopped")


if __name__ == "__main__":
    asyncio.run(test_mcp_server())
