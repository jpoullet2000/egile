#!/usr/bin/env python3
"""
Test enhanced confirmation message for stock updates.
"""

import asyncio
import logging
import sys

sys.path.append("/home/jbp/projects/egile/chatbot-agent")
from grok_agent import GrokEcommerceAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_enhanced_confirmation():
    """
    Test the enhanced confirmation message specifically
    """
    print("🔍 Testing enhanced confirmation messages...")
    
    agent = GrokEcommerceAgent()
    
    try:
        await agent.start()
        print("✅ Agent started successfully\n")
        
        # Test single stock update with detailed analysis
        test_message = "update laptop stock by 5"
        print(f"🧪 Testing: '{test_message}'")
        
        response = await agent.process_message(test_message)
        
        print(f"📤 Response type: {response.get('type')}")
        print(f"📤 Success: {response.get('action_result', {}).get('success', 'Unknown')}")
        
        message = response.get("message", "")
        intent = response.get("intent", {})
        
        print(f"\n📄 Full message:\n{message}")
        print(f"\n📋 Intent parameters: {intent.get('parameters', {})}")
        
        # Test if get_product_details works directly
        product_id = intent.get("parameters", {}).get("product_id")
        if product_id:
            print(f"\n🔍 Testing get_product_details for {product_id}...")
            product_details = await agent.get_product_details(product_id)
            print(f"📦 Product details: {product_details}")
        
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
    asyncio.run(test_enhanced_confirmation())
