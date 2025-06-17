#!/usr/bin/env python3
"""
Interactive demo script for the Smart E-commerce Agent.

This script provides an interactive interface to test the enhanced
agent capabilities with complex planning and execution.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from egile.smart_agent import SmartAgent


async def interactive_demo():
    """Run interactive demo with the smart agent."""
    print("🤖 Smart E-commerce Agent - Interactive Demo")
    print("=" * 60)
    print("This agent can handle complex requests and create execution plans.")
    print("Try commands like:")
    print("• 'setup demo store with 15 products'")
    print("• 'show all products'")
    print("• 'generate analytics report'")
    print("• 'help' for more options")
    print("• 'quit' to exit")
    print("=" * 60)

    agent = SmartAgent()

    try:
        print("\n🚀 Starting agent...")
        await agent.start()
        print("✅ Agent ready!")

        while True:
            try:
                user_input = input("\n💬 You: ").strip()

                if user_input.lower() in ["quit", "exit", "q"]:
                    print("👋 Goodbye!")
                    break

                if not user_input:
                    continue

                print("🔄 Processing...")
                response = await agent.process_request(user_input)

                print(f"🤖 Agent: {response.get('message', 'No response')}")

                # Show additional info for certain response types
                if response.get("type") == "plan_created":
                    plan_info = response.get("plan", {})
                    print(f"   📋 Plan ID: {plan_info.get('id', 'unknown')}")
                    print(f"   📊 Steps: {plan_info.get('steps', 0)}")

                elif response.get("type") == "product_list":
                    data = response.get("data", [])
                    if data:
                        print(f"   📦 Found {len(data)} products:")
                        for i, product in enumerate(data[:3]):  # Show first 3
                            name = product.get("name", "Unknown")
                            price = product.get("price", 0)
                            print(f"   {i + 1}. {name} - ${price:.2f}")
                        if len(data) > 3:
                            print(f"   ... and {len(data) - 3} more")

                elif response.get("type") == "plan_completed":
                    results = response.get("results", [])
                    successful = len([r for r in results if r.get("success")])
                    print(
                        f"   ✅ Completed: {successful}/{len(results)} steps successful"
                    )

                # Handle errors
                if not response.get("success", True):
                    suggestions = response.get("suggestions", [])
                    if suggestions:
                        print("   💡 Try these instead:")
                        for suggestion in suggestions[:3]:
                            print(f"   • {suggestion}")

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")

    finally:
        print("\n🛑 Shutting down agent...")
        await agent.stop()
        print("✅ Agent stopped")


async def automated_demo():
    """Run automated demo with predefined commands."""
    print("🤖 Smart Agent - Automated Demo")
    print("=" * 50)

    agent = SmartAgent()

    demo_commands = [
        ("Show available products", "show all products"),
        ("Setup demo store", "setup demo store with 10 products"),
        ("Confirm setup", "yes"),
        ("List products again", "show all products"),
        ("Search for electronics", "search electronics"),
        ("Generate analytics", "generate analytics report"),
        ("Confirm analytics", "yes"),
        ("Get help", "help"),
    ]

    try:
        print("🚀 Starting agent...")
        await agent.start()
        print("✅ Agent ready!\n")

        for description, command in demo_commands:
            print(f"📋 {description}")
            print(f"💬 User: {command}")

            response = await agent.process_request(command)
            message = response.get("message", "No response")

            # Truncate long messages for demo
            if len(message) > 200:
                message = message[:200] + "..."

            print(f"🤖 Agent: {message}")

            if response.get("type") == "plan_created":
                print("   📋 Plan created and awaiting confirmation")
            elif response.get("type") == "plan_completed":
                print("   ✅ Plan executed successfully")

            print()  # Blank line
            await asyncio.sleep(1)  # Brief pause for readability

        print("🎉 Automated demo completed!")

    finally:
        await agent.stop()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Smart Agent Demo")
    parser.add_argument(
        "--auto", action="store_true", help="Run automated demo instead of interactive"
    )

    args = parser.parse_args()

    if args.auto:
        asyncio.run(automated_demo())
    else:
        asyncio.run(interactive_demo())


if __name__ == "__main__":
    main()
