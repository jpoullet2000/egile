#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the project paths
sys.path.append("/home/jbp/projects/egile/chatbot-agent")
sys.path.append("/home/jbp/projects/egile")


async def test_microphone_search():
    try:
        from grok_agent import GrokEcommerceAgent

        agent = GrokEcommerceAgent()
        await agent.start()

        print("Testing microphone mapping...")

        # Test the mapping directly
        result = await agent._get_dynamic_product_mapping("microphone_egile")
        print(f"Mapping result for 'microphone_egile': {result}")

        # Test order creation
        response = await agent.process_message(
            "create order for demo for 1 microphone egile"
        )
        print(f"Order response: {response.get('message', '')[:100]}...")

        await agent.stop()
        print("Test completed!")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_microphone_search())
