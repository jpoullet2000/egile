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
        # Product creation state management
        self.product_creation_state: Optional[Dict[str, Any]] = None

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

            # Check if we're in the middle of creating a product
            if self.product_creation_state:
                return await self.handle_product_creation_step(user_message)

            # Analyze the message with Grok 3 to determine intent and extract parameters
            intent_analysis = await self.analyze_intent_with_grok(user_message)

            # Execute the appropriate ecommerce operation
            if intent_analysis.get("requires_action", False):
                action_result = await self.execute_ecommerce_action(intent_analysis)

                # For interactive actions, return the result directly without Grok processing
                action = intent_analysis.get("action")
                if action in ["help_create_product", "request_product_details"]:
                    # Add assistant response to conversation history
                    self.conversation_history.append(
                        {
                            "role": "assistant",
                            "content": action_result.get("message", ""),
                        }
                    )
                    return action_result

                # For data retrieval actions, use fallback formatting without Grok
                data_actions = [
                    "list_products",
                    "list_customers",
                    "list_orders",
                    "get_low_stock_products",
                    "search_products",
                    "get_product",
                    "get_customer",
                    "get_order",
                ]
                if action in data_actions:
                    # Use direct fallback formatting for data display
                    response = self.fallback_response_generation(
                        intent_analysis, action_result
                    )
                    self.conversation_history.append(
                        {"role": "assistant", "content": response.get("message", "")}
                    )
                    return response

                # Generate a conversational response with Grok 3 for other actions
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

            system_prompt = """You are an AI assistant for an e-commerce system. Analyze the user's message and determine what they want to do. Be flexible with natural language - understand common ways people ask about things.

For example:
- "what are my products?" = list_products
- "show me all products" = list_products  
- "what do I have in stock?" = list_products
- "most expensive products" = list_products with sort_by: "price_desc"
- "cheapest products" = list_products with sort_by: "price_asc"
- "products by price" = list_products with sort_by: "price_desc"
- "who are my customers?" = list_customers
- "show me orders" = list_orders
- "what's running low?" = get_low_stock_products
- "help me create a product" = create_product (if details provided) or help_create_product (if no details)
- "I want to add a new product" = create_product or help_create_product

Available operations:
- list_products: Show all products (supports parameters: sort_by: "price_desc"|"price_asc"|"name"|"stock", limit: number)
- create_product: Create a new product (needs: name, description, price, sku, category, stock_quantity)
- help_create_product: Provide guidance on creating products (when user asks for help but provides no details)
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

IMPORTANT: 
- Be generous in interpreting user intent
- For product queries with sorting (expensive, cheap, etc.), use list_products with appropriate sort_by parameter
- If someone asks about "most expensive" or "highest priced", use sort_by: "price_desc"
- If someone asks about "cheapest" or "lowest priced", use sort_by: "price_asc"
- You can add a limit parameter for "top 5" or similar requests
- If someone asks about creating/adding products but doesn't provide all details, use help_create_product
- If they provide partial details, extract what you can and set action to create_product
- For product creation, try to extract: name, description, price, sku, category, stock_quantity

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
                        "model": "grok-3",
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

        # Expensive/cheap product patterns - check these first
        expensive_patterns = [
            "most expensive",
            "highest priced",
            "priciest",
            "costliest",
            "expensive products",
            "highest price",
            "most costly",
        ]

        cheap_patterns = [
            "cheapest",
            "lowest priced",
            "least expensive",
            "cheap products",
            "lowest price",
            "most affordable",
        ]

        if any(pattern in message_lower for pattern in expensive_patterns):
            # Extract limit if mentioned (like "top 5 most expensive")
            import re

            limit_match = re.search(r"top (\d+)|first (\d+)|(\d+) most", message_lower)
            limit = None
            if limit_match:
                limit = int(
                    limit_match.group(1) or limit_match.group(2) or limit_match.group(3)
                )

            params = {"sort_by": "price_desc"}
            if limit:
                params["limit"] = limit

            return {
                "intent": f"Show {'top ' + str(limit) + ' ' if limit else ''}most expensive products",
                "action": "list_products",
                "parameters": params,
                "requires_action": True,
                "confidence": 0.9,
            }

        if any(pattern in message_lower for pattern in cheap_patterns):
            # Extract limit if mentioned
            import re

            limit_match = re.search(
                r"top (\d+)|first (\d+)|(\d+) cheapest", message_lower
            )
            limit = None
            if limit_match:
                limit = int(
                    limit_match.group(1) or limit_match.group(2) or limit_match.group(3)
                )

            params = {"sort_by": "price_asc"}
            if limit:
                params["limit"] = limit

            return {
                "intent": f"Show {'top ' + str(limit) + ' ' if limit else ''}cheapest products",
                "action": "list_products",
                "parameters": params,
                "requires_action": True,
                "confidence": 0.9,
            }

        # Product operations - more flexible patterns
        product_list_patterns = [
            "what are my products",
            "show me products",
            "list products",
            "show products",
            "what products do",
            "products available",
            "show all products",
            "list all products",
            "what's in stock",
            "what do I have",
            "my inventory",
            "show inventory",
            "what items",
            "what do we have",
            "product list",
            "all products",
        ]

        if any(pattern in message_lower for pattern in product_list_patterns):
            return {
                "intent": "List all products",
                "action": "list_products",
                "parameters": {},
                "requires_action": True,
                "confidence": 0.9,
            }

        # Customer operations - flexible patterns
        customer_list_patterns = [
            "show customers",
            "list customers",
            "who are my customers",
            "customer list",
            "show me customers",
            "all customers",
            "customer base",
            "my clients",
        ]

        if any(pattern in message_lower for pattern in customer_list_patterns):
            return {
                "intent": "List all customers",
                "action": "list_customers",
                "parameters": {},
                "requires_action": True,
                "confidence": 0.9,
            }

        # Order operations
        order_list_patterns = [
            "show orders",
            "list orders",
            "order history",
            "recent orders",
            "what orders",
            "show me orders",
            "all orders",
            "order list",
        ]

        if any(pattern in message_lower for pattern in order_list_patterns):
            return {
                "intent": "List all orders",
                "action": "list_orders",
                "parameters": {},
                "requires_action": True,
                "confidence": 0.9,
            }

        # Low stock patterns
        low_stock_patterns = [
            "low stock",
            "running low",
            "stock levels",
            "inventory levels",
            "what's low",
            "low inventory",
            "need to reorder",
            "stock shortage",
        ]

        if any(pattern in message_lower for pattern in low_stock_patterns):
            return {
                "intent": "Check low stock items",
                "action": "get_low_stock_products",
                "parameters": {},
                "requires_action": True,
                "confidence": 0.9,
            }

        # Create product patterns
        create_product_patterns = [
            "create product",
            "add product",
            "new product",
            "add new product",
            "help me create",
            "i want to create",
            "create a product",
            "add a product",
        ]
        if any(pattern in message_lower for pattern in create_product_patterns):
            params = self.extract_product_params(message)
            # If no params extracted, this is a request for help with product creation
            if not params:
                return {
                    "intent": "Request help for creating a new product",
                    "action": "help_create_product",
                    "parameters": {},
                    "requires_action": True,
                    "confidence": 0.9,
                }
            # If partial params (just name), ask for more details
            elif params.get("partial"):
                return {
                    "intent": f"Request details for creating product: {params.get('name')}",
                    "action": "request_product_details",
                    "parameters": params,
                    "requires_action": True,
                    "confidence": 0.9,
                }
            else:
                return {
                    "intent": "Create a new product",
                    "action": "create_product",
                    "parameters": params,
                    "requires_action": True,
                    "confidence": 0.8,
                }

        # Search products
        if "search" in message_lower and any(
            word in message_lower for word in ["product", "item", "for"]
        ):
            # Extract search query
            query_parts = (
                message_lower.replace("search", "")
                .replace("product", "")
                .replace("for", "")
                .replace("item", "")
                .strip()
            )
            return {
                "intent": "Search for products",
                "action": "search_products",
                "parameters": {"query": query_parts},
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

        # Try to match multiple patterns for product creation

        # Pattern 1: Structured format: create product "name" price sku category stock
        pattern1 = r'create product "([^"]+)" ([\d.]+) (\S+) (\S+) (\d+)'
        match = re.search(pattern1, message, re.IGNORECASE)
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

        # Pattern 2: Natural language with all fields
        # Example: "Create a product named iPhone 15, description: Latest Apple smartphone, price $999.99, SKU IP15-128, category Electronics, stock 50"
        name_match = re.search(
            r'(?:name[d]?|called)\s*:?\s*["\']?([^,\n]+?)["\']?(?:\s*,|$)',
            message,
            re.IGNORECASE,
        )
        desc_match = re.search(
            r'description\s*:?\s*["\']?([^,\n]+?)["\']?(?:\s*,|$)',
            message,
            re.IGNORECASE,
        )
        price_match = re.search(r"price[d]?\s*:?\s*\$?([\d.]+)", message, re.IGNORECASE)
        sku_match = re.search(
            r'sku\s*:?\s*["\']?([^\s,\n]+?)["\']?(?:\s*,|$)', message, re.IGNORECASE
        )
        category_match = re.search(
            r'category\s*:?\s*["\']?([^,\n]+?)["\']?(?:\s*,|$)', message, re.IGNORECASE
        )
        stock_match = re.search(
            r"stock\s*(?:quantity)?[:\s]*(\d+)", message, re.IGNORECASE
        )

        if name_match and price_match and sku_match and category_match and stock_match:
            name = name_match.group(1).strip()
            description = (
                desc_match.group(1).strip()
                if desc_match
                else f"{name} - {category_match.group(1).strip()}"
            )
            return {
                "name": name,
                "description": description,
                "price": float(price_match.group(1)),
                "sku": sku_match.group(1).strip(),
                "category": category_match.group(1).strip(),
                "stock_quantity": int(stock_match.group(1)),
            }

        # Pattern 3: Extract from "with" format
        # Example: "Create product "Test Phone" with description "Test smartphone", price $199.99, SKU TP-001, category Electronics, stock 10"
        product_name_match = re.search(
            r'(?:create|add)\s+product\s+["\']([^"\']+)["\']', message, re.IGNORECASE
        )
        if product_name_match:
            name = product_name_match.group(1)
            # Look for description in quotes after "description"
            desc_match = re.search(
                r'description\s+["\']([^"\']+)["\']', message, re.IGNORECASE
            )
            # Look for price with $ symbol
            price_match = re.search(r"price\s+\$?([\d.]+)", message, re.IGNORECASE)
            # Look for SKU
            sku_match = re.search(r"sku\s+([A-Za-z0-9-_]+)", message, re.IGNORECASE)
            # Look for category
            category_match = re.search(
                r"category\s+([A-Za-z]+)", message, re.IGNORECASE
            )
            # Look for stock
            stock_match = re.search(r"stock\s+(\d+)", message, re.IGNORECASE)

            if (
                desc_match
                and price_match
                and sku_match
                and category_match
                and stock_match
            ):
                return {
                    "name": name,
                    "description": desc_match.group(1),
                    "price": float(price_match.group(1)),
                    "sku": sku_match.group(1),
                    "category": category_match.group(1),
                    "stock_quantity": int(stock_match.group(1)),
                }

        # Pattern 4: Simple format with partial info - request more details
        simple_name_match = re.search(
            r'(?:add|create).*?(?:product|item).*?["\']([^"\']+)["\']',
            message,
            re.IGNORECASE,
        )
        if simple_name_match:
            # Found a product name but missing other details
            return {"partial": True, "name": simple_name_match.group(1).strip()}

        return {}

    async def help_create_product(self) -> Dict[str, Any]:
        """Start interactive product creation flow"""
        # Initialize product creation state
        self.product_creation_state = {
            "step": "name",
            "data": {},
            "steps": [
                "name",
                "description",
                "price",
                "sku",
                "category",
                "stock_quantity",
            ],
        }

        return {
            "type": "chat_response",
            "action": "help_create_product",
            "success": True,
            "message": """🚀 Let's create a new product together! I'll guide you through each step.

**Step 1 of 6: Product Name**
What would you like to name your product? 

For example: "iPhone 15 Pro" or "Wireless Gaming Mouse"

💡 *Tip: Choose a clear, descriptive name that customers will easily understand.*""",
        }

    async def request_product_details(
        self, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Request additional details for creating a product"""
        product_name = parameters.get("name", "your product")
        return {
            "action": "request_product_details",
            "success": True,
            "data": {
                "message": f"""Great! I see you want to create a product called "{product_name}". 

To complete the product creation, I need these additional details:

📝 **Missing Information:**
• **Description**: What is this product? (e.g., "Latest smartphone with advanced features")
• **Price**: How much does it cost? (e.g., 999.99)
• **SKU**: Unique product code (e.g., {product_name.replace(" ", "-").upper()}-001)
• **Category**: Product category (e.g., Electronics, Books, Clothing, etc.)
• **Stock Quantity**: How many units do you have? (e.g., 50)

💡 **Quick format:**
You can provide all details like this:
`Create "{product_name}" with description "your description here", price $X.XX, SKU YOUR-SKU, category YourCategory, stock XX`

Or just tell me each detail and I'll help you create it! 🚀""",
                "product_name": product_name,
            },
            "message": f"Please provide the missing details for {product_name}.",
        }

    async def handle_product_creation_step(self, user_message: str) -> Dict[str, Any]:
        """Handle each step of the interactive product creation process"""
        if not self.product_creation_state:
            return {"type": "error", "message": "No product creation in progress."}

        current_step = self.product_creation_state["step"]
        data = self.product_creation_state["data"]

        # Handle cancellation
        if user_message.lower().strip() in ["cancel", "quit", "stop", "exit"]:
            self.product_creation_state = None
            return {
                "type": "info",
                "message": "❌ Product creation cancelled. Feel free to start again anytime!",
            }

        # Process current step
        if current_step == "name":
            data["name"] = user_message.strip()
            self.product_creation_state["step"] = "description"
            return {
                "type": "chat_response",
                "message": f"""✅ Great! Product name: **{data["name"]}**

**Step 2 of 6: Description**
Please provide a description for your product.

For example: "Latest smartphone with advanced camera features" or "Ergonomic wireless mouse for gaming"

💡 *Tip: Include key features that customers would want to know about.*""",
            }

        elif current_step == "description":
            data["description"] = user_message.strip()
            self.product_creation_state["step"] = "price"
            return {
                "type": "chat_response",
                "message": """✅ Perfect! Description saved.

**Step 3 of 6: Price**
What's the price for this product? (in USD)

Examples: "99.99" or "1299" or "$29.99"

💡 *Tip: Just enter the number, with or without the $ symbol.*""",
            }

        elif current_step == "price":
            # Extract price from message
            import re

            price_match = re.search(r"(\d+\.?\d*)", user_message.replace("$", ""))
            if price_match:
                data["price"] = float(price_match.group(1))
                self.product_creation_state["step"] = "sku"
                return {
                    "type": "chat_response",
                    "message": f"""✅ Price set to: **${data["price"]:.2f}**

**Step 4 of 6: SKU (Product Code)**
Please provide a unique SKU (Stock Keeping Unit) for this product.

Examples: "IP15-PRO-256" or "MOUSE-WL-001" or "{data["name"].replace(" ", "-").upper()}-001"

💡 *Tip: Use letters, numbers, and dashes. Make it unique and memorable.*""",
                }
            else:
                return {
                    "type": "error",
                    "message": "❌ I couldn't understand the price. Please enter a number like '99.99' or '29'.",
                }

        elif current_step == "sku":
            data["sku"] = user_message.strip()
            self.product_creation_state["step"] = "category"
            return {
                "type": "chat_response",
                "message": f"""✅ SKU set to: **{data["sku"]}**

**Step 5 of 6: Category**
What category does this product belong to?

Examples: "Electronics", "Books", "Clothing", "Home & Garden", "Sports", "Toys"

💡 *Tip: Choose a broad category that helps organize your inventory.*""",
            }

        elif current_step == "category":
            data["category"] = user_message.strip()
            self.product_creation_state["step"] = "stock_quantity"
            return {
                "type": "chat_response",
                "message": f"""✅ Category set to: **{data["category"]}**

**Step 6 of 6: Stock Quantity**
How many units do you have in stock?

Examples: "50", "100", "25"

💡 *Tip: Enter the initial number of units you have available for sale.*""",
            }

        elif current_step == "stock_quantity":
            # Extract stock quantity
            import re

            stock_match = re.search(r"(\d+)", user_message)
            if stock_match:
                data["stock_quantity"] = int(stock_match.group(1))

                # All data collected, create the product
                try:
                    result = await self.ecommerce_agent.create_product(
                        name=data["name"],
                        description=data["description"],
                        price=data["price"],
                        sku=data["sku"],
                        category=data["category"],
                        stock_quantity=data["stock_quantity"],
                    )

                    # Clear the creation state
                    self.product_creation_state = None

                    if result.success:
                        return {
                            "type": "success",
                            "message": f"""🎉 **Product Created Successfully!**

📦 **Product Details:**
• **Name**: {data["name"]}
• **Description**: {data["description"]}
• **Price**: ${data["price"]:.2f}
• **SKU**: {data["sku"]}
• **Category**: {data["category"]}
• **Stock**: {data["stock_quantity"]} units

✅ Your product has been added to the catalog and is now available for sale!

Want to create another product? Just say "create a new product" or "help me create a product".""",
                        }
                    else:
                        return {
                            "type": "error",
                            "message": f"❌ Failed to create product: {result.error or 'Unknown error'}",
                        }

                except Exception as e:
                    self.product_creation_state = None
                    return {
                        "type": "error",
                        "message": f"❌ Error creating product: {str(e)}",
                    }
            else:
                return {
                    "type": "error",
                    "message": "❌ Please enter a valid number for stock quantity (e.g., '50' or '100').",
                }

        return {
            "type": "error",
            "message": "❌ Unknown step in product creation process.",
        }

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
            "help_create_product": "help_create_product",
            "request_product_details": "request_product_details",
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

        # Handle special cases
        if action == "help_create_product":
            return await self.help_create_product()
        elif action == "request_product_details":
            return await self.request_product_details(parameters)

        method_name = action_mapping[action]
        method = getattr(self.ecommerce_agent, method_name)

        # Handle special cases for actions that don't support certain parameters
        if action == "list_products" and parameters:
            # get_all_products doesn't accept parameters, but we might want to sort later
            # Store sorting info for post-processing
            sort_info = parameters.copy()
            logger.info(f"Storing sort_info for list_products: {sort_info}")
            parameters = {}  # Clear parameters for the actual method call
        else:
            sort_info = None

        # Execute the method
        if parameters:
            result = await method(**parameters)
        else:
            result = await method()

        # Post-process the result if sorting was requested
        if sort_info and action == "list_products":
            logger.info(f"Post-processing list_products with sort_info: {sort_info}")
            result = await self.post_process_product_list(result, sort_info)
        else:
            logger.info(f"No post-processing needed. sort_info: {sort_info}, action: {action}")

        # Extract data from AgentResponse for JSON serialization
        if hasattr(result, "data"):
            # The MCP agent returns data as [{'type': 'text', 'text': 'JSON_STRING'}]
            # We need to extract and parse the JSON string
            processed_data = result.data
            if (
                isinstance(processed_data, list)
                and len(processed_data) > 0
                and isinstance(processed_data[0], dict)
                and processed_data[0].get("type") == "text"
            ):
                try:
                    # Parse the JSON string to get actual objects
                    json_text = processed_data[0]["text"]
                    processed_data = json.loads(json_text)
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"Failed to parse JSON from MCP response: {e}")
                    # Keep original data if parsing fails
                    processed_data = result.data

            # Create a clean, JSON-serializable response
            return {
                "action": action,
                "success": result.success,
                "data": processed_data,
                "message": getattr(result, "message", ""),
                "error": getattr(result, "error", "") if not result.success else "",
            }
        else:
            # Handle case where result is raw data
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

        # Handle the new structure where we have direct data access
        if "data" in action_result:
            data = action_result.get("data", [])
            success = action_result.get("success", True)
            error_msg = action_result.get("error", "")
        else:
            # Fallback for old structure
            result = action_result.get("result")
            if hasattr(result, "data"):
                data = result.data if result.success else []
                success = result.success
                error_msg = result.error if hasattr(result, "error") else ""
            else:
                data = result
                success = True
                error_msg = ""

        if not success:
            return {
                "type": "chat_response",
                "message": f"❌ Error executing action: {error_msg}",
                "intent": intent_analysis,
            }

        # Format response based on action type
        if action == "list_products":
            if data and len(data) > 0:
                message = f"📦 I found {len(data)} product(s) in your catalog:\n\n"
                for product in data[:5]:  # Show first 5
                    # Debug: Check what type of object we have
                    logger.info(f"Product object type: {type(product)}")
                    logger.info(f"Product object: {product}")

                    # Handle dict objects (should be parsed JSON now)
                    if isinstance(product, dict):
                        message += (
                            f"• **{product.get('name')}** ({product.get('sku')})\n"
                        )
                        message += f"  💰 ${product.get('price')} | 📦 Stock: {product.get('stock_quantity')}\n\n"
                    elif hasattr(product, "name"):
                        # Dataclass object (backup)
                        message += f"• **{product.name}** ({product.sku})\n"
                        message += f"  💰 ${product.price} | 📦 Stock: {product.stock_quantity}\n\n"
                if len(data) > 5:
                    message += f"... and {len(data) - 5} more products."
            else:
                message = "📦 No products found in your catalog. Would you like to create some?"

        elif action == "list_customers":
            if data and len(data) > 0:
                message = f"👥 I found {len(data)} customer(s):\n\n"
                for customer in data[:5]:
                    # Debug: Check what type of object we have
                    logger.info(f"Customer object type: {type(customer)}")
                    logger.info(f"Customer object: {customer}")

                    # Handle dict objects (should be parsed JSON now)
                    if isinstance(customer, dict):
                        message += f"• **{customer.get('first_name')} {customer.get('last_name')}**\n"
                        message += f"  📧 {customer.get('email')}\n\n"
                    elif hasattr(customer, "first_name"):
                        # Dataclass object (backup)
                        message += f"• **{customer.first_name} {customer.last_name}**\n"
                        message += f"  📧 {customer.email}\n\n"
                if len(data) > 5:
                    message += f"... and {len(data) - 5} more customers."
            else:
                message = "👥 No customers found. Ready to add your first customer?"

        elif action == "list_orders":
            if data and len(data) > 0:
                message = f"📋 I found {len(data)} order(s):\n\n"
                for order in data[:5]:
                    # Debug: Check what type of object we have
                    logger.info(f"Order object type: {type(order)}")
                    logger.info(f"Order object: {order}")

                    # Handle dict objects (should be parsed JSON now)
                    if isinstance(order, dict):
                        customer_name = f"{order.get('customer', {}).get('first_name', 'Unknown')} {order.get('customer', {}).get('last_name', '')}"
                        product_name = order.get("product", {}).get(
                            "name", "Unknown Product"
                        )
                        message += f"• **Order #{order.get('id')}** - {customer_name}\n"
                        message += f"  📦 {order.get('quantity')} x {product_name}\n"
                        message += f"  💰 ${order.get('total_amount'):.2f} | Status: {order.get('status')}\n"
                        message += f"  📅 {order.get('created_at', '')[:10]}\n\n"
                    elif hasattr(order, "id"):
                        # Dataclass object (backup)
                        message += f"• **Order #{order.id}**\n"
                        message += f"  📦 {order.quantity} items | 💰 ${order.total_amount:.2f}\n\n"
                if len(data) > 5:
                    message += f"... and {len(data) - 5} more orders."
            else:
                message = "📋 No orders found yet. Ready to process your first order?"

        elif action == "get_low_stock_products":
            if data and len(data) > 0:
                message = f"⚠️ {len(data)} product(s) are running low on stock:\n\n"
                for product in data:
                    # Handle dict objects (should be parsed JSON now)
                    if isinstance(product, dict):
                        message += f"• **{product.get('name')}** - Only {product.get('stock_quantity')} left!\n"
                    elif hasattr(product, "name"):
                        # Dataclass object (backup)
                        message += f"• **{product.name}** - Only {product.stock_quantity} left!\n"
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

    async def post_process_product_list(self, result, sort_info: Dict[str, Any]):
        """Post-process product list to apply sorting and filtering"""
        try:
            logger.info(f"Post-processing with sort_info: {sort_info}")
            
            # Extract and parse the product data
            if hasattr(result, "data"):
                processed_data = result.data
                logger.info(f"Original data type: {type(processed_data)}")
                if (
                    isinstance(processed_data, list)
                    and len(processed_data) > 0
                    and isinstance(processed_data[0], dict)
                    and processed_data[0].get("type") == "text"
                ):
                    try:
                        import json

                        json_text = processed_data[0]["text"]
                        products = json.loads(json_text)
                        logger.info(f"Parsed {len(products)} products from JSON")
                    except (json.JSONDecodeError, KeyError) as e:
                        logger.warning(f"Failed to parse JSON: {e}")
                        return result  # Return original if parsing fails
                else:
                    products = processed_data
                    logger.info(f"Using data directly, type: {type(products)}")
            else:
                logger.warning("Result has no data attribute")
                return result

            # Apply sorting if requested
            sort_by = sort_info.get("sort_by")
            if sort_by:
                logger.info(f"Applying sort: {sort_by}")
                if sort_by == "price_desc" or sort_by == "price":
                    # Sort by price descending (most expensive first)
                    products.sort(key=lambda x: float(x.get("price", 0)), reverse=True)
                    logger.info(f"Sorted by price desc. First product: {products[0].get('name')} - ${products[0].get('price')}")
                elif sort_by == "price_asc":
                    # Sort by price ascending (cheapest first)
                    products.sort(key=lambda x: float(x.get("price", 0)), reverse=False)
                elif sort_by == "name":
                    # Sort by name alphabetically
                    products.sort(key=lambda x: x.get("name", "").lower())
                elif sort_by == "stock":
                    # Sort by stock quantity
                    products.sort(
                        key=lambda x: int(x.get("stock_quantity", 0)), reverse=True
                    )

            # Apply limit if requested
            limit = sort_info.get("limit")
            if limit and isinstance(limit, int):
                products = products[:limit]

            # Update the result with sorted data
            if hasattr(result, "data"):
                if (
                    isinstance(result.data, list)
                    and len(result.data) > 0
                    and isinstance(result.data[0], dict)
                    and result.data[0].get("type") == "text"
                ):
                    # Update the JSON string
                    import json

                    result.data[0]["text"] = json.dumps(products)
                else:
                    result.data = products

            return result

        except Exception as e:
            logger.warning(f"Failed to post-process product list: {e}")
            return result  # Return original result if processing fails
