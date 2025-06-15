#!/usr/bin/env python3
import sys

sys.path.append(".")

from egile.agent import EcommerceAgent
import asyncio


async def test_agent():
    try:
        print("Testing EcommerceAgent...")
        agent = EcommerceAgent()

        print("Starting agent...")
        await agent.start_server()

        print("Getting all products...")
        result = await agent.get_all_products()

        print(f"Result type: {type(result)}")
        print(f"Result: {result}")

        if hasattr(result, "data"):
            print(f"Result.data type: {type(result.data)}")
            print(f"Result.data: {result.data}")
            if result.data:
                print(f"First item type: {type(result.data[0])}")
                print(f"First item: {result.data[0]}")

        print("\nGetting all customers...")
        customer_result = await agent.get_all_customers()

        print(f"Customer result type: {type(customer_result)}")
        if hasattr(customer_result, "data"):
            print(f"Customer result.data: {customer_result.data}")
            if customer_result.data:
                print(f"First customer: {customer_result.data[0]}")

        await agent.stop_server()

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_agent())
