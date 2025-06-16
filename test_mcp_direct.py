#!/usr/bin/env python3
"""Direct test of MCP server communication."""

import asyncio
import logging
import sys
import os

# Add project directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "egile"))

from egile.agent import EcommerceAgent

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("mcp_test")


async def test_mcp_communication():
    """Test MCP server communication step by step."""
    print("=== Direct MCP Communication Test ===")

    agent = EcommerceAgent()

    print("1. Starting server...")
    start_success = await agent.start_server()
    print(f"   Server start result: {start_success}")

    if not start_success:
        print("   Failed to start server!")
        return

    print(f"   Connected: {agent.is_connected}")
    print(f"   Initialized: {agent.is_initialized}")

    print("\n2. Testing direct send_request...")
    try:
        response = await agent.send_request("tools/list", {})
        print(f"   Tools list response: {response}")
    except Exception as e:
        print(f"   Error getting tools list: {e}")

    print("\n3. Testing call_tool directly...")
    try:
        response = await agent.call_tool("get_all_products", {})
        print(f"   call_tool success: {response.success}")
        print(f"   call_tool data type: {type(response.data)}")
        print(f"   call_tool data: {response.data}")
        print(f"   call_tool error: {response.error}")
    except Exception as e:
        print(f"   Error in call_tool: {e}")

    print("\n4. Testing search_products...")
    try:
        response = await agent.search_products("microphone")
        print(f"   search_products success: {response.success}")
        print(f"   search_products data type: {type(response.data)}")
        print(f"   search_products data: {response.data}")
        print(f"   search_products error: {response.error}")
    except Exception as e:
        print(f"   Error in search_products: {e}")

    print("\n5. Stopping server...")
    await agent.stop_server()


if __name__ == "__main__":
    asyncio.run(test_mcp_communication())
