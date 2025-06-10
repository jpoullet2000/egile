#!/usr/bin/env python3
"""
Test basic MCP server functionality
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the project root to path
sys.path.insert(0, str(Path(__file__).parent))

from egile.agent import EcommerceAgent


async def test_basic_functionality():
    """Test basic MCP functionality."""
    agent = EcommerceAgent()

    try:
        print("🔧 Starting MCP server...")
        if not await agent.start_server():
            print("❌ Failed to start server")
            return False

        print("✅ Server started successfully")

        # Test 1: List tools
        print("\n📋 Testing tools/list...")
        try:
            response = await agent.send_request("tools/list")
            if "error" in response:
                print(f"❌ Tools list failed: {response['error']}")
                return False
            else:
                print(f"Debug: Full response = {response}")
                tools = response.get("result", [])
                print(
                    f"Debug: tools type = {type(tools)}, length = {len(tools) if hasattr(tools, '__len__') else 'no len'}"
                )
                print(f"✅ Found {len(tools)} tools")
                # Handle both dict and list response formats
                if isinstance(tools, dict):
                    tools_list = tools.get("tools", [])
                else:
                    tools_list = tools

                # Show first 3 tools
                for i, tool in enumerate(tools_list):
                    if i >= 3:
                        break
                    tool_name = (
                        tool.get("name", "Unknown tool")
                        if isinstance(tool, dict)
                        else str(tool)
                    )
                    print(f"   - {tool_name}")

                if len(tools_list) > 3:
                    print(f"   ... and {len(tools_list) - 3} more tools")
        except Exception as e:
            print(f"❌ Tools list exception: {e}")
            import traceback

            traceback.print_exc()
            return False

        # Test 2: List resources
        print("\n📋 Testing resources/list...")
        try:
            response = await agent.send_request("resources/list")
            if "error" in response:
                print(f"❌ Resources list failed: {response['error']}")
                return False
            else:
                resources = response.get("result", [])
                print(f"✅ Found {len(resources)} resources")
                # Handle both dict and list response formats
                if isinstance(resources, dict):
                    resources_list = resources.get("resources", [])
                else:
                    resources_list = resources

                for resource in resources_list:
                    if isinstance(resource, dict):
                        print(f"   - {resource.get('uri', 'Unknown resource')}")
                    else:
                        print(f"   - {str(resource)}")
        except Exception as e:
            print(f"❌ Resources list exception: {e}")
            import traceback

            traceback.print_exc()
            return False

        # Test 3: Create a product
        print("\n📦 Testing product creation...")
        try:
            response = await agent.create_product(
                name="Test Product",
                description="A test product",
                price=19.99,
                sku="TEST-001",
                category="Test",
                stock_quantity=5,
            )
            if response.success:
                print("✅ Product created successfully")
            else:
                print(f"❌ Product creation failed: {response.error}")
                return False
        except Exception as e:
            print(f"❌ Product creation exception: {e}")
            return False

        # Test 4: Try to access products resource (expected to fail)
        print("\n📋 Testing products resource access...")
        try:
            response = await agent.send_request(
                "resources/read", {"uri": "ecommerce://products"}
            )
            if "error" in response:
                print(
                    f"❌ Resource access failed (expected): {response['error']['message']}"
                )
            else:
                result = response.get("result", [])
                print(f"✅ Resource access successful, got {type(result)}")
        except Exception as e:
            print(f"❌ Resource access exception: {e}")

        # Test 5: Test our tool-based workaround
        print("\n🔧 Testing tool-based data access workaround...")
        try:
            response = await agent.send_request(
                "tools/call", {"name": "get_all_products", "arguments": {}}
            )
            if "error" in response:
                print(f"❌ Tool-based access failed: {response['error']['message']}")
                return False
            else:
                result = response.get("result", {})
                content = result.get("content", [])
                print(f"✅ Tool-based access works! Got {len(content)} content items")
                if content and content[0].get("text"):
                    import json

                    products = json.loads(content[0]["text"])
                    print(f"   Found {len(products)} products in database")
                return True
        except Exception as e:
            print(f"❌ Tool-based access exception: {e}")
            return False

        print("\n🎉 All basic tests passed!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        await agent.stop_server()


if __name__ == "__main__":
    success = asyncio.run(test_basic_functionality())
    if success:
        print("\n✅ Server is working correctly!")
        print("You can now use:")
        print("   python run_cli.py")
        print("   python run_agent_demo.py")
    else:
        print("\n❌ Server has issues. Check the errors above.")
    sys.exit(0 if success else 1)
