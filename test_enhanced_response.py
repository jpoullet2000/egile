#!/usr/bin/env python3
"""
Test the enhanced stock update response with detailed product information
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "chatbot-agent"))

from grok_agent import GrokEcommerceAgent


async def test_enhanced_stock_response():
    """Test the enhanced stock update response"""
    agent = GrokEcommerceAgent()

    try:
        await agent.start()
        print("✅ Agent started successfully")

        test_cases = [
            'update stock of "Test Laptop" by 5',
            'update stock laptop pro by 3',
        ]

        for command in test_cases:
            print(f"\n{'='*60}")
            print(f"Testing: {command}")
            print(f"{'='*60}")
            
            response = await agent.process_message(command)
            print(f"Response:\n{response.get('message', 'No message')}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(test_enhanced_stock_response())
