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
                action_result = await self.execute_ecommerce_action(
                    intent_analysis, user_message
                )

                # For interactive actions, return the result directly without Grok processing
                action = intent_analysis.get("action")
                interactive_actions = [
                    "help_create_product",
                    "request_product_details",
                    "help_find_customer",
                    "help_choose_customer_contact",
                    "help_create_order",
                ]
                if action in interactive_actions:
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
- "how can I contact the customer?" = help_choose_customer_contact (show customer list)
- "contact customer john@example.com" = get_customer with identifier: "john@example.com", search_by: "email"
- "customer details for john@example.com" = get_customer with identifier: "john@example.com", search_by: "email"
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
- get_customer: Get customer details (needs: identifier and search_by: "id"|"email")
- list_orders: Show all orders
- create_order: Create order (needs: customer_id, items: [{product_id, quantity}], currency)
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
- For get_customer, always use "identifier" and "search_by" parameters, not "email" or "customer_id" directly
- For create_order, format parameters as: {customer_id: "id", items: [{"product_id": "id", "quantity": number}], currency: "USD"}

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

            # Check if they're asking for a specific product type (e.g., "most expensive laptop")
            search_terms = []
            common_product_types = [
                "laptop",
                "phone",
                "computer",
                "mouse",
                "keyboard",
                "monitor",
                "tablet",
                "headphone",
                "speaker",
                "drive",
                "camera",
                "watch",
                "cable",
                "charger",
                "battery",
            ]
            for product_type in common_product_types:
                if product_type in message_lower:
                    search_terms.append(product_type)

            if search_terms:
                # Use search_products with sorting
                params = {"query": " ".join(search_terms), "sort_by": "price_desc"}
                if limit:
                    params["limit"] = limit
                return {
                    "intent": f"Show {'top ' + str(limit) + ' ' if limit else ''}most expensive {' '.join(search_terms)}",
                    "action": "search_products",
                    "parameters": params,
                    "requires_action": True,
                    "confidence": 0.9,
                }
            else:
                # General expensive products
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

            # Check if they're asking for a specific product type (e.g., "cheapest laptop")
            search_terms = []
            common_product_types = [
                "laptop",
                "phone",
                "computer",
                "mouse",
                "keyboard",
                "monitor",
                "tablet",
                "headphone",
                "speaker",
                "drive",
                "camera",
                "watch",
                "cable",
                "charger",
                "battery",
            ]
            for product_type in common_product_types:
                if product_type in message_lower:
                    search_terms.append(product_type)

            if search_terms:
                # Use search_products with sorting
                params = {"query": " ".join(search_terms), "sort_by": "price_asc"}
                if limit:
                    params["limit"] = limit
                return {
                    "intent": f"Show {'top ' + str(limit) + ' ' if limit else ''}cheapest {' '.join(search_terms)}",
                    "action": "search_products",
                    "parameters": params,
                    "requires_action": True,
                    "confidence": 0.9,
                }
            else:
                # General cheapest products
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

        # Customer contact/communication patterns
        customer_contact_patterns = [
            "how can i contact",
            "contact the customer",
            "contact customer",
            "contact",  # Added standalone "contact"
            "how to reach",
            "customer contact",
            "customer info",
            "customer details",
            "reach out to customer",
            "get in touch with",
            "communicate with customer",
        ]

        if any(pattern in message_lower for pattern in customer_contact_patterns):
            # Check if a specific customer is mentioned (email or name)
            import re

            # Look for email patterns
            email_match = re.search(
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", message_lower
            )
            # Look for customer names in quotes
            name_match = re.search(r'["\']([^"\']+)["\']', message)
            # Look for customer ID patterns
            id_match = re.search(
                r"\b(?:customer|id|#)\s*:?\s*([a-zA-Z0-9_-]+)", message_lower
            )

            if email_match:
                return {
                    "intent": f"Get contact details for customer: {email_match.group()}",
                    "action": "get_customer",
                    "parameters": {
                        "identifier": email_match.group(),
                        "search_by": "email",
                    },
                    "requires_action": True,
                    "confidence": 0.9,
                }
            elif name_match:
                # This is tricky - we can't search by name directly, so suggest listing customers
                return {
                    "intent": f"Find customer contact info for: {name_match.group(1)}",
                    "action": "help_find_customer",
                    "parameters": {"search_name": name_match.group(1)},
                    "requires_action": True,
                    "confidence": 0.8,
                }
            elif id_match:
                return {
                    "intent": f"Get contact details for customer ID: {id_match.group(1)}",
                    "action": "get_customer",
                    "parameters": {"identifier": id_match.group(1), "search_by": "id"},
                    "requires_action": True,
                    "confidence": 0.9,
                }
            else:
                # General customer contact query - show list of customers
                return {
                    "intent": "Show customers to choose who to contact",
                    "action": "help_choose_customer_contact",
                    "parameters": {},
                    "requires_action": True,
                    "confidence": 0.8,
                }

        # Phone number query patterns
        phone_patterns = [
            "phone number",
            "phone numbers",
            "any phone",
            "contact number",
            "telephone",
            "call them",
            "how to call",
            "phone info",
            "phone details",
        ]

        if any(pattern in message_lower for pattern in phone_patterns):
            # If asking about phone numbers in general, show customer list with phone info
            return {
                "intent": "Show customer phone numbers",
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

        # Order creation patterns
        order_creation_patterns = [
            "create order",
            "new order",
            "place order",
            "how to create order",
            "how to place order",
            "make order",
            "add order",
            "process order",
            "how to create a new order",
            "help me create order",
            "help with order",
        ]

        if any(pattern in message_lower for pattern in order_creation_patterns):
            # Check if they provided order details (customer, product, quantity)
            import re

            # Look for patterns like "customer: john@example.com", "product: laptop", "quantity: 2"
            customer_match = re.search(
                r"customer[:\s]+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[a-zA-Z0-9_-]+)",
                message_lower,
            )
            product_match = re.search(r"product[:\s]+([a-zA-Z0-9_-]+)", message_lower)
            quantity_match = re.search(r"quantity[:\s]+(\d+)", message_lower)

            # Enhanced patterns for natural language
            # Pattern: "create order for [customer] for [quantity] [product]"
            natural_pattern = re.search(
                r"(?:create|place|make)\s+order\s+for\s+(\w+)\s+for\s+(\d+)\s+(\w+)",
                message_lower,
            )

            # Pattern: "order [quantity] [product] for [customer]"
            reverse_pattern = re.search(
                r"order\s+(\d+)\s+(\w+)\s+for\s+(\w+)", message_lower
            )

            params = {}
            if customer_match:
                params["customer_id"] = customer_match.group(1)
            if product_match:
                params["product_id"] = product_match.group(1)
            if quantity_match:
                params["quantity"] = int(quantity_match.group(1))

            # Handle natural language patterns
            if natural_pattern:
                customer_term, quantity_str, product_term = natural_pattern.groups()
                params["customer_id"] = customer_term
                params["product_id"] = product_term
                params["quantity"] = int(quantity_str)
            elif reverse_pattern:
                quantity_str, product_term, customer_term = reverse_pattern.groups()
                params["customer_id"] = customer_term
                params["product_id"] = product_term
                params["quantity"] = int(quantity_str)

            if len(params) >= 3:  # All required parameters provided
                # Check if customer_id and product_id look like actual IDs or need to be resolved
                customer_id = params["customer_id"]
                product_id = params["product_id"]

                # If they don't look like real IDs, try to map them to real ones
                if not customer_id.startswith("cust_"):
                    # Map common customer terms to actual customer ID
                    if customer_id.lower() in ["demo", "test", "default"]:
                        customer_id = "cust_000001"  # Use first customer

                if not product_id.startswith("prod_"):
                    # Map common product terms to actual product IDs
                    product_mapping = {
                        "laptop": "prod_000004",  # Laptop Pro
                        "laptops": "prod_000004",
                        "microphone": "prod_000010",
                        "microphones": "prod_000010",
                        "headset": "prod_000009",
                        "headsets": "prod_000009",
                        "iphone": "prod_000007",
                        "phone": "prod_000007",
                        "phones": "prod_000007",
                        "usb": "prod_000006",
                        "drive": "prod_000006",
                    }
                    product_id = product_mapping.get(product_id.lower(), product_id)

                # Convert to proper format for create_order method
                items = [{"product_id": product_id, "quantity": params["quantity"]}]
                order_params = {
                    "customer_id": customer_id,
                    "items": items,
                    "currency": "USD",
                }
                return {
                    "intent": f"Create order: {params['quantity']} {params['product_id']} for {params['customer_id']}",
                    "action": "create_order",
                    "parameters": order_params,
                    "requires_action": True,
                    "confidence": 0.9,
                }
            else:
                # Not enough details provided, offer help
                return {
                    "intent": "Help with creating an order",
                    "action": "help_create_order",
                    "parameters": {},
                    "requires_action": True,
                    "confidence": 0.8,
                }

        # Stock update patterns
        stock_update_patterns = [
            "update stock",
            "update inventory",
            "change stock",
            "set stock",
            "add stock",
            "increase stock",
            "decrease stock",
            "modify stock",
            "adjust stock",
        ]

        if any(pattern in message_lower for pattern in stock_update_patterns):
            import re

            # Extract product name/identifier more intelligently
            product_name = self._extract_product_name_from_stock_command(message_lower)

            # Extract quantity
            quantity_match = re.search(r"(\d+)", message)
            quantity = int(quantity_match.group(1)) if quantity_match else 1

            # Determine operation type based on keywords
            operation = "set"  # Default operation

            # Check for "by" patterns (increment/add)
            if re.search(r"\bby\s+\d+", message_lower) or any(
                keyword in message_lower
                for keyword in ["add", "increase", "increment", "plus"]
            ):
                operation = "add"
            # Check for "to" patterns (set)
            elif re.search(r"\bto\s+\d+", message_lower) or any(
                keyword in message_lower for keyword in ["set", "change to", "make"]
            ):
                operation = "set"

            # Build parameters
            params = {"quantity": quantity, "operation": operation}

            if product_name:
                params["search_term"] = product_name

            return {
                "intent": f"Update stock for {product_name or 'product'} {operation} {quantity}",
                "action": "update_stock",
                "parameters": params,
                "requires_action": True,
                "confidence": 0.9,
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

    def _smart_product_mapping(self, search_term: str) -> Optional[str]:
        """
        Smart product mapping that handles specific product names better.
        Checks for exact matches first, then partial matches.
        """
        search_term = search_term.lower().strip()

        # Exact matches first (most specific)
        exact_mappings = {
            "laptop pro": "prod_000004",
            "test laptop": "prod_000008",
            "microphone egile": "prod_000010",
            "gaming headset": "prod_000009",
            "usb drive": "prod_000006",
        }

        if search_term in exact_mappings:
            return exact_mappings[search_term]

        # Partial matches with priority order (check more specific first)
        partial_mappings = [
            # Test Laptop should be matched before general laptop
            (["test laptop", "testing laptop"], "prod_000008"),
            # Laptop Pro should be matched before general laptop
            (["laptop pro", "pro laptop"], "prod_000004"),
            # Microphone variants
            (["microphone egile", "egile microphone"], "prod_000010"),
            (["microphone", "microphones", "mic"], "prod_000010"),
            # Headset variants
            (["gaming headset", "headset gaming"], "prod_000009"),
            (["headset", "headsets"], "prod_000009"),
            # Phone variants
            (["iphone", "phone", "phones"], "prod_000007"),
            # USB variants
            (["usb drive", "drive usb"], "prod_000006"),
            (["usb", "drive"], "prod_000006"),
            # General laptop (lowest priority to avoid conflicts)
            (["laptop", "laptops"], "prod_000004"),
        ]

        for keywords, product_id in partial_mappings:
            for keyword in keywords:
                if keyword in search_term:
                    return product_id

        return None

    def _extract_product_name_from_stock_command(
        self, message_lower: str
    ) -> Optional[str]:
        """
        Extract product name from stock update commands more intelligently.
        Handles phrases like 'update stock of "Test Laptop"' or 'update Test Laptop stock'
        """
        import re

        # Pattern 1: Look for quoted product names: 'update stock of "Test Laptop"'
        quoted_match = re.search(r'["\']([^"\']+)["\']', message_lower)
        if quoted_match:
            return quoted_match.group(1).strip()

        # Pattern 2: Look for "stock of [product]" patterns
        stock_of_match = re.search(
            r"stock\s+of\s+(.+?)\s+by|\bstock\s+of\s+(.+?)\s+to|\bstock\s+of\s+(.+)",
            message_lower,
        )
        if stock_of_match:
            product = (
                stock_of_match.group(1)
                or stock_of_match.group(2)
                or stock_of_match.group(3)
            ).strip()
            return product

        # Pattern 3: Look for "[product] stock" patterns: "Test Laptop stock by 10"
        product_stock_match = re.search(
            r"(?:update\s+)?(.+?)\s+stock\s+(?:by|to)", message_lower
        )
        if product_stock_match:
            product = product_stock_match.group(1).strip()
            # Filter out common words that aren't product names
            if product not in ["update", "change", "set", "modify", "adjust"]:
                return product

        # Pattern 4: Look for "stock [product]" patterns: "update stock Test Laptop by 10"
        stock_product_match = re.search(r"stock\s+(.+?)\s+(?:by|to)", message_lower)
        if stock_product_match:
            product = stock_product_match.group(1).strip()
            return product

        # Pattern 5: Fallback - look for common product keywords
        common_products = [
            "test laptop",
            "laptop pro",
            "microphone",
            "headset",
            "iphone",
            "phone",
            "usb",
            "drive",
        ]
        for product in common_products:
            if product in message_lower:
                return product

        # Pattern 6: Extract word after "stock" if no specific pattern matched
        simple_stock_match = re.search(r"stock\s+(\w+)", message_lower)
        if simple_stock_match:
            return simple_stock_match.group(1)

        return None

    async def execute_ecommerce_action(
        self, intent_analysis: Dict[str, Any], user_message: str = ""
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
            "help_find_customer": "help_find_customer",
            "help_choose_customer_contact": "help_choose_customer_contact",
            "list_orders": "get_all_orders",
            "create_order": "create_order",
            "help_create_order": "help_create_order",
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
        elif action == "help_find_customer":
            return await self.help_find_customer(parameters)
        elif action == "help_choose_customer_contact":
            return await self.help_choose_customer_contact()
        elif action == "help_create_order":
            return await self.help_create_order()

        # Special parameter validation and mapping for create_order
        if action == "create_order" and parameters:
            # Validate and map customer_id and product_id if needed
            customer_id = parameters.get("customer_id", "")
            if customer_id and not customer_id.startswith("cust_"):
                # Map common customer terms to actual customer ID
                if customer_id.lower() in ["demo", "test", "default"]:
                    parameters["customer_id"] = "cust_000001"  # Use first customer
                    logger.info(f"Mapped customer '{customer_id}' to 'cust_000001'")

            # Check items for product_id mapping
            items = parameters.get("items", [])
            for item in items:
                product_id = item.get("product_id", "")
                if product_id and not product_id.startswith("prod_"):
                    # Map common product terms to actual product IDs
                    product_mapping = {
                        "laptop": "prod_000004",  # Laptop Pro
                        "laptops": "prod_000004",
                        "microphone": "prod_000010",
                        "microphones": "prod_000010",
                        "headset": "prod_000009",
                        "headsets": "prod_000009",
                        "iphone": "prod_000007",
                        "phone": "prod_000007",
                        "phones": "prod_000007",
                        "usb": "prod_000006",
                        "drive": "prod_000006",
                    }
                    mapped_id = product_mapping.get(product_id.lower())
                    if mapped_id:
                        item["product_id"] = mapped_id
                        logger.info(f"Mapped product '{product_id}' to '{mapped_id}'")

        # Special parameter mapping for get_product
        elif action == "get_product" and parameters:
            # The get_product method expects 'identifier' and 'search_by' parameters
            # but the chatbot might provide 'product_id' or 'sku'
            if "product_id" in parameters:
                parameters["identifier"] = parameters.pop("product_id")
                parameters["search_by"] = "id"
            elif "sku" in parameters:
                parameters["identifier"] = parameters.pop("sku")
                parameters["search_by"] = "sku"
            elif "identifier" not in parameters:
                # Default behavior if no clear identifier
                if len(parameters) == 1:
                    # Assume the single parameter is the identifier
                    key, value = next(iter(parameters.items()))
                    parameters = {"identifier": value, "search_by": "id"}

        # Special parameter mapping for update_stock
        elif action == "update_stock" and parameters:
            # The update_stock method expects 'product_id', 'quantity', 'operation'
            # but the chatbot might provide 'search_term' or other variations
            if "search_term" in parameters:
                # Map search term to product_id using smart product mapping
                search_term = parameters.pop("search_term").lower()
                mapped_id = self._smart_product_mapping(search_term)
                if mapped_id:
                    parameters["product_id"] = mapped_id
                    logger.info(
                        f"Mapped product '{search_term}' to '{mapped_id}' for stock update"
                    )
                else:
                    # If no mapping found, assume it's already a product ID
                    parameters["product_id"] = search_term

            # Handle cases where product_id is None, empty, or just a partial name
            if "product_id" in parameters:
                product_id = parameters["product_id"]
                if (
                    not product_id
                    or product_id == "None"
                    or not product_id.startswith("prod_")
                ):
                    # Try to map using smart product mapping
                    mapped_id = self._smart_product_mapping(str(product_id).lower())
                    if mapped_id:
                        parameters["product_id"] = mapped_id
                        logger.info(
                            f"Mapped product '{product_id}' to '{mapped_id}' for stock update"
                        )
                    else:
                        # Default to laptop if no clear product specified
                        parameters["product_id"] = "prod_000004"
                        logger.info(
                            f"Defaulting unclear product '{product_id}' to 'prod_000004' (Laptop Pro)"
                        )
            else:
                # If no product_id at all, default to laptop
                parameters["product_id"] = "prod_000004"
                logger.info(
                    "No product_id specified, defaulting to 'prod_000004' (Laptop Pro)"
                )

            # Determine operation based on original user message context
            # Check the original user message FIRST, then intent analysis
            user_message_lower = user_message.lower()

            # Look for increment/add keywords vs set keywords
            increment_keywords = ["by", "add", "increase", "increment", "plus"]
            set_keywords = ["to", "set", "make", "change to"]

            # Check the original user message first (most reliable)
            if any(keyword in user_message_lower for keyword in increment_keywords):
                parameters["operation"] = "add"
                logger.info(
                    "Detected increment operation (add) from original user message"
                )
            elif any(keyword in user_message_lower for keyword in set_keywords):
                parameters["operation"] = "set"
                logger.info("Detected set operation from original user message")
            # Fallback to checking intent analysis
            else:
                original_intent = intent_analysis.get("intent", "").lower()

                # Check if user wants to add/increment (e.g., "update by 20", "increase by 10")
                if any(keyword in original_intent for keyword in increment_keywords):
                    parameters["operation"] = "add"
                    logger.info("Detected increment operation (add) from user intent")
                # Check if user wants to set (e.g., "update to 20", "set to 10")
                elif any(keyword in original_intent for keyword in set_keywords):
                    parameters["operation"] = "set"
                    logger.info("Detected set operation from user intent")
                # Check parameters for operation clues
                elif "operation" not in parameters:
                    # Look for operation clues in the parameters themselves
                    if "by" in str(parameters).lower():
                        parameters["operation"] = "add"
                        logger.info(
                            "Detected increment operation (add) from parameters"
                        )
                    else:
                        parameters["operation"] = "set"  # Default operation
                        logger.info("Using default set operation")

            # Map common parameter names
            if "stock" in parameters:
                parameters["quantity"] = parameters.pop("stock")
            elif "new_stock" in parameters:
                parameters["quantity"] = parameters.pop("new_stock")

        method_name = action_mapping[action]
        method = getattr(self.ecommerce_agent, method_name)

        # Handle special cases for actions that don't support certain parameters
        if action == "list_products" and parameters:
            # get_all_products doesn't accept parameters, but we might want to sort later
            # Store sorting info for post-processing
            sort_info = parameters.copy()
            logger.info(f"Storing sort_info for list_products: {sort_info}")
            parameters = {}  # Clear parameters for the actual method call
        elif action == "search_products" and parameters:
            # search_products may have sort_by parameters we need to handle after search
            sort_info = {
                k: v for k, v in parameters.items() if k in ["sort_by", "limit"]
            }
            if sort_info:
                # Remove sort parameters from the actual method call
                parameters = {
                    k: v for k, v in parameters.items() if k not in ["sort_by", "limit"]
                }
                logger.info(f"Storing sort_info for search_products: {sort_info}")
            else:
                sort_info = None
        elif action == "update_stock" and parameters:
            # update_stock only accepts 'product_id', 'quantity', 'operation'
            # Remove any other parameters that might have been added by mistake
            allowed_params = ["product_id", "quantity", "operation"]
            filtered_params = {
                k: v for k, v in parameters.items() if k in allowed_params
            }
            if len(filtered_params) != len(parameters):
                removed_params = {
                    k: v for k, v in parameters.items() if k not in allowed_params
                }
                logger.info(
                    f"Removed unexpected parameters for update_stock: {removed_params}"
                )
                parameters = filtered_params
            sort_info = None
        else:
            sort_info = None

        # Execute the method
        if parameters:
            logger.info(f"Calling {method_name} with parameters: {parameters}")
            result = await method(**parameters)
        else:
            logger.info(f"Calling {method_name} with no parameters")
            result = await method()

        # Post-process the result if sorting was requested
        if sort_info and action in ["list_products", "search_products"]:
            logger.info(f"Post-processing {action} with sort_info: {sort_info}")
            result = await self.post_process_product_list(result, sort_info)
        else:
            logger.info(
                f"No post-processing needed. sort_info: {sort_info}, action: {action}"
            )

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
                        name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip()
                        email = customer.get("email", "")
                        phone = customer.get("phone", "")

                        message += f"• **{name}**\n"
                        message += f"  📧 {email}\n"
                        if phone:
                            message += f"  📱 {phone}\n"
                        else:
                            message += "  📱 No phone number\n"
                        message += "\n"
                    elif hasattr(customer, "first_name"):
                        # Dataclass object (backup)
                        name = f"{customer.first_name} {customer.last_name}".strip()
                        phone = getattr(customer, "phone", None)
                        message += f"• **{name}**\n"
                        message += f"  📧 {customer.email}\n"
                        if phone:
                            message += f"  📱 {phone}\n"
                        else:
                            message += "  📱 No phone number\n"
                        message += "\n"
                if len(data) > 5:
                    message += f"... and {len(data) - 5} more customers."
            else:
                message = "👥 No customers found. Ready to add your first customer?"

        elif action == "get_customer":
            if data and len(data) > 0:
                # Handle single customer details
                customer = data[0] if isinstance(data, list) else data
                logger.info(f"Customer object type: {type(customer)}")
                logger.info(f"Customer object: {customer}")

                if isinstance(customer, dict):
                    name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip()
                    email = customer.get("email", "No email")
                    phone = customer.get("phone", "No phone number")
                    customer_id = customer.get("id", "Unknown")
                    created_at = customer.get("created_at", "")

                    message = f"👤 **Customer Details**\n\n"
                    message += f"**Name:** {name}\n"
                    message += f"**Email:** {email}\n"
                    message += f"**Phone:** {phone}\n"
                    message += f"**Customer ID:** {customer_id}\n"
                    if created_at:
                        message += f"**Member since:** {created_at[:10]}\n"

                    # Add contact information
                    message += f"\n📞 **Contact Information:**\n"
                    if phone and phone != "No phone number":
                        message += f"• Call: {phone}\n"
                    if email and email != "No email":
                        message += f"• Email: {email}\n"

                elif hasattr(customer, "first_name"):
                    # Dataclass object (backup)
                    name = f"{customer.first_name} {customer.last_name}".strip()
                    message = f"👤 **Customer Details**\n\n"
                    message += f"**Name:** {name}\n"
                    message += f"**Email:** {getattr(customer, 'email', 'No email')}\n"
                    message += (
                        f"**Phone:** {getattr(customer, 'phone', 'No phone number')}\n"
                    )
                    message += (
                        f"**Customer ID:** {getattr(customer, 'id', 'Unknown')}\n"
                    )
                else:
                    message = f"👤 Customer found: {customer}"
            else:
                message = "👤 Customer not found. Please check the email address or customer ID."

        elif action == "list_orders":
            if data and len(data) > 0:
                message = f"📋 I found {len(data)} order(s):\n\n"
                for order in data[:5]:
                    # Debug: Check what type of object we have
                    logger.info(f"Order object type: {type(order)}")
                    logger.info(f"Order object: {order}")

                    # Handle dict objects (should be parsed JSON now)
                    if isinstance(order, dict):
                        # Get customer name
                        customer_id = order.get("customer_id", "Unknown")
                        customer_name = "Unknown Customer"
                        if customer_id == "cust_000001":
                            customer_name = "Demo User"

                        # Get order items and calculate total quantity
                        items = order.get("items", [])
                        total_quantity = sum(item.get("quantity", 0) for item in items)

                        # Get product names for display
                        product_names = []
                        for item in items:
                            product_id = item.get("product_id", "")
                            quantity = item.get("quantity", 0)

                            # Map product IDs to names
                            product_name = "Unknown Product"
                            if product_id == "prod_000010":
                                product_name = "microphone Egile"
                            elif product_id == "prod_000004":
                                product_name = "Laptop Pro"
                            elif product_id == "prod_000009":
                                product_name = "Gaming Headset Pro"
                            elif product_id == "prod_000007":
                                product_name = "Test iPhone"
                            elif product_id == "prod_000005":
                                product_name = "Wireless Mouse"
                            elif product_id == "prod_000006":
                                product_name = "USB Drive"

                            if quantity > 1:
                                product_names.append(f"{quantity}x {product_name}")
                            else:
                                product_names.append(product_name)

                        products_display = (
                            ", ".join(product_names) if product_names else "No items"
                        )

                        message += f"• **Order #{order.get('id')}** - {customer_name}\n"
                        message += f"  📦 {products_display}\n"
                        message += f"  💰 ${order.get('total_amount', 0):.2f} | Status: {order.get('status', 'unknown')}\n"
                        message += f"  📅 {order.get('created_at', '')[:10]}\n\n"
                    elif hasattr(order, "id"):
                        # Dataclass object (backup)
                        customer_name = "Unknown Customer"
                        if (
                            hasattr(order, "customer_id")
                            and order.customer_id == "cust_000001"
                        ):
                            customer_name = "Demo User"

                        # Count items
                        item_count = len(order.items) if hasattr(order, "items") else 0

                        message += f"• **Order #{order.id}** - {customer_name}\n"
                        message += f"  📦 {item_count} item(s) | 💰 ${order.total_amount:.2f}\n"
                        message += f"  Status: {order.status} | 📅 {order.created_at[:10] if hasattr(order, 'created_at') else 'Unknown'}\n\n"

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

        elif action == "search_products":
            if data and len(data) > 0:
                query = intent_analysis.get("parameters", {}).get("query", "")
                message = f"🔍 **Search Results for '{query}'**\n\n"
                message += f"Found {len(data)} product(s):\n\n"

                for product in data[:10]:  # Limit to 10 results
                    if isinstance(product, dict):
                        name = product.get("name", "Unnamed Product")
                        price = product.get("price", 0)
                        stock = product.get("stock_quantity", 0)
                        category = product.get("category", "Unknown")
                        description = product.get("description", "")

                        message += f"• **{name}**\n"
                        message += f"  💰 ${price:.2f}\n"
                        message += f"  📦 {stock} in stock\n"
                        message += f"  🏷️ Category: {category}\n"
                        if description:
                            # Truncate long descriptions
                            desc = (
                                description[:100] + "..."
                                if len(description) > 100
                                else description
                            )
                            message += f"  📝 {desc}\n"
                        message += "\n"
                    else:
                        message += f"• {product}\n"

                if len(data) > 10:
                    message += f"... and {len(data) - 10} more results\n"
            else:
                query = intent_analysis.get("parameters", {}).get("query", "")
                message = f"🔍 No products found matching '{query}'. Try different search terms."
        elif action == "get_product":
            if data and len(data) > 0:
                product = data[0] if isinstance(data, list) else data

                if isinstance(product, dict):
                    name = product.get("name", "Unnamed Product")
                    price = product.get("price", 0)
                    stock = product.get("stock_quantity", 0)
                    category = product.get("category", "Unknown")
                    description = product.get("description", "")
                    sku = product.get("sku", "")
                    product_id = product.get("id", "Unknown")

                    message = f"📦 **Product Details**\n\n"
                    message += f"**Name:** {name}\n"
                    message += f"**Price:** ${price:.2f}\n"
                    message += f"**Stock:** {stock} units available\n"
                    message += f"**Category:** {category}\n"
                    if sku:
                        message += f"**SKU:** {sku}\n"
                    message += f"**Product ID:** {product_id}\n"
                    if description:
                        message += f"**Description:** {description}\n"

                    # Add availability status
                    if stock > 0:
                        message += f"\n✅ **In Stock** - {stock} units available"
                    else:
                        message += f"\n❌ **Out of Stock**"
                else:
                    message = f"📦 Product details: {product}"
            else:
                identifier = intent_analysis.get("parameters", {}).get("identifier", "")
                message = f"📦 Product not found. Please check the product ID or SKU: '{identifier}'"
        elif action == "get_order":
            if data and len(data) > 0:
                order = data[0] if isinstance(data, list) else data

                if isinstance(order, dict):
                    order_id = order.get("id", "Unknown")
                    status = order.get("status", "Unknown")
                    total = order.get("total_amount", 0)
                    quantity = order.get("quantity", 0)
                    created_at = order.get("created_at", "")

                    customer = order.get("customer", {})
                    product = order.get("product", {})

                    customer_name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip()
                    product_name = product.get("name", "Unknown Product")

                    message = "📋 **Order Details**\n\n"
                    message += f"**Order ID:** {order_id}\n"
                    message += f"**Customer:** {customer_name}\n"
                    message += f"**Product:** {product_name}\n"
                    message += f"**Quantity:** {quantity}\n"
                    message += f"**Total Amount:** ${total:.2f}\n"
                    message += f"**Status:** {status}\n"
                    if created_at:
                        message += f"**Order Date:** {created_at[:10]}\n"

                    # Add status indicator
                    if status.lower() == "completed":
                        message += "\n✅ **Order Completed**"
                    elif status.lower() == "pending":
                        message += "\n🕐 **Order Pending**"
                    elif status.lower() == "cancelled":
                        message += "\n❌ **Order Cancelled**"
                else:
                    message = f"📋 Order details: {order}"
            else:
                order_id = intent_analysis.get("parameters", {}).get("order_id", "")
                message = f"📋 Order not found. Please check the order ID: '{order_id}'"
        elif action == "create_order":
            if data and len(data) > 0:
                # Parse the order creation response
                try:
                    import json

                    response_text = data[0].get("text", "")

                    # Extract JSON from response (usually has "Order created: {JSON}")
                    json_start = response_text.find("{")
                    if json_start >= 0:
                        json_part = response_text[json_start:]
                        order_data = json.loads(json_part)

                        order_id = order_data.get("id", "Unknown")
                        customer_id = order_data.get("customer_id", "Unknown")
                        total_amount = order_data.get("total_amount", 0)
                        currency = order_data.get("currency", "USD")
                        status = order_data.get("status", "pending")
                        created_at = order_data.get("created_at", "")
                        items = order_data.get("items", [])

                        message = "🎉 **Order Created Successfully!**\n\n"
                        message += f"**Order ID:** {order_id}\n"
                        message += f"**Customer:** {customer_id}\n"
                        message += f"**Status:** {status.title()}\n"
                        message += f"**Total Amount:** ${total_amount} {currency}\n"
                        if created_at:
                            # Format the timestamp nicely
                            date_part = (
                                created_at.split("T")[0]
                                if "T" in created_at
                                else created_at[:10]
                            )
                            time_part = (
                                created_at.split("T")[1][:8]
                                if "T" in created_at
                                else ""
                            )
                            message += f"**Created:** {date_part} at {time_part}\n"

                        message += "\n📦 **Order Items:**\n"
                        for item in items:
                            product_id = item.get("product_id", "Unknown")
                            quantity = item.get("quantity", 0)
                            unit_price = item.get("unit_price", 0)
                            total_price = item.get("total_price", 0)

                            message += f"• **Product:** {product_id}\n"
                            message += f"  **Quantity:** {quantity}\n"
                            message += f"  **Unit Price:** ${unit_price}\n"
                            message += f"  **Total:** ${total_price}\n\n"

                        message += (
                            "✅ Your order has been placed and is being processed!"
                        )

                    else:
                        # Fallback if JSON parsing fails
                        message = (
                            f"🎉 **Order Created Successfully!**\n\n{response_text}"
                        )

                except (json.JSONDecodeError, KeyError, IndexError) as e:
                    # Fallback for any parsing errors
                    message = f"🎉 **Order Created Successfully!**\n\nYour order has been placed and will be processed shortly."
            else:
                message = "🎉 **Order Created Successfully!**\n\nYour order has been placed and will be processed shortly."
        elif action == "update_stock":
            # Provide specific feedback for stock updates
            if data and len(data) > 0:
                try:
                    import json

                    response_text = data[0].get("text", "")

                    # Try to extract product information from the response
                    if "Stock updated for product" in response_text:
                        message = (
                            f"📦 **Stock Updated Successfully!**\n\n{response_text}"
                        )
                    else:
                        # Parse JSON response if available
                        json_start = response_text.find("{")
                        if json_start >= 0:
                            json_part = response_text[json_start:]
                            stock_data = json.loads(json_part)

                            product_id = stock_data.get("product_id", "Unknown")
                            new_quantity = stock_data.get("quantity", "Unknown")

                            # Map product ID to name for better display
                            product_name = "Unknown Product"
                            if product_id == "prod_000004":
                                product_name = "Laptop Pro"
                            elif product_id == "prod_000010":
                                product_name = "microphone Egile"
                            elif product_id == "prod_000009":
                                product_name = "Gaming Headset Pro"
                            elif product_id == "prod_000007":
                                product_name = "Test iPhone"
                            elif product_id == "prod_000005":
                                product_name = "Wireless Mouse"
                            elif product_id == "prod_000006":
                                product_name = "USB Drive"
                            elif product_id == "prod_000008":
                                product_name = "Test Laptop"

                            message = f"📦 **Stock Updated Successfully!**\n\n"
                            message += f"**Product:** {product_name} ({product_id})\n"
                            message += f"**New Stock Level:** {new_quantity} units\n\n"
                            message += "✅ Your inventory has been updated!"
                        else:
                            message = (
                                f"📦 **Stock Updated Successfully!**\n\n{response_text}"
                            )

                except (json.JSONDecodeError, KeyError, IndexError):
                    # Get parameters from intent to show what was updated
                    params = intent_analysis.get("parameters", {})
                    product_id = params.get("product_id", "Unknown")
                    quantity = params.get("quantity", "Unknown")

                    # Map product ID to name
                    product_name = "Unknown Product"
                    if product_id == "prod_000004":
                        product_name = "Laptop Pro"
                    elif product_id == "prod_000010":
                        product_name = "microphone Egile"
                    elif product_id == "prod_000009":
                        product_name = "Gaming Headset Pro"
                    elif product_id == "prod_000007":
                        product_name = "Test iPhone"
                    elif product_id == "prod_000005":
                        product_name = "Wireless Mouse"
                    elif product_id == "prod_000006":
                        product_name = "USB Drive"
                    elif product_id == "prod_000008":
                        product_name = "Test Laptop"

                    message = f"📦 **Stock Updated Successfully!**\n\n"
                    message += f"**Product:** {product_name}\n"
                    message += f"**New Stock Level:** {quantity} units\n\n"
                    message += "✅ Your inventory has been updated!"
            else:
                message = "📦 **Stock Updated Successfully!**\n\nYour inventory has been updated!"
        else:
            message = f"✅ Operation completed successfully! Action: {action}"

        return {
            "type": "chat_response",
            "message": message,
            "intent": intent_analysis,
            "action_result": action_result,
        }

    async def help_find_customer(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Help find a specific customer by name"""
        search_name = parameters.get("search_name", "")
        return {
            "type": "chat_response",
            "action": "help_find_customer",
            "success": True,
            "message": f"""🔍 I'd love to help you find contact info for "{search_name}"!

However, I can only search customers by email address or customer ID, not by name directly.

📋 **Here are your options:**

1. **Show all customers**: I can display your customer list so you can find "{search_name}"
   Just say: "show me all customers"

2. **Search by email**: If you know their email, I can get their details
   Example: "get customer john@example.com"

3. **Search by customer ID**: If you know their ID
   Example: "get customer cust_123456"

Would you like me to show your customer list to help you find "{search_name}"? 👥""",
        }

    async def help_choose_customer_contact(self) -> Dict[str, Any]:
        """Help user choose which customer to contact by showing customer list"""
        try:
            # Get all customers first
            customers_result = await self.ecommerce_agent.get_all_customers()

            if customers_result.success and customers_result.data:
                # Parse customer data
                processed_data = customers_result.data
                if (
                    isinstance(processed_data, list)
                    and len(processed_data) > 0
                    and isinstance(processed_data[0], dict)
                    and processed_data[0].get("type") == "text"
                ):
                    try:
                        import json

                        json_text = processed_data[0]["text"]
                        customers = json.loads(json_text)
                        logger.info(f"Parsed {len(customers)} customers from JSON")
                    except (json.JSONDecodeError, KeyError):
                        customers = processed_data
                else:
                    customers = processed_data

                if customers and len(customers) > 0:
                    message = """📞 **Customer Contact Directory**

Here are your customers. To get contact details for any of them, just ask:
"get customer [email]" or "contact [email]"

👥 **Your Customers:**

"""
                    for customer in customers[:10]:  # Show first 10
                        if isinstance(customer, dict):
                            name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip()
                            email = customer.get("email", "")
                            phone = customer.get("phone", "No phone")
                            message += f"• **{name}**\n"
                            message += f"  📧 {email}\n"
                            message += f"  📱 {phone}\n\n"

                    if len(customers) > 10:
                        message += f"... and {len(customers) - 10} more customers.\n\n"

                    message += """💡 **To get full contact details, try:**
• "get customer john@example.com"
• "contact customer sarah@company.com"
• "customer details for mike@business.com" """

                    return {
                        "type": "chat_response",
                        "action": "help_choose_customer_contact",
                        "success": True,
                        "message": message,
                    }
                else:
                    return {
                        "type": "chat_response",
                        "action": "help_choose_customer_contact",
                        "success": True,
                        "message": "👥 You don't have any customers yet. Would you like to add your first customer?",
                    }
            else:
                return {
                    "type": "error",
                    "message": "❌ Unable to retrieve customer list. Please try again.",
                }

        except Exception as e:
            return {
                "type": "error",
                "message": f"❌ Error retrieving customers: {str(e)}",
            }

    async def help_create_order(self) -> Dict[str, Any]:
        """Provide guidance on creating an order"""
        try:
            # Get customers and products to help user understand what's available
            customers_result = await self.ecommerce_agent.get_all_customers()
            products_result = await self.ecommerce_agent.get_all_products()

            message = """📋 **How to Create a New Order**

To create an order, I need three pieces of information:
1. **Customer ID** (who is placing the order)
2. **Product ID** (what they want to buy)  
3. **Quantity** (how many items)

"""

            # Show available customers
            if customers_result.success and customers_result.data:
                customers = customers_result.data
                if (
                    isinstance(customers, list)
                    and len(customers) > 0
                    and isinstance(customers[0], dict)
                    and customers[0].get("type") == "text"
                ):
                    import json

                    customers = json.loads(customers[0]["text"])

                if customers and len(customers) > 0:
                    message += "👥 **Available Customers:**\n"
                    for customer in customers[:5]:  # Show first 5
                        if isinstance(customer, dict):
                            name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip()
                            email = customer.get("email", "")
                            customer_id = customer.get("id", "")
                            message += f"• **{name}** (ID: {customer_id}) - {email}\n"
                    if len(customers) > 5:
                        message += f"... and {len(customers) - 5} more customers\n"
                    message += "\n"

            # Show available products
            if products_result.success and products_result.data:
                products = products_result.data
                if (
                    isinstance(products, list)
                    and len(products) > 0
                    and isinstance(products[0], dict)
                    and products[0].get("type") == "text"
                ):
                    import json

                    products = json.loads(products[0]["text"])

                if products and len(products) > 0:
                    message += "📦 **Available Products:**\n"
                    for product in products[:5]:  # Show first 5
                        if isinstance(product, dict):
                            name = product.get("name", "Unnamed Product")
                            product_id = product.get("id", "")
                            price = product.get("price", 0)
                            stock = product.get("stock_quantity", 0)
                            message += f"• **{name}** (ID: {product_id}) - ${price:.2f} ({stock} in stock)\n"
                    if len(products) > 5:
                        message += f"... and {len(products) - 5} more products\n"
                    message += "\n"

            message += """💡 **Example Order Creation:**
"Create order for customer 1, product 2, quantity 3"

🔧 **Alternative Commands:**
• "place order customer: john@example.com product: laptop quantity: 2"
• "new order for customer 5 with 1 of product 10"

📝 **Need to check IDs?**
• "show me customers" - to see all customer IDs
• "show me products" - to see all product IDs"""

            return {
                "type": "chat_response",
                "action": "help_create_order",
                "success": True,
                "message": message,
            }

        except Exception as e:
            return {
                "type": "error",
                "message": f"❌ Error providing order creation help: {str(e)}",
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
                    logger.info(
                        f"Sorted by price desc. First product: {products[0].get('name')} - ${products[0].get('price')}"
                    )
                elif sort_by == "price_asc":
                    # Sort by price ascending (cheapest first)
                    products.sort(key=lambda x: float(x.get("price", 0)), reverse=False)
                    logger.info(
                        f"Sorted by price asc. First product: {products[0].get('name')} - ${products[0].get('price')}"
                    )
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
