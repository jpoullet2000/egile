#!/usr/bin/env python3
"""
Simple test script to verify the Smart Agent works after cleanup.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def test_smart_agent():
    """Test the Smart Agent basic functionality."""
    print("🧪 Testing Smart Agent...")

    try:
        # Test import
        from egile.smart_agent import SmartAgent

        print("✅ SmartAgent imported successfully")

        # Create agent
        agent = SmartAgent()
        print("✅ SmartAgent instance created")

        # Start agent
        await agent.start()
        print("✅ Agent started")

        # Test simple requests
        test_requests = [
            "help",
            "show all products",
            "setup demo store with 5 products",
        ]

        for request in test_requests:
            print(f"\n📝 Testing: '{request}'")
            response = await agent.process_request(request)

            success = response.get("success", False)
            response_type = response.get("type", "unknown")
            message_preview = response.get("message", "")[:100]

            print(f"   Success: {success}")
            print(f"   Type: {response_type}")
            print(f"   Message: {message_preview}...")

            # If it's a plan, test confirmation
            if response_type == "plan_created":
                print("   🔄 Testing plan confirmation...")
                confirm_response = await agent.process_request("yes")
                confirm_success = confirm_response.get("success", False)
                print(f"   Confirmation success: {confirm_success}")

        # Stop agent
        await agent.stop()
        print("✅ Agent stopped")

        print("\n🎉 Smart Agent test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_enhanced_tools():
    """Test the Enhanced MCP Tools."""
    print("\n🧪 Testing Enhanced MCP Tools...")

    try:
        from egile.enhanced_mcp_tools import EnhancedMCPTools

        print("✅ EnhancedMCPTools imported successfully")

        tools = EnhancedMCPTools()
        print("✅ EnhancedMCPTools instance created")

        # Test store analysis
        result = await tools.analyze_store_performance()
        success = result.get("success", False)
        print(f"✅ Store analysis: {success}")

        print("🎉 Enhanced tools test completed!")
        return True

    except Exception as e:
        print(f"❌ Enhanced tools test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("🚀 Starting Smart Agent System Tests")
    print("=" * 50)

    # Test Smart Agent
    smart_agent_ok = await test_smart_agent()

    # Test Enhanced Tools
    enhanced_tools_ok = await test_enhanced_tools()

    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   Smart Agent: {'✅ PASS' if smart_agent_ok else '❌ FAIL'}")
    print(f"   Enhanced Tools: {'✅ PASS' if enhanced_tools_ok else '❌ FAIL'}")

    if smart_agent_ok and enhanced_tools_ok:
        print("\n🎉 All systems working correctly!")
        print("\n💡 You can now use:")
        print("   • python3 demo_smart_agent.py (interactive)")
        print("   • python3 demo_smart_agent.py --auto (automated demo)")
        print("   • python3 run_enhanced_demo.py (enhanced tools demo)")
    else:
        print("\n❌ Some tests failed. Check the errors above.")


if __name__ == "__main__":
    asyncio.run(main())
