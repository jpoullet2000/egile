#!/usr/bin/env python3
"""
AI Agent that uses Grok 3 LLM to interact with the Ecommerce MCP Server.
This agent provides intelligent, conversational responses while executing e-commerce operations.
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from egile.agent import EcommerceAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GrokEcommerceAgent:
    def __init__(self, api_key: Optional[str] = None):
        self.grok_api_key = api_key or os.getenv("XAI_API_KEY")
        self.ecommerce_agent: Optional[EcommerceAgent] = None
        self.conversation_history: List[Dict[str, str]] = []

        if not self.grok_api_key:
            logger.warning(
                "No XAI API key provided. Set XAI_API_KEY environment variable or pass api_key parameter."
            )

    async def start(self):
        """Initialize the ecommerce agent"""
        try:
            self.ecommerce_agent = EcommerceAgent()
            await self.ecommerce_agent.start_server()
            logger.info("Ecommerce MCP agent started successfully")
        except Exception as e:
            logger.error(f"Failed to start ecommerce agent: {e}")
            raise

    async def stop(self):
        """Stop the ecommerce agent"""
        if self.ecommerce_agent:
            await self.ecommerce_agent.stop_server()
            logger.info("Ecommerce MCP agent stopped")

    async def process_message(self, user_message: str) -> Dict[str, Any]:
        """Process a user message using Grok 3 and execute ecommerce operations"""
        try:
            # Add user message to conversation history
            self.conversation_history.append({"role": "user", "content": user_message})

            # Analyze the message with Grok 3 to determine intent and extract parameters
            intent_analysis = await self.analyze_intent_with_grok(user_message)

            # Execute the appropriate ecommerce operation
            if intent_analysis.get("requires_action", False):
                action_result = await self.execute_ecommerce_action(intent_analysis)

                # Generate a conversational response with Grok 3
                response = await self.generate_response_with_grok(
                    user_message, intent_analysis, action_result
                )
            else:
                # Generate a conversational response without action
                response = await self.generate_response_with_grok(
                    user_message, intent_analysis
                )

            # Add assistant response to conversation history
            self.conversation_history.append(
                {"role": "assistant", "content": response.get("message", "")}
            )

            return response

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "type": "error",
                "message": f"I encountered an error: {str(e)}. Please try again.",
            }

    async def analyze_intent_with_grok(self, message: str) -> Dict[str, Any]:
        """Analyze user intent using Grok 3"""
        if not self.grok_api_key:
            # Fallback to simple pattern matching if no API key
            return self.fallback_intent_analysis(message)

        try:
            import httpx

            system_prompt = """You are an AI assistant for an e-commerce system. Analyze the user's message and determine:
1. What action they want to perform (if any)
2. Extract any parameters needed
3. Determine if this requires executing an e-commerce operation

Available operations:
- list_products: Show all products
- create_product: Create a new product (needs: name, price, sku, category, stock_quantity)
- get_product: Get product details (needs: product_id or sku)
- search_products: Search products (needs: query)
- list_customers: Show all customers
- create_customer: Create customer (needs: email, first_name, last_name, optional: phone)
- get_customer: Get customer details (needs: customer_id or email)
- list_orders: Show all orders
- create_order: Create order (needs: customer_id, product_id, quantity)
- get_order: Get order details (needs: order_id)
- get_low_stock_products: Show low stock items (optional: threshold)
- update_stock: Update product stock (needs: product_id, quantity)

Respond with JSON format:
{
    "intent": "description of what user wants",
    "action": "operation_name or null",
    "parameters": {...},
    "requires_action": true/false,
    "confidence": 0.0-1.0
}"""

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.x.ai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.grok_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": message},
                        ],
                        "model": "grok-beta",
                        "stream": False,
                        "temperature": 0.1,
                    },
                    timeout=30.0,
                )

                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]

                    # Try to parse JSON response
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError:
                        # If JSON parsing fails, extract intent manually
                        return self.fallback_intent_analysis(message)
                else:
                    logger.warning(f"Grok API error: {response.status_code}")
                    return self.fallback_intent_analysis(message)

        except Exception as e:
            logger.warning(f"Failed to use Grok API: {e}")
            return self.fallback_intent_analysis(message)

    def fallback_intent_analysis(self, message: str) -> Dict[str, Any]:
        """Fallback intent analysis using simple pattern matching"""
        message_lower = message.lower().strip()

        # Product operations
        if "list products" in message_lower or "show products" in message_lower:
            return {
                "intent": "List all products",
                "action": "list_products",
                "parameters": {},
                "requires_action": True,
                "confidence": 0.9,
            }

        if "create product" in message_lower:
            return {
                "intent": "Create a new product",
                "action": "create_product",
                "parameters": self.extract_product_params(message),
                "requires_action": True,
                "confidence": 0.8,
            }

        if "search" in message_lower and "product" in message_lower:
            query = (
                message_lower.replace("search", "")
                .replace("product", "")
                .replace("for", "")
                .strip()
            )
            return {
                "intent": "Search for products",
                "action": "search_products",
                "parameters": {"query": query},
                "requires_action": True,
                "confidence": 0.8,
            }

        # Customer operations
        if "list customers" in message_lower or "show customers" in message_lower:
            return {
                "intent": "List all customers",
                "action": "list_customers",
                "parameters": {},
                "requires_action": True,
                "confidence": 0.9,
            }

        # Order operations
        if "list orders" in message_lower or "show orders" in message_lower:
            return {
                "intent": "List all orders",
                "action": "list_orders",
                "parameters": {},
                "requires_action": True,
                "confidence": 0.9,
            }

        # Stock operations
        if "low stock" in message_lower or "stock low" in message_lower:
            return {
                "intent": "Check low stock items",
                "action": "get_low_stock_products",
                "parameters": {"threshold": 10},
                "requires_action": True,
                "confidence": 0.8,
            }

        # Default - no action needed
        return {
            "intent": "General conversation or help request",
            "action": None,
            "parameters": {},
            "requires_action": False,
            "confidence": 0.5,
        }

    def extract_product_params(self, message: str) -> Dict[str, Any]:
        """Extract product parameters from message"""
        import re

        # Try to match: create product "name" price sku category stock
        pattern = r'create product "([^"]+)" ([\d.]+) (\S+) (\S+) (\d+)'
        match = re.search(pattern, message, re.IGNORECASE)

        if match:
            name, price, sku, category, stock = match.groups()
            return {
                "name": name,
                "description": f"{name} - {category}",
                "price": float(price),
                "sku": sku,
                "category": category,
                "stock_quantity": int(stock),
            }

        return {}

    async def execute_ecommerce_action(
        self, intent_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the determined ecommerce action"""
        action = intent_analysis.get("action")
        parameters = intent_analysis.get("parameters", {})

        if not self.ecommerce_agent:
            raise Exception("Ecommerce agent not initialized")

        # Map actions to agent methods
        action_mapping = {
            "list_products": "get_all_products",
            "create_product": "create_product",
            "get_product": "get_product",
            "search_products": "search_products",
            "list_customers": "get_all_customers",
            "create_customer": "create_customer",
            "get_customer": "get_customer",
            "list_orders": "get_all_orders",
            "create_order": "create_order",
            "get_order": "get_order",
            "get_low_stock_products": "get_low_stock_products",
            "update_stock": "update_stock",
        }

        if action not in action_mapping:
            raise Exception(f"Unknown action: {action}")

        method_name = action_mapping[action]
        method = getattr(self.ecommerce_agent, method_name)

        # Execute the method
        if parameters:
            result = await method(**parameters)
        else:
            result = await method()

        return {"action": action, "result": result, "success": True}

    async def generate_response_with_grok(
        self,
        user_message: str,
        intent_analysis: Dict[str, Any],
        action_result: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate a conversational response using Grok 3"""
        if not self.grok_api_key:
            # Fallback to simple response formatting
            return self.fallback_response_generation(intent_analysis, action_result)

        try:
            import httpx

            # Prepare context for Grok
            context = f"User intent: {intent_analysis.get('intent')}\n"

            if action_result:
                context += f"Action performed: {action_result.get('action')}\n"
                context += (
                    f"Result: {json.dumps(action_result.get('result'), indent=2)}\n"
                )

            system_prompt = """You are a helpful and friendly e-commerce assistant. Based on the user's message and any actions performed, provide a conversational and informative response. 

Guidelines:
- Be conversational and friendly
- If data was retrieved, present it in a clear, organized way
- Use emojis appropriately to make responses engaging
- If an action was successful, confirm what was done
- If no action was needed, provide helpful information or suggestions
- Keep responses concise but informative"""

            conversation_context = ""
            if len(self.conversation_history) > 6:  # Keep last 3 exchanges
                conversation_context = json.dumps(self.conversation_history[-6:])
            else:
                conversation_context = json.dumps(self.conversation_history)

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.x.ai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.grok_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {
                                "role": "user",
                                "content": f"Context: {context}\n\nConversation history: {conversation_context}\n\nUser message: {user_message}\n\nGenerate a helpful response.",
                            },
                        ],
                        "model": "grok-beta",
                        "stream": False,
                        "temperature": 0.7,
                    },
                    timeout=30.0,
                )

                if response.status_code == 200:
                    result = response.json()
                    message = result["choices"][0]["message"]["content"]

                    return {
                        "type": "chat_response",
                        "message": message,
                        "intent": intent_analysis,
                        "action_result": action_result,
                    }
                else:
                    logger.warning(f"Grok API error: {response.status_code}")
                    return self.fallback_response_generation(
                        intent_analysis, action_result
                    )

        except Exception as e:
            logger.warning(f"Failed to generate response with Grok: {e}")
            return self.fallback_response_generation(intent_analysis, action_result)

    def fallback_response_generation(
        self,
        intent_analysis: Dict[str, Any],
        action_result: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Fallback response generation without Grok"""
        if not action_result:
            return {
                "type": "chat_response",
                "message": "I understand you want help with your e-commerce operations. Try asking me to 'list products', 'show customers', or 'check low stock items'.",
                "intent": intent_analysis,
            }

        action = action_result.get("action")
        result = action_result.get("result")

        # Format response based on action type
        if action == "list_products":
            if result and len(result) > 0:
                message = f"📦 I found {len(result)} product(s) in your catalog:\n\n"
                for product in result[:5]:  # Show first 5
                    message += f"• **{product.get('name')}** ({product.get('sku')})\n"
                    message += f"  💰 ${product.get('price')} | 📦 Stock: {product.get('stock_quantity')}\n\n"
                if len(result) > 5:
                    message += f"... and {len(result) - 5} more products."
            else:
                message = "📦 No products found in your catalog. Would you like to create some?"

        elif action == "list_customers":
            if result and len(result) > 0:
                message = f"👥 I found {len(result)} customer(s):\n\n"
                for customer in result[:5]:
                    message += f"• **{customer.get('first_name')} {customer.get('last_name')}**\n"
                    message += f"  📧 {customer.get('email')}\n\n"
                if len(result) > 5:
                    message += f"... and {len(result) - 5} more customers."
            else:
                message = "👥 No customers found. Ready to add your first customer?"

        elif action == "get_low_stock_products":
            if result and len(result) > 0:
                message = f"⚠️ {len(result)} product(s) are running low on stock:\n\n"
                for product in result:
                    message += f"• **{product.get('name')}** - Only {product.get('stock_quantity')} left!\n"
            else:
                message = "🎉 Great news! All products are well-stocked."

        else:
            message = f"✅ Operation completed successfully! Action: {action}"

        return {
            "type": "chat_response",
            "message": message,
            "intent": intent_analysis,
            "action_result": action_result,
        }


async def main():
    """Test the Grok agent"""
    agent = GrokEcommerceAgent()
    await agent.start()

    try:
        # Test conversation
        test_messages = [
            "Hello! Can you show me all products?",
            "What customers do we have?",
            "Are there any products with low stock?",
        ]

        for message in test_messages:
            print(f"\nUser: {message}")
            response = await agent.process_message(message)
            print(f"Assistant: {response.get('message', 'No response')}")

    finally:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
