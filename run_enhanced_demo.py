#!/usr/bin/env python3
"""
Demo script for the enhanced e-commerce agent capabilities.

This script demonstrates:
1. Enhanced MCP server tools
2. Intelligent planning and analysis
3. Complex multi-step operations
4. Business intelligence features
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from egile.enhanced_mcp_tools import EnhancedMCPTools


async def demo_enhanced_agent():
    """Demonstrate enhanced agent capabilities."""
    print("🚀 Enhanced E-commerce Agent Demo")
    print("=" * 60)

    # Initialize enhanced tools
    tools = EnhancedMCPTools()

    try:
        # 1. Setup a comprehensive demo store
        print("\n1. 🏪 Setting up comprehensive demo store...")
        setup_result = await tools.setup_demo_store(
            num_products=25, num_customers=12, num_orders=8
        )

        if setup_result["success"]:
            print("   ✅ Demo store created successfully!")
            print(setup_result["summary"])
        else:
            print(f"   ❌ Setup failed: {setup_result.get('message', 'Unknown error')}")

        # 2. Perform comprehensive store analysis
        print("\n2. 📊 Analyzing store performance...")
        analysis_result = await tools.analyze_store_performance()

        if analysis_result["success"]:
            data = analysis_result["data"]
            overview = data["overview"]
            products = data["products"]

            print("   ✅ Store analysis completed!")
            print(f"   📈 Total Revenue: ${overview['total_revenue']:.2f}")
            print(f"   🛍️  Average Order Value: ${overview['average_order_value']:.2f}")
            print(f"   📦 Product Categories: {len(products['categories'])}")
            print(f"   🔴 Low Stock Items: {products['stock_levels']['low']}")

            if data["recommendations"]:
                print("   💡 Key Recommendations:")
                for rec in data["recommendations"][:3]:
                    print(f"      • {rec}")
        else:
            print(
                f"   ❌ Analysis failed: {analysis_result.get('message', 'Unknown error')}"
            )

        # 3. Intelligent inventory management
        print("\n3. 📦 Performing intelligent inventory analysis...")
        inventory_result = await tools.intelligent_inventory_management(threshold=20)

        if inventory_result["success"]:
            inv_data = inventory_result["data"]
            overview = inv_data["inventory_overview"]
            financial = inv_data["financial_impact"]

            print("   ✅ Inventory analysis completed!")
            print(
                f"   📊 Low Stock Percentage: {overview['low_stock_percentage']:.1f}%"
            )
            print(
                f"   💰 Estimated Restock Cost: ${financial['total_estimated_cost']:.2f}"
            )
            print(f"   🔥 High Priority Items: {financial['high_priority_items']}")

            # Show top 3 restock recommendations
            restock_plan = inv_data["restock_plan"]
            if restock_plan:
                print("   📋 Top Restock Recommendations:")
                for item in restock_plan[:3]:
                    print(
                        f"      • {item['product_name']}: {item['current_stock']} → {item['new_stock_level']}"
                    )

                # Demo auto-restocking
                print("\n   🤖 Executing auto-restock for high-priority items...")
                high_priority = [
                    item for item in restock_plan if item["priority"] == "high"
                ]

                if high_priority:
                    restock_result = await tools.execute_auto_restock(high_priority[:3])
                    if restock_result["success"]:
                        print(
                            f"      ✅ Auto-restocked {len(restock_result['data']['executed_restocks'])} products"
                        )
                    else:
                        print(
                            f"      ❌ Auto-restock failed: {restock_result.get('message', 'Unknown error')}"
                        )

        # 4. Test complex planning with natural language
        print("\n4. 🧠 Testing natural language planning...")

        test_requests = [
            "setup demo store",
            "generate analytics report",
            "analyze inventory and restock",
        ]

        for request in test_requests:
            print(f"   🗣️  Request: '{request}'")
            plan_result = await tools.execute_complex_plan(request)

            if plan_result["success"]:
                print("      ✅ Executed successfully")
            else:
                print(f"      ❌ Failed: {plan_result.get('message', 'Unknown error')}")

        # 5. Generate final summary
        print("\n5. 📋 Generating final business summary...")
        final_analysis = await tools.analyze_store_performance()

        if final_analysis["success"]:
            data = final_analysis["data"]

            print("\n" + "=" * 60)
            print("📊 BUSINESS INTELLIGENCE SUMMARY")
            print("=" * 60)

            print("💼 Store Overview:")
            print(f"   • Products: {data['overview']['total_products']}")
            print(f"   • Customers: {data['overview']['total_customers']}")
            print(f"   • Orders: {data['overview']['total_orders']}")
            print(f"   • Revenue: ${data['overview']['total_revenue']:.2f}")

            print("\n📈 Performance Metrics:")
            print(
                f"   • Average Order Value: ${data['overview']['average_order_value']:.2f}"
            )
            print(
                f"   • Customer Order Ratio: {data['overview']['total_orders'] / max(data['overview']['total_customers'], 1):.2f}"
            )

            categories = data["products"]["categories"]
            top_category = (
                max(categories.items(), key=lambda x: x[1])
                if categories
                else ("None", 0)
            )
            print(f"   • Top Category: {top_category[0]} ({top_category[1]} products)")

            print("\n💡 Strategic Recommendations:")
            for rec in data["recommendations"]:
                print(f"   • {rec}")

            print("\n🎯 Next Steps:")
            print("   • Monitor inventory levels regularly")
            print("   • Implement automated restocking alerts")
            print("   • Focus on customer retention strategies")
            print("   • Consider expanding successful product categories")

        print("\n" + "=" * 60)
        print("🎉 Enhanced Agent Demo Completed Successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        import traceback

        traceback.print_exc()


async def interactive_demo():
    """Interactive demo where user can try different commands."""
    print("\n🔧 Interactive Mode")
    print("=" * 40)
    print("Try these commands:")
    print("• 'setup demo store'")
    print("• 'generate analytics report'")
    print("• 'analyze inventory'")
    print("• 'quit' to exit")
    print("=" * 40)

    tools = EnhancedMCPTools()

    while True:
        try:
            user_input = input("\n🤖 Enter command: ").strip()

            if user_input.lower() in ["quit", "exit", "q"]:
                print("👋 Goodbye!")
                break

            if not user_input:
                continue

            print(f"🔄 Processing: {user_input}")
            result = await tools.execute_complex_plan(user_input)

            if result["success"]:
                print(f"✅ Success: {result.get('message', 'Operation completed')}")
                if "summary" in result:
                    print(result["summary"])
            else:
                print(f"❌ Error: {result.get('message', 'Unknown error')}")

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")


def main():
    """Main function to run the demo."""
    import argparse

    parser = argparse.ArgumentParser(description="Enhanced E-commerce Agent Demo")
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Run in interactive mode"
    )

    args = parser.parse_args()

    if args.interactive:
        asyncio.run(interactive_demo())
    else:
        asyncio.run(demo_enhanced_agent())


if __name__ == "__main__":
    main()
