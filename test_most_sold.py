#!/usr/bin/env python3
"""
Test the most sold products functionality
"""

import asyncio
import sys

sys.path.append("/home/jbp/projects/egile/chatbot-agent")

from grok_agent import GrokEcommerceAgent


async def test_most_sold_products():
    """Test most sold products functionality"""
    agent = GrokEcommerceAgent()

    try:
        await agent.start()
        print("🚀 Testing most sold products functionality...")

        # Test the fallback intent analysis directly
        print("\n📝 Testing fallback intent analysis:")
        intent1 = await agent.fallback_intent_analysis(
            "what are the most sold products?"
        )
        print(f"Intent for 'most sold products': {intent1}")

        intent2 = await agent.fallback_intent_analysis("show me best selling products")
        print(f"Intent for 'best selling products': {intent2}")

        intent3 = await agent.fallback_intent_analysis("top selling products")
        print(f"Intent for 'top selling products': {intent3}")

        # Test the analysis method directly
        print("\n📝 Testing analyze_most_sold_products method:")
        result = await agent.analyze_most_sold_products()
        print(f"Analysis result success: {result.get('success', False)}")
        if result.get("data"):
            print(f"Number of products analyzed: {len(result['data'])}")
            print("Top 3 products by sales:")
            for i, product in enumerate(result["data"][:3], 1):
                name = product.get("name", "Unknown")
                total_sold = product.get("total_sold", 0)
                revenue = product.get("revenue_generated", 0)
                print(f"  {i}. {name}: {total_sold} units sold, ${revenue:.2f} revenue")

        # Test the full chatbot response
        print("\n📝 Testing full chatbot response:")
        result = await agent.process_message("what are the most sold products?")
        print(f"Chatbot result: {result.get('success', False)}")
        if result.get("message"):
            message = result["message"]
            print(f"Message preview: {message[:300]}...")

        print("\n✅ Most sold products testing completed!")

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(test_most_sold_products())
