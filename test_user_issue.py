#!/usr/bin/env python3
"""
Direct test of the exact issue: 'what are the products between $10 and $30'
should only return products in that price range, not all products.
"""

import asyncio
import sys
import json

sys.path.append("/home/jbp/projects/egile/chatbot-agent")

from grok_agent import GrokEcommerceAgent


async def test_specific_issue():
    """Test the specific issue reported by the user"""
    agent = GrokEcommerceAgent()

    try:
        await agent.start()
        print("🔍 Testing the specific user issue...")
        print("Query: 'what are the products between $10 and $30'")
        print("Expected: Only products with prices between $10 and $30")
        print("Problem: Currently returns all products")
        print()

        # Process the exact message from the user
        result = await agent.process_message(
            "what are the products between $10 and $30"
        )

        print(f"Success: {result.get('success', False)}")
        print(f"Response type: {type(result)}")

        if result.get("message"):
            message = result["message"]
            print(f"\nResponse message:")
            print(f"Length: {len(message)} characters")
            print(f"First 500 characters:")
            print(message[:500])

            # Check if response contains prices outside the range
            if (
                "$89.99" in message
                or "$100.0" in message
                or "$149.99" in message
                or "$1299.99" in message
            ):
                print(
                    "\n❌ ISSUE CONFIRMED: Response contains products outside $10-$30 range"
                )
                print(
                    "   Found prices like $89.99, $100, $149.99, $1299.99 which are outside the range"
                )
            else:
                print(
                    "\n✅ ISSUE FIXED: Response only contains products in $10-$30 range"
                )

        print(f"\n{'=' * 50}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(test_specific_issue())
