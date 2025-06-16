#!/usr/bin/env python3

import asyncio


async def test_simple():
    print("🧪 Starting simple test...")

    # Test a simple search query simulation
    search_term = "laptop"
    print(f"Search term: {search_term}")

    # Simulate the logic
    if search_term.lower() in ["laptop", "headset", "microphone"]:
        print("✅ Simple mapping would work")
    else:
        print("❌ No mapping found")

    print("Test completed!")


if __name__ == "__main__":
    asyncio.run(test_simple())
