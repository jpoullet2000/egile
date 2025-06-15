#!/usr/bin/env python3
"""
Test to verify the new stock level is displayed correctly in confirmation messages.
"""

import asyncio
import logging
import sys

sys.path.append("/home/jbp/projects/egile/chatbot-agent")
from grok_agent import GrokEcommerceAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_stock_level_display():
    """
    Test that confirmation messages show the actual new stock level, not the change amount
    """
    print("🔍 Testing stock level display in confirmation messages...")
    
    agent = GrokEcommerceAgent()
    
    try:
        await agent.start()
        print("✅ Agent started successfully\n")
        
        # First, let's see the current stock of Test Laptop
        print("📋 Checking current product list...")
        products_response = await agent.process_message("show me all products")
        print("Current stock levels shown in product list.")
        
        print("\n" + "="*60)
        
        # Test increment operation
        print("🧪 Test 1: Increment operation (should show total after adding)")
        test_message = 'update stock "test laptop" by 5'
        print(f"Command: {test_message}")
        
        response = await agent.process_message(test_message)
        message = response.get("message", "")
        print(f"\n📄 Response:\n{message}")
        
        # Extract the stock level from the response
        import re
        stock_match = re.search(r"New Stock Level:\s*(\d+)\s*units", message)
        if stock_match:
            confirmed_stock = int(stock_match.group(1))
            print(f"\n✅ Confirmed stock level: {confirmed_stock}")
        else:
            print("\n❌ Could not extract stock level from response")
        
        print("\n" + "="*60)
        
        # Test set operation
        print("🧪 Test 2: Set operation (should show the exact set value)")
        test_message = 'set test laptop stock to 50'
        print(f"Command: {test_message}")
        
        response = await agent.process_message(test_message)
        message = response.get("message", "")
        print(f"\n📄 Response:\n{message}")
        
        # Extract the stock level from the response
        stock_match = re.search(r"New Stock Level:\s*(\d+)\s*units", message)
        if stock_match:
            confirmed_stock = int(stock_match.group(1))
            print(f"\n✅ Confirmed stock level: {confirmed_stock}")
            if confirmed_stock == 50:
                print("✅ Correct! Shows the set value (50)")
            else:
                print("❌ Incorrect! Should show 50")
        else:
            print("\n❌ Could not extract stock level from response")
        
        print("\n" + "="*60)
        
        # Verify with product list
        print("📋 Final verification - checking product list...")
        products_response = await agent.process_message("show me all products")
        products_message = products_response.get("message", "")
        
        # Extract Test Laptop stock from product list
        laptop_match = re.search(r"Test Laptop.*?\|\s*📦\s*Stock:\s*(\d+)", products_message)
        if laptop_match:
            actual_stock = int(laptop_match.group(1))
            print(f"✅ Actual stock in database: {actual_stock}")
        else:
            print("❌ Could not find Test Laptop in product list")
        
        print("\n✅ Test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if agent.ecommerce_agent:
            await agent.stop()
            print("🛑 Agent stopped")

if __name__ == "__main__":
    asyncio.run(test_stock_level_display())
