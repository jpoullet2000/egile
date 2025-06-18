#!/usr/bin/env python3
"""
Smart E-commerce Agent with Advanced Planning

A more intelligent and modular agent that can:
1. Break down complex requests into actionable plans
2. Execute multi-step operations autonomously
3. Learn from patterns and provide intelligent suggestions
4. Handle contextual conversations with memory
5. Integrate with enhanced MCP server capabilities
"""

import json
import logging
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from egile.agent import EcommerceAgent

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("smart-agent")


def robust_json_parse(data: Any, context: str = "data") -> Any:
    """
    Robustly parse JSON data that may come in various formats from the MCP server.

    Args:
        data: The data to parse (could be string, dict, object with attributes, etc.)
        context: Context for error logging

    Returns:
        Parsed data structure or None if parsing fails
    """
    try:
        # If already a dict or list, return as-is
        if isinstance(data, (dict, list)):
            return data

        # If it's an object with a 'text' attribute
        if hasattr(data, "text"):
            text_content = data.text
        # If it's a dict with 'text' key
        elif isinstance(data, dict) and "text" in data:
            text_content = data["text"]
        # Otherwise convert to string
        else:
            text_content = str(data)

        # If the text content is already a dict or list, return it
        if isinstance(text_content, (dict, list)):
            return text_content

        # Try to parse as JSON
        if isinstance(text_content, str):
            # Clean up common JSON issues
            text_content = text_content.strip()

            # Handle empty string
            if not text_content:
                logger.warning(f"Empty {context} received")
                if (
                    "search" in context
                    or "products" in context
                    or "customers" in context
                    or "orders" in context
                ):
                    return []
                return None

            # Remove any leading/trailing quotes that might wrap the JSON
            if text_content.startswith('"') and text_content.endswith('"'):
                text_content = text_content[1:-1]
                # Unescape quotes
                text_content = text_content.replace('\\"', '"')

            # Try direct parsing
            try:
                return json.loads(text_content)
            except json.JSONDecodeError as e:
                logger.warning(f"JSON decode error for {context}: {e}")

                # Try to extract JSON from response if it's wrapped in other text
                json_match = re.search(r"(\[.*\]|\{.*\})", text_content, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group(1))
                    except json.JSONDecodeError:
                        pass

                # If it looks like a simple string that should be JSON, try to fix quotes
                if text_content.startswith("{") or text_content.startswith("["):
                    # Replace single quotes with double quotes (common issue)
                    fixed_content = text_content.replace("'", '"')
                    try:
                        return json.loads(fixed_content)
                    except json.JSONDecodeError:
                        # Try more aggressive quote fixing for unquoted keys
                        # Fix unquoted keys like {name: 'value'} -> {"name": "value"}
                        import re as regex_module

                        fixed_content = regex_module.sub(
                            r"(\w+):", r'"\1":', text_content
                        )
                        fixed_content = fixed_content.replace("'", '"')
                        try:
                            return json.loads(fixed_content)
                        except json.JSONDecodeError:
                            pass

                logger.warning(
                    f"Could not parse {context} as JSON: {text_content[:100]}..."
                )
                # Try to return empty list for search results that should be lists
                if (
                    "search" in context
                    or "products" in context
                    or "customers" in context
                    or "orders" in context
                ):
                    return []
                return None

        logger.warning(f"Unexpected data type for {context}: {type(text_content)}")
        return None

    except Exception as e:
        logger.error(f"Error parsing {context}: {e}")
        return None


def extract_text_from_result(result_data: Any) -> str:
    """
    Extract text content from various result data formats.

    Args:
        result_data: The result data from MCP server

    Returns:
        Text content as string
    """
    try:
        if hasattr(result_data, "text"):
            return result_data.text
        elif isinstance(result_data, dict) and "text" in result_data:
            return result_data["text"]
        else:
            return str(result_data)
    except Exception as e:
        logger.error(f"Error extracting text from result: {e}")
        return ""


@dataclass
class TaskStep:
    """Represents a single step in a task execution plan."""

    id: str
    action: str
    description: str
    parameters: Dict[str, Any]
    dependencies: List[str] = None
    status: str = "pending"  # pending, running, completed, failed
    result: Any = None
    error_message: str = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class ExecutionPlan:
    """Represents a complete execution plan with steps."""

    id: str
    title: str
    description: str
    steps: List[TaskStep]
    context: Dict[str, Any] = None
    status: str = "pending"
    created_at: str = None

    def __post_init__(self):
        if self.context is None:
            self.context = {}
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


class SmartAgent:
    """
    Smart e-commerce agent with planning and execution capabilities.

    This agent can understand natural language requests, create execution plans,
    and carry out complex multi-step operations autonomously.
    """

    def __init__(self):
        self.ecommerce_agent: Optional[EcommerceAgent] = None
        self.conversation_history: List[Dict[str, str]] = []
        self.active_plan: Optional[ExecutionPlan] = None
        self.user_preferences: Dict[str, Any] = {}
        self.plan_counter = 0

    async def start(self):
        """Initialize the agent and start the MCP server."""
        try:
            self.ecommerce_agent = EcommerceAgent()
            await self.ecommerce_agent.start_server()
            logger.info("Smart Agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to start Smart Agent: {e}")
            raise

    async def stop(self):
        """Stop the agent and MCP server."""
        if self.ecommerce_agent:
            await self.ecommerce_agent.stop_server()
            logger.info("Smart Agent stopped")

    async def process_request(self, user_input: str) -> Dict[str, Any]:
        """
        Process a user request and return appropriate response.

        Args:
            user_input: Natural language request from user

        Returns:
            Dict containing response, actions taken, and any follow-up questions
        """
        try:
            # Add to conversation history
            self.conversation_history.append(
                {
                    "role": "user",
                    "content": user_input,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            # Analyze the request
            intent = await self._analyze_intent(user_input)

            # Handle different types of requests
            if intent["type"] == "simple_query":
                response = await self._handle_simple_query(intent)
            elif intent["type"] == "complex_operation":
                response = await self._handle_complex_operation(intent)
            elif intent["type"] == "plan_continuation":
                response = await self._handle_plan_continuation(user_input)
            elif intent["type"] == "help_request":
                response = self._provide_help(intent)
            else:
                response = self._handle_unknown_request(user_input)

            # Add assistant response to history
            self.conversation_history.append(
                {
                    "role": "assistant",
                    "content": response.get("message", ""),
                    "timestamp": datetime.now().isoformat(),
                }
            )

            return response

        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return {
                "success": False,
                "message": f"I encountered an error: {str(e)}",
                "type": "error",
            }

    async def _analyze_intent(self, user_input: str) -> Dict[str, Any]:
        """Analyze user input to determine intent and extract parameters."""
        text = user_input.lower().strip()

        # Pattern matching for different request types
        patterns = {
            "complex_operations": [
                r"(create|setup|build).*(demo|sample).*(store|shop)",
                r"(generate|create).*(report|analytics|analysis)",
                r"(bulk|mass).*(create|add|import)",
                r"(setup|initialize).*(database|data)",
                r"(process|handle).*(order|customer).*workflow",
                r"(inventory|stock).*(management|optimization|restock)",
            ],
            "simple_queries": [
                r"^(show|list|display|get|find|search)",
                r"^(create|add|new).*(product|customer|order).*",
                r"^(update|modify|change).*(price|stock|status)",
                r"^(delete|remove).*(product|customer|order)",
                r"(what|which).*(product|item).*low.*stock",
                r"(what|which).*(product|item).*(out of|low|stock)",
                r"(show|find|list).*(low|stock|inventory)",
                r"(stock|inventory).*(level|status|low|alert)",
                # Enhanced customer creation patterns
                r"(create|add|new|register).*(customer|client|user)",
                r"(add|create).*customer.*(name|email)",
                r"(register|signup|sign up).*(customer|user)",
                r"(customer|client).*(name|email|phone|address)",
                r"[A-Za-z]+\s+[A-Za-z]+.*@.*\.(com|org|net)",  # Name + email pattern
                r"(john|jane|bob|alice|mike|sarah|david|mary).*@.*\.(com|org|net)",  # Common names + email
            ],
            "plan_continuation": [
                r"^(yes|y|ok|proceed|continue|next)$",
                r"^(no|n|stop|cancel|abort)$",
                r"^(modify|change|update).*(plan|step)",
            ],
            "help_requests": [
                r"(help|what can|how do|explain)",
                r"(capabilities|features|options)",
                r"(examples|demo|tutorial)",
            ],
        }

        # Check for active plan continuation
        if self.active_plan and any(
            re.search(p, text) for p in patterns["plan_continuation"]
        ):
            return {"type": "plan_continuation", "text": text}

        # Check for complex operations
        for pattern in patterns["complex_operations"]:
            if re.search(pattern, text):
                return self._extract_complex_operation_details(user_input, text)

        # Check for simple queries
        for pattern in patterns["simple_queries"]:
            if re.search(pattern, text):
                simple_intent = self._extract_simple_query_details(user_input, text)
                if simple_intent is not None:
                    return simple_intent
                # If extract_simple_query_details returns None, continue to LLM classification

        # Check for help requests
        for pattern in patterns["help_requests"]:
            if re.search(pattern, text):
                return {"type": "help_request", "text": text, "original": user_input}

        # If no clear pattern match or ambiguous case, try LLM-based intent classification
        llm_intent = await self._classify_intent_with_llm(user_input)
        if llm_intent and llm_intent.get("type") != "unknown":
            return llm_intent

        # Default to unknown
        return {"type": "unknown", "text": text, "original": user_input}

    def _extract_complex_operation_details(
        self, original: str, text: str
    ) -> Dict[str, Any]:
        """Extract details for complex operations."""
        if "demo" in text and "store" in text:
            # Extract numbers if present
            numbers = re.findall(r"\d+", original)
            return {
                "type": "complex_operation",
                "operation": "setup_demo_store",
                "parameters": {
                    "products": int(numbers[0]) if numbers else 20,
                    "customers": int(numbers[1]) if len(numbers) > 1 else 10,
                    "orders": int(numbers[2]) if len(numbers) > 2 else 5,
                },
                "original": original,
            }
        elif "report" in text or "analytics" in text:
            return {
                "type": "complex_operation",
                "operation": "generate_analytics",
                "parameters": {},
                "original": original,
            }
        elif "bulk" in text or "mass" in text:
            numbers = re.findall(r"\d+", original)
            return {
                "type": "complex_operation",
                "operation": "bulk_create_products",
                "parameters": {"count": int(numbers[0]) if numbers else 10},
                "original": original,
            }
        elif "inventory" in text or "stock" in text:
            return {
                "type": "complex_operation",
                "operation": "inventory_management",
                "parameters": {},
                "original": original,
            }
        else:
            return {
                "type": "complex_operation",
                "operation": "general_complex",
                "parameters": {},
                "original": original,
            }

    def _extract_simple_query_details(self, original: str, text: str) -> Dict[str, Any]:
        """Extract details for simple queries."""

        # Check for low stock queries first
        if ("low" in text and "stock" in text) or ("stock" in text and "level" in text):
            return {
                "type": "simple_query",
                "action": "list_low_stock",
                "original": original,
            }

        # Skip the broad customer patterns here - let the create/add logic handle it more precisely

        if text.startswith("show") or text.startswith("list"):
            if "product" in text:
                return {
                    "type": "simple_query",
                    "action": "list_products",
                    "original": original,
                }
            elif "customer" in text:
                return {
                    "type": "simple_query",
                    "action": "list_customers",
                    "original": original,
                }
            elif "order" in text:
                return {
                    "type": "simple_query",
                    "action": "list_orders",
                    "original": original,
                }
        elif text.startswith("create") or text.startswith("add"):
            # Check for order creation first (higher priority)
            if "order" in text:
                return {
                    "type": "simple_query",
                    "action": "create_order",
                    "original": original,
                }
            elif "product" in text:
                return {
                    "type": "simple_query",
                    "action": "create_product",
                    "original": original,
                }
            elif ("customer" in text or "client" in text) and "order" not in text:
                # Only route to customer creation if it's clearly about customer creation
                # and NOT about creating an order
                import re

                explicit_customer_patterns = [
                    r"(create|add|register|signup|sign up).*(customer|client|user)(?!\s*(?:order|for))",
                    r"^customer\s+[A-Z][a-z]+\s+[A-Z][a-z]+",  # "customer John Doe"
                    r"(new|register)\s+(customer|client)",
                ]

                if any(
                    re.search(pattern, text, re.IGNORECASE)
                    for pattern in explicit_customer_patterns
                ):
                    return {
                        "type": "simple_query",
                        "action": "create_customer",
                        "original": original,
                    }
                else:
                    # Not clearly customer creation - use LLM
                    logger.info(
                        f"Customer-related but ambiguous request, deferring to LLM: {original}"
                    )
                    return None
            else:
                # Ambiguous case - use LLM to resolve
                logger.info(
                    f"Ambiguous create/add request, deferring to LLM: {original}"
                )
                # Return None to trigger LLM classification
                return None
        elif text.startswith("search") or text.startswith("find"):
            query = original.split(maxsplit=1)[1] if len(original.split()) > 1 else ""
            return {
                "type": "simple_query",
                "action": "search_products",
                "parameters": {"query": query},
                "original": original,
            }

        return {"type": "simple_query", "action": "unknown", "original": original}

    async def _handle_simple_query(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Handle simple, single-step queries."""
        action = intent.get("action", "unknown")

        try:
            if action == "list_products":
                result = await self.ecommerce_agent.get_all_products()
                if result.success:
                    # Debug: Log the actual result structure
                    logger.info(f"Result data structure: {result.data}")

                    try:
                        if result.data and len(result.data) > 0:
                            # Check if result.data is already a list of products
                            if isinstance(result.data, list) and isinstance(
                                result.data[0], dict
                            ):
                                # Data is already parsed
                                products = result.data
                            else:
                                # Use robust JSON parsing
                                products = robust_json_parse(result.data[0], "products")
                                if products is None:
                                    return {
                                        "success": False,
                                        "message": "Error parsing product data from server.",
                                    }

                            # Format the products nicely
                            formatted_products = self._format_products(products[:10])

                            return {
                                "success": True,
                                "message": f"Found {len(products)} products in the store. Here are the first 10:\n\n{formatted_products}",
                                "data": products[:10],  # Show first 10
                                "type": "product_list",
                            }
                        else:
                            return {
                                "success": False,
                                "message": "No product data received from server.",
                            }
                    except Exception as e:
                        logger.error(f"Error processing product data: {e}")
                        return {
                            "success": False,
                            "message": f"Error processing product data: {str(e)}",
                        }
                else:
                    return {
                        "success": False,
                        "message": f"Failed to get products: {result.error}",
                    }

            elif action == "list_customers":
                result = await self.ecommerce_agent.get_all_customers()
                if result.success:
                    import json

                    try:
                        if result.data and len(result.data) > 0:
                            # Check if result.data is already a list of customers
                            if isinstance(result.data, list) and isinstance(
                                result.data[0], dict
                            ):
                                # Data is already parsed
                                customers = result.data
                            else:
                                # Use robust JSON parsing
                                customers = robust_json_parse(
                                    result.data[0], "customers"
                                )
                                if customers is None:
                                    return {
                                        "success": False,
                                        "message": "Error parsing customer data from server.",
                                    }

                            # Format the customers nicely
                            formatted_customers = self._format_customers(customers[:10])

                            return {
                                "success": True,
                                "message": f"Found {len(customers)} customers. Here are the first 10:\n\n{formatted_customers}",
                                "data": customers[:10],
                                "type": "customer_list",
                            }
                        else:
                            return {
                                "success": False,
                                "message": "No customer data received from server.",
                            }
                    except (
                        json.JSONDecodeError,
                        KeyError,
                        AttributeError,
                        IndexError,
                    ) as e:
                        logger.error(f"Error parsing customer data: {e}")
                        return {
                            "success": False,
                            "message": f"Error parsing customer data: {str(e)}",
                        }
                else:
                    return {
                        "success": False,
                        "message": f"Failed to get customers: {result.error}",
                    }

            elif action == "list_orders":
                result = await self.ecommerce_agent.get_all_orders()
                if result.success:
                    import json

                    try:
                        if result.data and len(result.data) > 0:
                            # Check if result.data is already a list of orders
                            if isinstance(result.data, list) and isinstance(
                                result.data[0], dict
                            ):
                                # Data is already parsed
                                orders = result.data
                            else:
                                # Use robust JSON parsing
                                orders = robust_json_parse(result.data[0], "orders")
                                if orders is None:
                                    return {
                                        "success": False,
                                        "message": "Error parsing order data from server.",
                                    }

                            # Enhance orders with customer information
                            enhanced_orders = (
                                await self._enhance_orders_with_customer_info(
                                    orders[:10]
                                )
                            )

                            # Format the orders nicely
                            formatted_orders = self._format_orders(enhanced_orders)

                            return {
                                "success": True,
                                "message": f"Found {len(orders)} orders. Here are the first 10:\n\n{formatted_orders}",
                                "data": enhanced_orders,
                                "type": "order_list",
                            }
                        else:
                            return {
                                "success": False,
                                "message": "No order data received from server.",
                            }
                    except (
                        json.JSONDecodeError,
                        KeyError,
                        AttributeError,
                        IndexError,
                    ) as e:
                        logger.error(f"Error parsing order data: {e}")
                        return {
                            "success": False,
                            "message": f"Error parsing order data: {str(e)}",
                        }
                else:
                    return {
                        "success": False,
                        "message": f"Failed to get orders: {result.error}",
                    }

            elif action == "search_products":
                query = intent.get("parameters", {}).get("query", "")
                if not query:
                    return {
                        "success": False,
                        "message": "Please specify what products you want to search for.",
                        "type": "needs_clarification",
                    }

                result = await self.ecommerce_agent.search_products(query)
                if result.success:
                    import json

                    try:
                        if result.data and len(result.data) > 0:
                            # Check if result.data is already a list of products
                            if isinstance(result.data, list) and isinstance(
                                result.data[0], dict
                            ):
                                # Data is already parsed
                                products = result.data
                            else:
                                # Use robust JSON parsing
                                products = robust_json_parse(
                                    result.data[0], "search_products"
                                )
                                if products is None:
                                    return {
                                        "success": False,
                                        "message": "Error parsing product search results from server.",
                                    }

                            # Format the search results
                            if products:
                                formatted_products = self._format_products(
                                    products[:10]
                                )
                                return {
                                    "success": True,
                                    "message": f"Found {len(products)} products matching '{query}':\n\n{formatted_products}",
                                    "data": products[:10],
                                    "type": "search_results",
                                }
                            else:
                                return {
                                    "success": True,
                                    "message": f"No products found matching '{query}'.",
                                    "data": [],
                                    "type": "search_results",
                                }
                        else:
                            return {
                                "success": True,
                                "message": f"No products found matching '{query}'.",
                                "data": [],
                                "type": "search_results",
                            }
                    except (
                        json.JSONDecodeError,
                        KeyError,
                        AttributeError,
                        IndexError,
                    ) as e:
                        logger.error(f"Error parsing search results: {e}")
                        return {
                            "success": False,
                            "message": f"Error processing search results: {str(e)}",
                            "type": "error",
                        }
                else:
                    return {
                        "success": False,
                        "message": f"Search failed: {result.error}",
                    }

            elif action == "list_low_stock":
                threshold = intent.get("parameters", {}).get("threshold", 10)
                result = await self.ecommerce_agent.get_low_stock_products(threshold)
                if result.success:
                    import json

                    try:
                        if result.data and len(result.data) > 0:
                            # Check if result.data is already a list of products
                            if isinstance(result.data, list) and isinstance(
                                result.data[0], dict
                            ):
                                # Data is already parsed
                                products = result.data
                            else:
                                # Use robust JSON parsing
                                products = robust_json_parse(
                                    result.data[0], "low_stock_products"
                                )
                                if products is None:
                                    return {
                                        "success": False,
                                        "message": "Error parsing low stock product data from server.",
                                    }

                            if products:
                                # Format the low stock products nicely
                                formatted_products = self._format_products(products)

                                return {
                                    "success": True,
                                    "message": f"Found {len(products)} products with low stock (below {threshold} units):\n\n{formatted_products}",
                                    "data": products,
                                    "type": "low_stock_list",
                                }
                            else:
                                return {
                                    "success": True,
                                    "message": f"Great news! No products are currently low on stock (below {threshold} units).",
                                    "data": [],
                                    "type": "low_stock_list",
                                }
                        else:
                            return {
                                "success": True,
                                "message": f"Great news! No products are currently low on stock (below {threshold} units).",
                                "data": [],
                                "type": "low_stock_list",
                            }
                    except (
                        json.JSONDecodeError,
                        KeyError,
                        AttributeError,
                        IndexError,
                    ) as e:
                        logger.error(f"Error parsing low stock data: {e}")
                        return {
                            "success": False,
                            "message": f"Error parsing low stock data: {str(e)}",
                        }
                else:
                    return {
                        "success": False,
                        "message": f"Failed to get low stock products: {result.error}",
                    }

            elif action == "create_product":
                # Check if we have the required parameters
                params = intent.get("parameters", {})

                # Add the original text for natural language parsing
                params["original_text"] = intent.get("original", "")

                # Try to parse product details from natural language
                parsed_info = await self._parse_product_from_text(
                    params["original_text"]
                )

                # Check if we got multiple products (list) or single product (dict)
                if isinstance(parsed_info, list):
                    # Handle multiple products
                    return await self._handle_multiple_products(parsed_info)
                else:
                    # Handle single product
                    return await self._handle_single_product(parsed_info, params)

            elif action == "create_customer":
                # Check if we have the required parameters
                params = intent.get("parameters", {})

                # Add the original text for natural language parsing
                params["original_text"] = intent.get("original", "")

                # Try to parse from natural language first
                parsed_info = self._parse_customer_from_text(params["original_text"])

                # Merge parsed info with any explicitly provided parameters
                for key, value in parsed_info.items():
                    if value and not params.get(key):
                        params[key] = value

                required_fields = ["email", "first_name", "last_name"]
                missing_fields = [
                    field for field in required_fields if not params.get(field)
                ]

                if missing_fields:
                    return {
                        "success": True,
                        "message": "To create a customer, I need: email, first name, and last name. "
                        + f"From your message, I found: {self._format_parsed_info(parsed_info)}. "
                        + f"Still missing: {', '.join(missing_fields)}. "
                        + "Please provide the missing information.",
                        "type": "needs_input",
                        "required_fields": missing_fields,
                        "optional_fields": ["phone", "address"],
                        "parsed_info": parsed_info,
                    }
                else:
                    # We have all required fields, create the customer
                    try:
                        result = await self.ecommerce_agent.create_customer(
                            email=params["email"],
                            first_name=params["first_name"],
                            last_name=params["last_name"],
                            phone=params.get("phone"),
                            address=params.get("address"),
                        )

                        if result.success:
                            # Parse the response data if it's JSON
                            try:
                                import json

                                # Handle different response structures
                                response_data = result.data
                                if (
                                    isinstance(response_data, list)
                                    and len(response_data) > 0
                                ):
                                    # Use robust JSON parsing
                                    customer_data = robust_json_parse(
                                        response_data[0], "create_customer"
                                    )
                                    if customer_data is None:
                                        customer_data = {"id": "unknown"}
                                else:
                                    customer_data = {"id": "unknown"}

                                customer_name = (
                                    f"{params['first_name']} {params['last_name']}"
                                )
                                customer_id = customer_data.get("id", "unknown")

                                return {
                                    "success": True,
                                    "message": f"Successfully created customer: {customer_name} (ID: {customer_id}, Email: {params['email']})",
                                    "type": "customer_created",
                                    "data": customer_data,
                                }
                            except Exception as parse_error:
                                logger.error(
                                    f"Error parsing customer creation response: {parse_error}"
                                )
                                return {
                                    "success": True,
                                    "message": f"Customer {params['first_name']} {params['last_name']} was created successfully.",
                                    "type": "customer_created",
                                }
                        else:
                            return {
                                "success": False,
                                "message": f"Failed to create customer: {result.error}",
                                "type": "creation_failed",
                            }
                    except Exception as e:
                        logger.error(f"Error creating customer: {e}")
                        return {
                            "success": False,
                            "message": f"Error creating customer: {str(e)}",
                            "type": "error",
                        }

            elif action == "create_order":
                # Parse order information from the original text
                original_text = intent.get("original", "")
                order_info = await self._parse_order_from_text(original_text)

                # Check if we have the required information
                if not order_info.get("customer_name") and not order_info.get(
                    "customer_email"
                ):
                    return {
                        "success": True,
                        "message": "To create an order, I need a customer name or email, and product information. "
                        + f"From your message: '{original_text}'. "
                        + "Please provide the customer email and specify which products and quantities you want to order.",
                        "type": "needs_input",
                        "required_fields": ["customer_email", "products"],
                    }

                if not order_info.get("products"):
                    return {
                        "success": True,
                        "message": "I found the customer information, but I need to know which products to order. "
                        + "Please specify the product name(s) and quantity(ies).",
                        "type": "needs_input",
                        "required_fields": ["products"],
                        "customer_info": order_info,
                    }

                # Create the order
                return await self._create_order_with_info(order_info)

            else:
                return {
                    "success": False,
                    "message": f"I don't know how to handle the action '{action}' yet.",
                    "type": "unknown_action",
                }

        except Exception as e:
            logger.error(f"Simple query handling failed: {e}")
            return {"success": False, "message": f"Error executing query: {str(e)}"}

    async def _handle_complex_operation(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Handle complex operations that require planning."""
        operation = intent.get("operation", "unknown")
        parameters = intent.get("parameters", {})

        # Create execution plan
        plan = self._create_execution_plan(operation, parameters)
        if not plan:
            return {
                "success": False,
                "message": f"I couldn't create a plan for '{operation}'. Could you be more specific?",
                "type": "planning_failed",
            }

        # Set as active plan
        self.active_plan = plan

        # Present plan to user
        plan_description = self._format_plan_for_user(plan)

        return {
            "success": True,
            "message": f"I've created a plan for your request:\n\n{plan_description}\n\nShould I proceed with this plan? (yes/no)",
            "type": "plan_created",
            "plan": {"id": plan.id, "title": plan.title, "steps": len(plan.steps)},
            "awaiting_confirmation": True,
        }

    def _create_execution_plan(
        self, operation: str, parameters: Dict[str, Any]
    ) -> Optional[ExecutionPlan]:
        """Create an execution plan for the given operation."""
        self.plan_counter += 1
        plan_id = f"plan_{self.plan_counter:03d}"

        if operation == "setup_demo_store":
            return self._create_demo_store_plan(plan_id, parameters)
        elif operation == "generate_analytics":
            return self._create_analytics_plan(plan_id)
        elif operation == "bulk_create_products":
            return self._create_bulk_products_plan(plan_id, parameters)
        elif operation == "inventory_management":
            return self._create_inventory_plan(plan_id)

        return None

    def _create_demo_store_plan(
        self, plan_id: str, params: Dict[str, Any]
    ) -> ExecutionPlan:
        """Create plan for setting up a demo store."""
        num_products = params.get("products", 20)
        num_customers = params.get("customers", 10)
        num_orders = params.get("orders", 5)

        steps = [
            TaskStep(
                id="check_existing",
                action="check_existing_data",
                description="Check what data already exists in the store",
                parameters={},
            ),
            TaskStep(
                id="create_products",
                action="create_sample_products",
                description=f"Create {num_products} sample products across different categories",
                parameters={"count": num_products},
                dependencies=["check_existing"],
            ),
            TaskStep(
                id="create_customers",
                action="create_sample_customers",
                description=f"Create {num_customers} sample customers",
                parameters={"count": num_customers},
                dependencies=["create_products"],
            ),
            TaskStep(
                id="create_orders",
                action="create_sample_orders",
                description=f"Create {num_orders} sample orders",
                parameters={"count": num_orders},
                dependencies=["create_customers"],
            ),
            TaskStep(
                id="generate_summary",
                action="generate_store_summary",
                description="Generate a summary of the created demo store",
                parameters={},
                dependencies=["create_orders"],
            ),
        ]

        return ExecutionPlan(
            id=plan_id,
            title=f"Setup Demo Store ({num_products}p, {num_customers}c, {num_orders}o)",
            description=f"Create a complete demo store with {num_products} products, {num_customers} customers, and {num_orders} orders",
            steps=steps,
        )

    def _create_analytics_plan(self, plan_id: str) -> ExecutionPlan:
        """Create plan for generating analytics."""
        steps = [
            TaskStep(
                id="collect_data",
                action="collect_all_data",
                description="Collect all products, customers, and orders data",
                parameters={},
            ),
            TaskStep(
                id="analyze_products",
                action="analyze_product_data",
                description="Analyze product performance and inventory",
                parameters={},
                dependencies=["collect_data"],
            ),
            TaskStep(
                id="analyze_customers",
                action="analyze_customer_data",
                description="Analyze customer demographics and behavior",
                parameters={},
                dependencies=["collect_data"],
            ),
            TaskStep(
                id="analyze_sales",
                action="analyze_sales_data",
                description="Analyze sales patterns and revenue",
                parameters={},
                dependencies=["collect_data"],
            ),
            TaskStep(
                id="generate_report",
                action="compile_analytics_report",
                description="Compile comprehensive analytics report",
                parameters={},
                dependencies=["analyze_products", "analyze_customers", "analyze_sales"],
            ),
        ]

        return ExecutionPlan(
            id=plan_id,
            title="Generate Analytics Report",
            description="Comprehensive analysis of store performance and business insights",
            steps=steps,
        )

    def _create_bulk_products_plan(
        self, plan_id: str, params: Dict[str, Any]
    ) -> ExecutionPlan:
        """Create plan for bulk product creation."""
        count = params.get("count", 10)

        steps = [
            TaskStep(
                id="generate_product_data",
                action="generate_product_templates",
                description=f"Generate {count} diverse product templates",
                parameters={"count": count},
            ),
            TaskStep(
                id="validate_data",
                action="validate_product_data",
                description="Validate product data and check for duplicates",
                parameters={},
                dependencies=["generate_product_data"],
            ),
            TaskStep(
                id="create_products",
                action="batch_create_products",
                description="Create all products in the database",
                parameters={},
                dependencies=["validate_data"],
            ),
            TaskStep(
                id="verify_creation",
                action="verify_products_created",
                description="Verify all products were created successfully",
                parameters={},
                dependencies=["create_products"],
            ),
        ]

        return ExecutionPlan(
            id=plan_id,
            title=f"Bulk Create {count} Products",
            description=f"Create {count} products with diverse categories and realistic data",
            steps=steps,
        )

    def _create_inventory_plan(self, plan_id: str) -> ExecutionPlan:
        """Create plan for inventory management."""
        steps = [
            TaskStep(
                id="analyze_stock",
                action="analyze_current_stock",
                description="Analyze current inventory levels",
                parameters={},
            ),
            TaskStep(
                id="identify_issues",
                action="identify_stock_issues",
                description="Identify low stock and overstock situations",
                parameters={},
                dependencies=["analyze_stock"],
            ),
            TaskStep(
                id="calculate_restock",
                action="calculate_restock_needs",
                description="Calculate optimal restock quantities",
                parameters={},
                dependencies=["identify_issues"],
            ),
            TaskStep(
                id="execute_restock",
                action="execute_restocking",
                description="Execute restocking for identified products",
                parameters={},
                dependencies=["calculate_restock"],
            ),
        ]

        return ExecutionPlan(
            id=plan_id,
            title="Inventory Management",
            description="Analyze and optimize inventory levels",
            steps=steps,
        )

    def _format_plan_for_user(self, plan: ExecutionPlan) -> str:
        """Format execution plan for user presentation."""
        description = f"**{plan.title}**\n{plan.description}\n\nSteps:"

        for i, step in enumerate(plan.steps, 1):
            description += f"\n{i}. {step.description}"

        return description

    async def _handle_plan_continuation(self, user_input: str) -> Dict[str, Any]:
        """Handle user response to plan confirmation."""
        if not self.active_plan:
            return {
                "success": False,
                "message": "No active plan to continue. What would you like me to help you with?",
                "type": "no_active_plan",
            }

        text = user_input.lower().strip()

        if text in ["yes", "y", "ok", "proceed", "continue"]:
            # Execute the plan
            result = await self._execute_plan(self.active_plan)
            self.active_plan = None  # Clear after execution
            return result
        elif text in ["no", "n", "stop", "cancel", "abort"]:
            # Cancel the plan
            plan_title = self.active_plan.title
            self.active_plan = None
            return {
                "success": True,
                "message": f"Plan '{plan_title}' cancelled. What else can I help you with?",
                "type": "plan_cancelled",
            }
        else:
            return {
                "success": True,
                "message": "I didn't understand your response. Please say 'yes' to proceed with the plan or 'no' to cancel it.",
                "type": "clarification_needed",
            }

    async def _execute_plan(self, plan: ExecutionPlan) -> Dict[str, Any]:
        """Execute a complete plan step by step."""
        plan.status = "running"
        results = []

        try:
            completed_steps = 0
            total_steps = len(plan.steps)

            # Execute steps in dependency order
            while completed_steps < total_steps:
                # Find ready steps (dependencies satisfied)
                ready_steps = [
                    step
                    for step in plan.steps
                    if step.status == "pending"
                    and self._dependencies_satisfied(step, plan.steps)
                ]

                if not ready_steps:
                    # Check for deadlock
                    pending_steps = [s for s in plan.steps if s.status == "pending"]
                    if pending_steps:
                        return {
                            "success": False,
                            "message": f"Plan execution stuck - cannot resolve dependencies for: {[s.id for s in pending_steps]}",
                            "type": "execution_deadlock",
                        }
                    break

                # Execute ready steps
                for step in ready_steps:
                    step.status = "running"
                    step_result = await self._execute_step(step, plan.context)

                    if step_result["success"]:
                        step.status = "completed"
                        step.result = step_result.get("data")
                        completed_steps += 1

                        # Store step result in context for subsequent steps
                        plan.context[step.id] = step_result

                        results.append(
                            {
                                "step": step.id,
                                "description": step.description,
                                "success": True,
                                "message": step_result.get("message", ""),
                            }
                        )
                    else:
                        step.status = "failed"
                        step.error_message = step_result.get("message", "Unknown error")
                        results.append(
                            {
                                "step": step.id,
                                "description": step.description,
                                "success": False,
                                "error": step.error_message,
                            }
                        )

                        # Decide whether to continue or abort
                        if self._is_critical_step(step):
                            plan.status = "failed"
                            return {
                                "success": False,
                                "message": f"Plan failed at critical step '{step.description}': {step.error_message}",
                                "type": "critical_step_failed",
                                "results": results,
                            }

            plan.status = "completed"
            success_count = len([r for r in results if r["success"]])

            # Check if the last step generated a report or important output
            final_step_message = ""
            if results and results[-1]["success"]:
                last_step = plan.steps[-1]
                if last_step.result and isinstance(last_step.result, dict):
                    # If the last step has a message or report, include it
                    if "report" in last_step.result:
                        final_step_message = f"\n\n{last_step.result['report']}"
                    elif last_step.result.get("message"):
                        final_step_message = f"\n\n{last_step.result['message']}"

            completion_message = f"Plan '{plan.title}' completed! ({success_count}/{len(results)} steps successful){final_step_message}"

            return {
                "success": True,
                "message": completion_message,
                "type": "plan_completed",
                "results": results,
                "summary": self._generate_execution_summary(results),
            }

        except Exception as e:
            plan.status = "failed"
            logger.error(f"Plan execution error: {e}")
            return {
                "success": False,
                "message": f"Plan execution failed with error: {str(e)}",
                "type": "execution_error",
                "results": results,
            }

    def _dependencies_satisfied(
        self, step: TaskStep, all_steps: List[TaskStep]
    ) -> bool:
        """Check if all dependencies for a step are satisfied."""
        if not step.dependencies:
            return True

        step_map = {s.id: s for s in all_steps}

        for dep_id in step.dependencies:
            dep_step = step_map.get(dep_id)
            if not dep_step or dep_step.status != "completed":
                return False

        return True

    def _is_critical_step(self, step: TaskStep) -> bool:
        """Determine if a step failure should abort the entire plan."""
        critical_actions = [
            "create_sample_products",
            "batch_create_products",
            "collect_all_data",
        ]
        return step.action in critical_actions

    async def _execute_step(
        self, step: TaskStep, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single step."""
        action = step.action
        params = step.parameters

        try:
            # Route to appropriate action handler
            if action == "check_existing_data":
                return await self._check_existing_data()
            elif action == "create_sample_products":
                return await self._create_sample_products(params)
            elif action == "create_sample_customers":
                return await self._create_sample_customers(params)
            elif action == "create_sample_orders":
                return await self._create_sample_orders(params)
            elif action == "create_customer":
                return await self._create_customer(params)
            elif action == "generate_store_summary":
                return await self._generate_store_summary()
            elif action == "collect_all_data":
                return await self._collect_all_data()
            elif action == "analyze_product_data":
                return await self._analyze_product_data(context)
            elif action == "analyze_customer_data":
                return await self._analyze_customer_data(context)
            elif action == "analyze_sales_data":
                return await self._analyze_sales_data(context)
            elif action == "compile_analytics_report":
                return await self._compile_analytics_report(context)
            else:
                return {"success": False, "message": f"Unknown action: {action}"}

        except Exception as e:
            logger.error(f"Step execution failed: {e}")
            return {"success": False, "message": f"Step failed: {str(e)}"}

    # Step execution methods
    async def _check_existing_data(self) -> Dict[str, Any]:
        """Check what data already exists."""
        try:
            products_result = await self.ecommerce_agent.get_all_products()
            customers_result = await self.ecommerce_agent.get_all_customers()
            orders_result = await self.ecommerce_agent.get_all_orders()

            import json

            products = (
                json.loads(products_result.data[0]["text"])
                if products_result.success
                else []
            )
            customers = (
                json.loads(customers_result.data[0]["text"])
                if customers_result.success
                else []
            )
            orders = (
                json.loads(orders_result.data[0]["text"])
                if orders_result.success
                else []
            )

            return {
                "success": True,
                "message": f"Found {len(products)} products, {len(customers)} customers, {len(orders)} orders",
                "data": {
                    "products_count": len(products),
                    "customers_count": len(customers),
                    "orders_count": len(orders),
                },
            }
        except Exception as e:
            return {"success": False, "message": f"Failed to check existing data: {e}"}

    async def _create_sample_products(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create sample products."""
        count = params.get("count", 10)

        # Product templates for different categories
        templates = [
            {
                "name": "Laptop Pro 15",
                "category": "Electronics",
                "price": 1299.99,
                "description": "High-performance laptop",
            },
            {
                "name": "Wireless Mouse",
                "category": "Electronics",
                "price": 49.99,
                "description": "Ergonomic wireless mouse",
            },
            {
                "name": "Running Shoes",
                "category": "Sports",
                "price": 129.99,
                "description": "Comfortable running shoes",
            },
            {
                "name": "Coffee Maker",
                "category": "Home",
                "price": 89.99,
                "description": "Programmable coffee maker",
            },
            {
                "name": "Python Book",
                "category": "Books",
                "price": 39.99,
                "description": "Learn Python programming",
            },
            {
                "name": "Desk Chair",
                "category": "Furniture",
                "price": 199.99,
                "description": "Ergonomic office chair",
            },
            {
                "name": "Bluetooth Speaker",
                "category": "Electronics",
                "price": 79.99,
                "description": "Portable speaker",
            },
            {
                "name": "Yoga Mat",
                "category": "Sports",
                "price": 29.99,
                "description": "Non-slip yoga mat",
            },
            {
                "name": "Kitchen Knife",
                "category": "Home",
                "price": 59.99,
                "description": "Professional chef knife",
            },
            {
                "name": "Notebook",
                "category": "Office",
                "price": 12.99,
                "description": "Lined notebook",
            },
        ]

        created_count = 0
        errors = []

        for i in range(min(count, len(templates))):
            template = templates[i]
            try:
                result = await self.ecommerce_agent.create_product(
                    name=template["name"],
                    description=template["description"],
                    price=template["price"],
                    sku=f"PROD-{i + 1:03d}",
                    category=template["category"],
                    stock_quantity=20 + (i * 3),
                )

                if result.success:
                    created_count += 1
                else:
                    errors.append(
                        f"Failed to create {template['name']}: {result.error}"
                    )

            except Exception as e:
                errors.append(f"Error creating {template['name']}: {str(e)}")

        return {
            "success": created_count > 0,
            "message": f"Created {created_count} products"
            + (f" ({len(errors)} errors)" if errors else ""),
            "data": {"created": created_count, "errors": errors},
        }

    async def _create_sample_customers(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create sample customers."""
        count = params.get("count", 5)

        customer_templates = [
            {"email": "john.doe@example.com", "first_name": "John", "last_name": "Doe"},
            {
                "email": "jane.smith@example.com",
                "first_name": "Jane",
                "last_name": "Smith",
            },
            {
                "email": "bob.wilson@example.com",
                "first_name": "Bob",
                "last_name": "Wilson",
            },
            {
                "email": "alice.brown@example.com",
                "first_name": "Alice",
                "last_name": "Brown",
            },
            {
                "email": "charlie.davis@example.com",
                "first_name": "Charlie",
                "last_name": "Davis",
            },
        ]

        created_count = 0
        errors = []

        for i in range(min(count, len(customer_templates))):
            customer = customer_templates[i]
            try:
                result = await self.ecommerce_agent.create_customer(
                    email=customer["email"],
                    first_name=customer["first_name"],
                    last_name=customer["last_name"],
                    phone=f"+1-555-{1000 + i:04d}",
                )

                if result.success:
                    created_count += 1
                else:
                    errors.append(
                        f"Failed to create {customer['email']}: {result.error}"
                    )

            except Exception as e:
                errors.append(f"Error creating {customer['email']}: {str(e)}")

        return {
            "success": created_count > 0,
            "message": f"Created {created_count} customers"
            + (f" ({len(errors)} errors)" if errors else ""),
            "data": {"created": created_count, "errors": errors},
        }

    async def _create_sample_orders(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create sample orders."""
        count = params.get("count", 3)

        try:
            # Get existing customers and products
            customers_result = await self.ecommerce_agent.get_all_customers()
            products_result = await self.ecommerce_agent.get_all_products()

            if not customers_result.success or not products_result.success:
                return {
                    "success": False,
                    "message": "Could not fetch customers or products",
                }

            import json

            customers = json.loads(customers_result.data[0]["text"])
            products = json.loads(products_result.data[0]["text"])

            if not customers or not products:
                return {
                    "success": False,
                    "message": "No customers or products available",
                }

            created_count = 0
            errors = []

            for i in range(min(count, len(customers))):
                try:
                    customer = customers[i]
                    # Select 1-2 random products
                    import random

                    selected_products = random.sample(products, min(2, len(products)))

                    order_items = []
                    for product in selected_products:
                        order_items.append(
                            {
                                "product_id": product["id"],
                                "quantity": random.randint(1, 3),
                            }
                        )

                    result = await self.ecommerce_agent.create_order(
                        customer_id=customer["id"], items=order_items
                    )

                    if result.success:
                        created_count += 1
                    else:
                        errors.append(
                            f"Failed to create order for {customer['email']}: {result.error}"
                        )

                except Exception as e:
                    errors.append(f"Error creating order {i + 1}: {str(e)}")

            return {
                "success": created_count > 0,
                "message": f"Created {created_count} orders"
                + (f" ({len(errors)} errors)" if errors else ""),
                "data": {"created": created_count, "errors": errors},
            }

        except Exception as e:
            return {"success": False, "message": f"Order creation failed: {str(e)}"}

    async def _generate_store_summary(self) -> Dict[str, Any]:
        """Generate a summary of the store."""
        try:
            products_result = await self.ecommerce_agent.get_all_products()
            customers_result = await self.ecommerce_agent.get_all_customers()
            orders_result = await self.ecommerce_agent.get_all_orders()

            import json

            products = (
                json.loads(products_result.data[0]["text"])
                if products_result.success
                else []
            )
            customers = (
                json.loads(customers_result.data[0]["text"])
                if customers_result.success
                else []
            )
            orders = (
                json.loads(orders_result.data[0]["text"])
                if orders_result.success
                else []
            )

            # Calculate metrics
            total_revenue = sum(order.get("total_amount", 0) for order in orders)
            categories = list(set(p.get("category") for p in products))

            summary = f"""
🏪 **Demo Store Summary**

📊 **Overview:**
• Products: {len(products)} items
• Categories: {len(categories)} ({", ".join(categories[:5])})
• Customers: {len(customers)} registered
• Orders: {len(orders)} completed
• Revenue: ${total_revenue:.2f}

✅ **Store is ready for use!**
            """

            return {
                "success": True,
                "message": "Store summary generated",
                "data": {"summary": summary.strip()},
            }

        except Exception as e:
            return {"success": False, "message": f"Summary generation failed: {str(e)}"}

    async def _collect_all_data(self) -> Dict[str, Any]:
        """Collect all store data for analysis."""
        try:
            products_result = await self.ecommerce_agent.get_all_products()
            customers_result = await self.ecommerce_agent.get_all_customers()
            orders_result = await self.ecommerce_agent.get_all_orders()

            data = {
                "products": products_result.data if products_result.success else [],
                "customers": customers_result.data if customers_result.success else [],
                "orders": orders_result.data if orders_result.success else [],
            }

            return {
                "success": True,
                "message": f"Collected data: {len(data['products'])} products, {len(data['customers'])} customers, {len(data['orders'])} orders",
                "data": data,
            }

        except Exception as e:
            return {"success": False, "message": f"Data collection failed: {str(e)}"}

    async def _analyze_product_data(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze product data."""
        # Implementation for product analysis
        return {
            "success": True,
            "message": "Product analysis completed",
            "data": {"analysis": "product_metrics"},
        }

    async def _analyze_customer_data(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze customer data."""
        # Implementation for customer analysis
        return {
            "success": True,
            "message": "Customer analysis completed",
            "data": {"analysis": "customer_metrics"},
        }

    async def _analyze_sales_data(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sales data."""
        # Implementation for sales analysis
        return {
            "success": True,
            "message": "Sales analysis completed",
            "data": {"analysis": "sales_metrics"},
        }

    async def _compile_analytics_report(
        self, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compile comprehensive analytics report using collected data."""
        try:
            # Get the collected data from context
            collected_data = context.get("collect_data", {}).get("data", {})
            products = collected_data.get("products", [])
            customers = collected_data.get("customers", [])
            orders = collected_data.get("orders", [])

            # Calculate key metrics
            total_products = len(products)
            total_customers = len(customers)
            total_orders = len(orders)

            # Product analytics
            active_products = len([p for p in products if p.get("is_active", True)])
            low_stock_products = len(
                [p for p in products if p.get("stock_quantity", 0) < 10]
            )

            # Category breakdown
            categories = {}
            total_inventory_value = 0
            for product in products:
                category = product.get("category", "Unknown")
                categories[category] = categories.get(category, 0) + 1
                total_inventory_value += product.get("price", 0) * product.get(
                    "stock_quantity", 0
                )

            # Order analytics
            total_revenue = sum(order.get("total_amount", 0) for order in orders)
            completed_orders = len(
                [o for o in orders if o.get("status") == "completed"]
            )

            # Customer analytics
            active_customers = len([c for c in customers if c.get("is_active", True)])

            # Generate report
            report = f"""
📊 **E-COMMERCE ANALYTICS REPORT**
Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

═══════════════════════════════════════

📦 **PRODUCT OVERVIEW**
• Total Products: {total_products}
• Active Products: {active_products}
• Low Stock Alert: {low_stock_products} products (<10 items)
• Total Inventory Value: ${total_inventory_value:,.2f}

**Category Breakdown:**
"""

            for category, count in sorted(categories.items()):
                report += f"  • {category}: {count} products\n"

            report += f"""
👥 **CUSTOMER OVERVIEW**
• Total Customers: {total_customers}
• Active Customers: {active_customers}
• Customer Retention: {(active_customers / total_customers * 100) if total_customers > 0 else 0:.1f}%

📋 **ORDER OVERVIEW**
• Total Orders: {total_orders}
• Completed Orders: {completed_orders}
• Total Revenue: ${total_revenue:,.2f}
• Completion Rate: {(completed_orders / total_orders * 100) if total_orders > 0 else 0:.1f}%

📈 **KEY INSIGHTS**
"""

            # Add insights based on data
            insights = []
            if low_stock_products > 0:
                insights.append(f"⚠️  {low_stock_products} products need restocking")
            if total_revenue > 0:
                avg_order_value = (
                    total_revenue / total_orders if total_orders > 0 else 0
                )
                insights.append(f"💰 Average order value: ${avg_order_value:.2f}")
            if categories:
                top_category = max(categories, key=categories.get)
                insights.append(
                    f"🏆 Top category: {top_category} ({categories[top_category]} products)"
                )

            if insights:
                for insight in insights:
                    report += f"  {insight}\n"
            else:
                report += "  • Store data collected successfully\n  • Ready for detailed analysis\n"

            report += """
═══════════════════════════════════════
Report generated by Smart E-commerce Agent
"""

            return {
                "success": True,
                "message": report.strip(),
                "data": {
                    "report": report.strip(),
                    "metrics": {
                        "total_products": total_products,
                        "total_customers": total_customers,
                        "total_orders": total_orders,
                        "total_revenue": total_revenue,
                        "low_stock_products": low_stock_products,
                    },
                },
            }

        except Exception as e:
            logger.error(f"Error compiling analytics report: {e}")
            return {
                "success": False,
                "message": f"Failed to compile analytics report: {str(e)}",
            }

    def _generate_execution_summary(self, results: List[Dict[str, Any]]) -> str:
        """Generate execution summary."""
        successful = len([r for r in results if r["success"]])
        total = len(results)
        return f"Execution completed: {successful}/{total} steps successful"

    def _provide_help(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Provide help information."""
        help_text = """
🤖 **Smart E-commerce Agent Help**

I can help you with:

**Simple Operations:**
• "Show all products" - List products in store
• "List customers" - Show customer list  
• "Search wireless" - Find products matching query
• "Create product" - Start product creation process

**Complex Operations:**
• "Setup demo store with 20 products" - Create complete demo store
• "Generate analytics report" - Comprehensive business analysis
• "Create 15 products" - Bulk product creation
• "Manage inventory" - Analyze and optimize stock levels

**Examples:**
• "Setup a demo store with 25 products, 15 customers, and 8 orders"
• "Generate a comprehensive analytics report"
• "Create 20 products across different categories"

Just tell me what you'd like to accomplish in natural language!
        """

        return {"success": True, "message": help_text.strip(), "type": "help_response"}

    def _handle_unknown_request(self, user_input: str) -> Dict[str, Any]:
        """Handle unknown requests."""
        return {
            "success": False,
            "message": f"I didn't understand '{user_input}'. Try asking for help to see what I can do, or be more specific about what you need.",
            "type": "unknown_request",
            "suggestions": [
                "show all products",
                "setup demo store",
                "generate analytics report",
                "help",
            ],
        }

    def _format_products(self, products: list) -> str:
        """Format product list for user-friendly display."""
        if not products:
            return "No products found."

        formatted = ""
        for i, product in enumerate(products, 1):
            name = product.get("name", "Unknown Product")
            price = product.get("price", 0)
            currency = product.get("currency", "USD")
            stock = product.get("stock_quantity", 0)
            category = product.get("category", "Unknown")
            sku = product.get("sku", "N/A")

            # Format price nicely
            price_str = (
                f"${price:.2f}" if currency == "USD" else f"{price:.2f} {currency}"
            )

            # Stock status indicator
            stock_status = "🟢" if stock > 20 else "🟡" if stock > 5 else "🔴"

            formatted += f"**{i}. {name}**\n"
            formatted += f"   💰 Price: {price_str}\n"
            formatted += f"   📦 Stock: {stock} {stock_status}\n"
            formatted += f"   🏷️  Category: {category}\n"
            formatted += f"   🔢 SKU: {sku}\n\n"

        return formatted.strip()

    def _format_customers(self, customers: list) -> str:
        """Format customer list for user-friendly display."""
        if not customers:
            return "No customers found."

        formatted = ""
        for i, customer in enumerate(customers, 1):
            # Handle both possible name formats
            if "name" in customer:
                name = customer.get("name", "Unknown Customer")
            else:
                first_name = customer.get("first_name", "")
                last_name = customer.get("last_name", "")
                if first_name or last_name:
                    name = f"{first_name} {last_name}".strip()
                else:
                    name = "Unknown Customer"

            email = customer.get("email", "No email")
            total_orders = customer.get("total_orders", 0)
            created_at = customer.get("created_at", "")

            # Format date nicely
            if created_at:
                try:
                    from datetime import datetime

                    date_obj = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    date_str = date_obj.strftime("%Y-%m-%d")
                except Exception:
                    date_str = created_at[:10] if len(created_at) >= 10 else created_at
            else:
                date_str = "Unknown"

            formatted += f"**{i}. {name}**\n"
            formatted += f"   📧 Email: {email}\n"
            formatted += f"   🛒 Orders: {total_orders}\n"
            formatted += f"   📅 Joined: {date_str}\n\n"

        return formatted.strip()

    def _format_orders(self, orders: list) -> str:
        """Format order list for user-friendly display."""
        if not orders:
            return "No orders found."

        formatted = ""
        for i, order in enumerate(orders, 1):
            order_id = order.get("id", "Unknown ID")

            # Handle customer name - try multiple approaches
            customer_name = order.get("customer_name")
            if not customer_name:
                customer_id = order.get("customer_id", "")
                customer_name = (
                    f"Customer {customer_id}" if customer_id else "Unknown Customer"
                )

            total = order.get("total_amount", 0)
            currency = order.get("currency", "USD")
            status = order.get("status", "Unknown")
            created_at = order.get("created_at", "")

            # Format price
            price_str = (
                f"${total:.2f}" if currency == "USD" else f"{total:.2f} {currency}"
            )

            # Status indicator
            status_icon = (
                "✅"
                if status.lower() == "completed"
                else "⏳"
                if status.lower() == "pending"
                else "📋"
            )

            # Format date
            if created_at:
                try:
                    from datetime import datetime

                    date_obj = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    date_str = date_obj.strftime("%Y-%m-%d %H:%M")
                except Exception:
                    date_str = created_at[:16] if len(created_at) >= 16 else created_at
            else:
                date_str = "Unknown"

            formatted += f"**{i}. Order {order_id}**\n"
            formatted += f"   👤 Customer: {customer_name}\n"
            formatted += f"   💰 Total: {price_str}\n"
            formatted += f"   {status_icon} Status: {status}\n"
            formatted += f"   📅 Date: {date_str}\n\n"

        return formatted.strip()

    async def _create_customer(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a customer with smart natural language parsing."""
        try:
            # Extract original text for parsing
            original_text = params.get("original_text", "")

            # Try to parse customer information from natural language
            parsed_info = self._parse_customer_from_text(original_text)

            # Merge with any explicitly provided parameters
            for key, value in params.items():
                if key != "original_text" and value:
                    parsed_info[key] = value

            # Check required fields
            required_fields = ["email", "first_name", "last_name"]
            missing_fields = [
                field for field in required_fields if not parsed_info.get(field)
            ]

            if missing_fields:
                return {
                    "success": False,
                    "message": f"To create a customer, I need: {', '.join(missing_fields)}. "
                    + f"Parsed from your message: {self._format_parsed_info(parsed_info)}. "
                    + "Please provide the missing information.",
                    "type": "needs_input",
                    "required_fields": missing_fields,
                    "parsed_info": parsed_info,
                }

            # Create the customer
            result = await self.ecommerce_agent.create_customer(
                email=parsed_info["email"],
                first_name=parsed_info["first_name"],
                last_name=parsed_info["last_name"],
                phone=parsed_info.get("phone"),
                address=parsed_info.get("address"),
            )

            if result.success:
                try:
                    import json

                    if isinstance(result.data[0]["text"], str):
                        customer_data = json.loads(result.data[0]["text"])
                    else:
                        customer_data = result.data[0]["text"]

                    customer_name = (
                        f"{parsed_info['first_name']} {parsed_info['last_name']}"
                    )
                    customer_id = customer_data.get("id", "unknown")

                    return {
                        "success": True,
                        "message": f"Successfully created customer: {customer_name} "
                        + f"(ID: {customer_id}, Email: {parsed_info['email']})",
                        "type": "customer_created",
                        "data": customer_data,
                    }
                except Exception as parse_error:
                    logger.error(
                        f"Error parsing customer creation response: {parse_error}"
                    )
                    return {
                        "success": True,
                        "message": f"Customer {parsed_info['first_name']} {parsed_info['last_name']} was created successfully.",
                        "type": "customer_created",
                    }
            else:
                return {
                    "success": False,
                    "message": f"Failed to create customer: {result.error}",
                    "type": "creation_failed",
                }

        except Exception as e:
            logger.error(f"Error in _create_customer: {e}")
            return {
                "success": False,
                "message": f"Error creating customer: {str(e)}",
                "type": "error",
            }

    async def _parse_product_from_text(self, text: str) -> Dict[str, str]:
        """Parse product information from natural language text using LLM (XAI/Grok preferred, OpenAI fallback)."""
        try:
            import os

            logger.info(f"Parsing product text with LLM: {text}")

            # Check for available API keys (prefer XAI over OpenAI)
            xai_api_key = os.getenv("XAI_API_KEY")
            openai_api_key = os.getenv("OPENAI_API_KEY")

            if not xai_api_key and not openai_api_key:
                logger.warning(
                    "No XAI or OpenAI API key found, falling back to pattern matching"
                )
                return self._fallback_parse_product(text)

            # Create a structured prompt for product parsing
            prompt = f"""
You are a product data extraction expert. Parse the following text and extract product information.

Text to parse: "{text}"

Extract the following fields if present in the text:
- name: The product name
- description: Product description 
- price: Price in dollars (number only, no $ symbol)
- sku: Product SKU/code
- category: Product category
- stock_quantity: Stock quantity (number only)

Respond with valid JSON only, no other text. If a field is not found, omit it from the response.
Example format:
{{
    "name": "pen",
    "description": "this is a pen", 
    "price": "2",
    "sku": "pen-5inches",
    "category": "bureautic",
    "stock_quantity": "10"
}}
"""

            # Try XAI/Grok first (preferred)
            if xai_api_key:
                try:
                    from openai import AsyncOpenAI

                    logger.info("Using XAI/Grok for product parsing")
                    client = AsyncOpenAI(
                        api_key=xai_api_key, base_url="https://api.x.ai/v1"
                    )

                    # Try different Grok model names in order of preference
                    grok_models = [
                        "grok-3",
                        "grok-2-1212",
                        "grok-2",
                        "grok-beta",
                        "grok-1",
                    ]

                    for model_name in grok_models:
                        try:
                            response = await client.chat.completions.create(
                                model=model_name,
                                messages=[
                                    {
                                        "role": "system",
                                        "content": "You are a helpful assistant that extracts product information from text and responds only with valid JSON.",
                                    },
                                    {"role": "user", "content": prompt},
                                ],
                                temperature=0.1,
                                max_tokens=200,
                            )

                            # If we get here, the model worked
                            logger.info(f"Successfully used XAI model: {model_name}")

                            # Parse the LLM response
                            llm_output = response.choices[0].message.content.strip()
                            logger.info(f"XAI/Grok response: {llm_output}")

                            parsed = self._parse_llm_response(llm_output)
                            if parsed:
                                logger.info(
                                    f"Successfully parsed product info with XAI/Grok: {parsed}"
                                )
                                return parsed
                            break

                        except Exception as model_error:
                            logger.warning(
                                f"XAI model {model_name} failed: {model_error}"
                            )
                            continue

                    # If no models worked, log and continue to OpenAI fallback
                    logger.warning("All XAI/Grok models failed, trying OpenAI...")

                except Exception as e:
                    logger.error(f"Error with XAI/Grok setup: {e}")
                    # Continue to try OpenAI if available

            # Try OpenAI if XAI failed or isn't available
            if openai_api_key:
                try:
                    from openai import AsyncOpenAI

                    logger.info("Using OpenAI for product parsing")
                    client = AsyncOpenAI(api_key=openai_api_key)

                    response = await client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a helpful assistant that extracts product information from text and responds only with valid JSON.",
                            },
                            {"role": "user", "content": prompt},
                        ],
                        temperature=0.1,
                        max_tokens=200,
                    )

                    # Parse the LLM response
                    llm_output = response.choices[0].message.content.strip()
                    logger.info(f"OpenAI response: {llm_output}")

                    parsed = self._parse_llm_response(llm_output)
                    if parsed:
                        logger.info(
                            f"Successfully parsed product info with OpenAI: {parsed}"
                        )
                        return parsed

                except Exception as e:
                    logger.error(f"Error calling OpenAI API: {e}")

            # If all LLM attempts failed, fall back to pattern matching
            logger.warning("All LLM attempts failed, falling back to pattern matching")
            return self._fallback_parse_product(text)

        except ImportError as e:
            logger.error(f"OpenAI library not available: {e}")
            return self._fallback_parse_product(text)
        except Exception as e:
            logger.error(f"Error in LLM product parsing: {e}")
            return self._fallback_parse_product(text)

    def _parse_llm_response(self, llm_output: str) -> Dict[str, str]:
        """Parse and validate LLM response JSON."""
        try:
            # First try direct JSON parsing
            parsed = json.loads(llm_output)
            return parsed
        except json.JSONDecodeError:
            # Try to extract JSON from response if it's wrapped in other text
            json_match = re.search(r"\{.*\}", llm_output, re.DOTALL)
            if json_match:
                try:
                    parsed = json.loads(json_match.group())
                    return parsed
                except json.JSONDecodeError:
                    pass

        logger.error(f"Could not parse LLM response as JSON: {llm_output}")
        return {}

    def _parse_structured_format(self, text: str) -> Dict[str, str]:
        """Parse comma-separated format like 'pen, this is a pen, $2, pen-5inches, bureautic, 10'."""
        import re

        parsed = {}

        # Split by comma and clean up
        parts = [part.strip() for part in text.split(",")]

        if len(parts) >= 6:
            # Standard format: name, description, price, sku, category, stock
            parsed["name"] = (
                parts[0].replace("create", "").replace("product", "").strip()
            )
            parsed["description"] = parts[1]

            # Extract price (remove $ if present)
            price_part = parts[2].replace("$", "").strip()
            if price_part and re.match(r"^\d+(\.\d{2})?$", price_part):
                parsed["price"] = price_part

            parsed["sku"] = parts[3]
            parsed["category"] = parts[4]

            # Extract stock quantity
            stock_part = parts[5].strip()
            if stock_part.isdigit():
                parsed["stock_quantity"] = stock_part
        elif len(parts) >= 3:
            # Partial format, try to intelligently assign
            idx = 0

            # First part is likely the name
            name_part = parts[idx].replace("create", "").replace("product", "").strip()
            if name_part:
                parsed["name"] = name_part
                idx += 1

            # Look for description (non-price, non-numeric parts)
            while idx < len(parts):
                part = parts[idx].strip()
                if not part.startswith("$") and not part.isdigit() and "-" not in part:
                    parsed["description"] = part
                    idx += 1
                    break
                idx += 1

            # Look for price
            for i, part in enumerate(parts):
                if part.strip().startswith("$") or re.match(
                    r"^\$?\d+(\.\d{2})?$", part.strip()
                ):
                    price = part.strip().replace("$", "")
                    if re.match(r"^\d+(\.\d{2})?$", price):
                        parsed["price"] = price
                    break

            # Look for SKU (contains hyphen)
            for part in parts:
                if "-" in part.strip() and len(part.strip()) > 3:
                    parsed["sku"] = part.strip()
                    break

            # Look for stock (pure numbers)
            for part in reversed(parts):  # Start from end
                if part.strip().isdigit() and int(part.strip()) > 0:
                    parsed["stock_quantity"] = part.strip()
                    break

            # Remaining parts might be category
            for part in parts:
                part = part.strip()
                if (
                    part not in [parsed.get("name"), parsed.get("description")]
                    and not part.startswith("$")
                    and not part.isdigit()
                    and "-" not in part
                    and len(part) > 2
                ):
                    parsed["category"] = part
                    break

        return parsed

    def _parse_flexible_format(self, text: str) -> Dict[str, str]:
        """Parse more flexible natural language format."""
        import re

        parsed = {}

        # Look for product name at the beginning
        name_patterns = [
            r"(?:create|add|new)\s+(?:product\s+)?([a-zA-Z][a-zA-Z0-9\s\-_]+?)(?:\s*,|\s+with|\s+this)",
            r"^([a-zA-Z][a-zA-Z0-9\s\-_]+?)(?:\s*,|\s+this\s+is|\s+description)",
        ]

        for pattern in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                exclude_words = {"product", "item", "create", "add", "new"}
                if name.lower() not in exclude_words:
                    parsed["name"] = name
                    break

        # Look for "this is a..." descriptions
        desc_match = re.search(r"this\s+is\s+(?:a\s+)?([^,\$]+)", text, re.IGNORECASE)
        if desc_match:
            parsed["description"] = desc_match.group(1).strip()

        # Look for price
        price_match = re.search(r"\$(\d+(?:\.\d{2})?)", text)
        if price_match:
            parsed["price"] = price_match.group(1)

        # Look for SKU (hyphenated codes)
        sku_match = re.search(r"\b([a-zA-Z]+-[a-zA-Z0-9]+)\b", text)
        if sku_match:
            parsed["sku"] = sku_match.group(1)

        # Look for common categories
        categories = [
            "bureautic",
            "kitchen",
            "electronics",
            "clothing",
            "books",
            "sports",
            "toys",
            "home",
            "garden",
            "office",
        ]
        for category in categories:
            if category in text.lower():
                parsed["category"] = category
                break

        # Look for stock at the end
        stock_match = re.search(r"\b(\d+)\s*$", text)
        if stock_match:
            parsed["stock_quantity"] = stock_match.group(1)

        return parsed

    def _fallback_parse_product(self, text: str) -> Dict[str, str]:
        """Fallback parsing using simple pattern matching."""
        import re

        parsed = {}

        # Simple comma-separated parsing for format like "pen, this is a pen, $2, pen-5inches, bureautic, 10"
        parts = [part.strip() for part in text.split(",")]

        if len(parts) >= 6:
            # Assume format: name, description, price, sku, category, stock
            parsed["name"] = parts[0]
            parsed["description"] = parts[1]

            # Extract price (remove $ if present)
            price_part = parts[2].replace("$", "").strip()
            if price_part and price_part.replace(".", "").isdigit():
                parsed["price"] = price_part

            parsed["sku"] = parts[3]
            parsed["category"] = parts[4]

            # Extract stock quantity
            stock_part = parts[5].strip()
            if stock_part.isdigit():
                parsed["stock_quantity"] = stock_part

        # If comma-separated didn't work, try some basic patterns
        if not parsed:
            # Look for price pattern
            price_match = re.search(r"\$(\d+(?:\.\d{2})?)", text)
            if price_match:
                parsed["price"] = price_match.group(1)

            # Look for hyphenated SKU
            sku_match = re.search(r"\b([a-zA-Z]+-[a-zA-Z0-9]+)\b", text)
            if sku_match:
                parsed["sku"] = sku_match.group(1)

            # Look for numbers at end (stock)
            stock_match = re.search(r"\b(\d+)\s*$", text)
            if stock_match:
                parsed["stock_quantity"] = stock_match.group(1)

        return parsed

    def _format_parsed_product_info(self, parsed_info: Dict[str, str]) -> str:
        """Format parsed product information for display."""
        if not parsed_info:
            return "no product information detected"

        formatted = []
        if parsed_info.get("name"):
            formatted.append(f"Name: {parsed_info['name']}")
        if parsed_info.get("description"):
            formatted.append(f"Description: {parsed_info['description']}")
        if parsed_info.get("price"):
            formatted.append(f"Price: ${parsed_info['price']}")
        if parsed_info.get("sku"):
            formatted.append(f"SKU: {parsed_info['sku']}")
        if parsed_info.get("category"):
            formatted.append(f"Category: {parsed_info['category']}")
        if parsed_info.get("stock_quantity"):
            formatted.append(f"Stock: {parsed_info['stock_quantity']} units")

        return ", ".join(formatted) if formatted else "no valid product information"

    def _parse_customer_from_text(self, text: str) -> Dict[str, str]:
        """Parse customer information from natural language text."""
        import re

        parsed = {}

        # Email patterns - more comprehensive
        email_patterns = [
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            r"email[:\s]+([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})",
            r"at\s+([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})",
        ]

        for pattern in email_patterns:
            email_match = re.search(pattern, text, re.IGNORECASE)
            if email_match:
                if "@" in email_match.group(0):
                    parsed["email"] = email_match.group(0).strip()
                else:
                    parsed["email"] = email_match.group(1).strip()
                break

        # Phone patterns
        phone_patterns = [
            r"\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b",
            r"phone[:\s]+(\+?[\d\s\-\(\)\.]+)",
            r"call[:\s]+(\+?[\d\s\-\(\)\.]+)",
            r"tel[:\s]+(\+?[\d\s\-\(\)\.]+)",
        ]

        for pattern in phone_patterns:
            phone_match = re.search(pattern, text, re.IGNORECASE)
            if phone_match:
                if pattern == phone_patterns[0]:  # Standard US format
                    parsed["phone"] = (
                        f"({phone_match.group(1)}) {phone_match.group(2)}-{phone_match.group(3)}"
                    )
                else:
                    parsed["phone"] = phone_match.group(1).strip()
                break

        # Name patterns - try to identify first and last names
        name_patterns = [
            # "create customer John Doe"
            r"(?:create|add|new|register).*?customer\s+([A-Z][a-z]+)\s+([A-Z][a-z]+)",
            # "customer named John Doe" or "customer John Doe"
            r"customer\s+(?:named\s+)?([A-Z][a-z]+)\s+([A-Z][a-z]+)",
            # "name is John Doe" or "name: John Doe"
            r"name\s*(?:is|:)\s*([A-Z][a-z]+)\s+([A-Z][a-z]+)",
            # "first name John last name Doe"
            r"first\s*name\s*[:\s]*([A-Z][a-z]+).*?last\s*name\s*[:\s]*([A-Z][a-z]+)",
            # "John Doe" at the beginning of text (capitalized words that might be names)
            r"^\s*([A-Z][a-z]+)\s+([A-Z][a-z]+)\b",
            # "John Doe" followed by email
            r"\b([A-Z][a-z]+)\s+([A-Z][a-z]+)\s+[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}",
        ]

        for pattern in name_patterns:
            name_match = re.search(pattern, text, re.IGNORECASE)
            if name_match:
                potential_first = name_match.group(1).capitalize()
                potential_last = name_match.group(2).capitalize()

                # Avoid common false positives and validate names
                common_words = {
                    "Create",
                    "Customer",
                    "Name",
                    "Email",
                    "Phone",
                    "Address",
                    "New",
                    "Add",
                    "Named",
                    "With",
                    "And",
                    "The",
                    "At",
                    "In",
                    "On",
                    "For",
                    "To",
                    "From",
                }
                if (
                    potential_first not in common_words
                    and potential_last not in common_words
                    and len(potential_first) > 1
                    and len(potential_last) > 1
                    and potential_first.isalpha()
                    and potential_last.isalpha()
                ):
                    parsed["first_name"] = potential_first
                    parsed["last_name"] = potential_last
                    break

        # Address patterns
        address_patterns = [
            r"address[:\s]+(.+?)(?:\s+phone|\s+email|\s*$)",
            r"lives?\s+(?:at|in)\s+(.+?)(?:\s+phone|\s+email|\s*$)",
            r"(?:street|st|ave|avenue|road|rd|blvd|boulevard)[:\s]+(.+?)(?:\s+phone|\s+email|\s*$)",
        ]

        for pattern in address_patterns:
            address_match = re.search(pattern, text, re.IGNORECASE)
            if address_match:
                address = address_match.group(1).strip()
                # Clean up common artifacts
                address = re.sub(
                    r"\s+(and|with|phone|email|tel).*$",
                    "",
                    address,
                    flags=re.IGNORECASE,
                )
                if len(address) > 5:  # Reasonable minimum address length
                    parsed["address"] = address
                break

        # Try to extract from more structured text like "John Doe john@email.com (555) 123-4567"
        if not parsed.get("first_name") or not parsed.get("last_name"):
            # Look for pattern: Name Email Phone
            structured_pattern = r"([A-Z][a-z]+)\s+([A-Z][a-z]+)\s+([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})"
            structured_match = re.search(structured_pattern, text)
            if structured_match:
                parsed["first_name"] = structured_match.group(1)
                parsed["last_name"] = structured_match.group(2)
                if not parsed.get("email"):
                    parsed["email"] = structured_match.group(3)

        return parsed

    def _format_parsed_info(self, parsed_info: Dict[str, str]) -> str:
        """Format parsed customer information for display."""
        if not parsed_info:
            return "no information could be extracted"

        formatted = []
        if parsed_info.get("first_name") and parsed_info.get("last_name"):
            formatted.append(
                f"Name: {parsed_info['first_name']} {parsed_info['last_name']}"
            )
        elif parsed_info.get("first_name"):
            formatted.append(f"First name: {parsed_info['first_name']}")
        elif parsed_info.get("last_name"):
            formatted.append(f"Last name: {parsed_info['last_name']}")

        if parsed_info.get("email"):
            formatted.append(f"Email: {parsed_info['email']}")

        if parsed_info.get("phone"):
            formatted.append(f"Phone: {parsed_info['phone']}")

        if parsed_info.get("address"):
            formatted.append(f"Address: {parsed_info['address']}")

        return ", ".join(formatted) if formatted else "no valid information"

    async def _enhance_orders_with_customer_info(self, orders: list) -> list:
        """Enhance order data with customer name information."""
        enhanced_orders = []

        for order in orders:
            enhanced_order = order.copy()
            customer_id = order.get("customer_id")

            if customer_id and not order.get("customer_name"):
                try:
                    # Try to get customer information
                    customer_result = await self.ecommerce_agent.get_customer(
                        customer_id, "id"
                    )
                    if customer_result.success and customer_result.data:
                        # Use robust JSON parsing
                        customer_data = robust_json_parse(
                            customer_result.data[0], "customer_info"
                        )
                        if customer_data is None:
                            enhanced_order["customer_name"] = f"Customer {customer_id}"
                            continue

                        # Build customer name
                        first_name = customer_data.get("first_name", "")
                        last_name = customer_data.get("last_name", "")
                        if first_name or last_name:
                            enhanced_order["customer_name"] = (
                                f"{first_name} {last_name}".strip()
                            )
                        else:
                            enhanced_order["customer_name"] = customer_data.get(
                                "email", "Unknown Customer"
                            )

                except Exception as e:
                    logger.debug(
                        f"Could not fetch customer info for {customer_id}: {e}"
                    )
                    enhanced_order["customer_name"] = f"Customer {customer_id}"

            enhanced_orders.append(enhanced_order)

        return enhanced_orders

    async def _handle_single_product(
        self, parsed_info: Dict[str, str], params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle creation of a single product."""
        # Merge parsed info with any explicitly provided parameters
        for key, value in parsed_info.items():
            if value and not params.get(key):
                params[key] = value

        required_fields = [
            "name",
            "description",
            "price",
            "sku",
            "category",
            "stock_quantity",
        ]
        missing_fields = [field for field in required_fields if not params.get(field)]

        if missing_fields:
            return {
                "success": True,
                "message": "To create a product, I need: name, description, price, SKU, category, and stock quantity. "
                + f"From your message, I found: {self._format_parsed_product_info(parsed_info)}. "
                + f"Still missing: {', '.join(missing_fields)}. "
                + "Please provide the missing information.",
                "type": "needs_input",
                "required_fields": missing_fields,
                "parsed_info": parsed_info,
            }
        else:
            # We have all required fields, create the product
            return await self._create_single_product(params)

    async def _handle_multiple_products(
        self, products_list: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Handle creation of multiple products."""
        if not products_list:
            return {
                "success": False,
                "message": "No product information found in your request.",
                "type": "error",
            }

        required_fields = [
            "name",
            "description",
            "price",
            "sku",
            "category",
            "stock_quantity",
        ]

        # Check if all products have required fields
        incomplete_products = []
        complete_products = []

        for i, product in enumerate(products_list):
            missing_fields = [
                field for field in required_fields if not product.get(field)
            ]
            if missing_fields:
                incomplete_products.append(
                    {"index": i + 1, "product": product, "missing": missing_fields}
                )
            else:
                complete_products.append(product)

        if incomplete_products:
            # Some products are missing information
            missing_info = []
            for item in incomplete_products:
                product_name = item["product"].get("name", f"Product {item['index']}")
                missing_info.append(
                    f"{product_name}: missing {', '.join(item['missing'])}"
                )

            return {
                "success": True,
                "message": f"I found {len(products_list)} products to create, but some are missing information:\n\n"
                + "\n".join(missing_info)
                + "\n\nPlease provide the missing information so I can create all products.",
                "type": "needs_input",
                "parsed_products": products_list,
                "incomplete_products": incomplete_products,
                "complete_products": complete_products,
            }
        else:
            # All products have complete information, create them
            return await self._create_multiple_products(complete_products)

    async def _create_single_product(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a single product."""
        try:
            result = await self.ecommerce_agent.create_product(
                name=params["name"],
                description=params["description"],
                price=float(params["price"]),
                sku=params["sku"],
                category=params["category"],
                stock_quantity=int(params["stock_quantity"]),
            )

            if result.success:
                return {
                    "success": True,
                    "message": f"Successfully created product: {params['name']} (SKU: {params['sku']}) in {params['category']} category. "
                    + f"Price: ${params['price']}, Stock: {params['stock_quantity']} units.",
                    "type": "product_created",
                    "data": params,
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to create product: {result.error}",
                    "type": "creation_failed",
                }
        except Exception as e:
            logger.error(f"Error creating product: {e}")
            return {
                "success": False,
                "message": f"Error creating product: {str(e)}",
                "type": "error",
            }

    async def _create_multiple_products(
        self, products: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Create multiple products."""
        created_products = []
        failed_products = []

        for product in products:
            try:
                result = await self.ecommerce_agent.create_product(
                    name=product["name"],
                    description=product["description"],
                    price=float(product["price"]),
                    sku=product["sku"],
                    category=product["category"],
                    stock_quantity=int(product["stock_quantity"]),
                )

                if result.success:
                    created_products.append(product)
                else:
                    failed_products.append({"product": product, "error": result.error})
            except Exception as e:
                logger.error(
                    f"Error creating product {product.get('name', 'unknown')}: {e}"
                )
                failed_products.append({"product": product, "error": str(e)})

        # Build response message
        if created_products and not failed_products:
            # All products created successfully
            return {
                "success": True,
                "message": f"Successfully created {len(created_products)} products:\n\n"
                + "\n".join(
                    [
                        f"• {p['name']} (SKU: {p['sku']}) - ${p['price']} in {p['category']}"
                        for p in created_products
                    ]
                ),
                "type": "multiple_products_created",
                "created_products": created_products,
                "total_created": len(created_products),
            }
        elif created_products and failed_products:
            # Some products created, some failed
            failure_info = [
                f"• {f['product']['name']}: {f['error']}" for f in failed_products
            ]

            return {
                "success": True,  # Partial success
                "message": f"Created {len(created_products)} products successfully:\n"
                + "\n".join(
                    [f"• {p['name']} (SKU: {p['sku']})" for p in created_products]
                )
                + f"\n\nFailed to create {len(failed_products)} products:\n"
                + "\n".join(failure_info),
                "type": "partial_products_created",
                "created_products": created_products,
                "failed_products": failed_products,
                "total_created": len(created_products),
                "total_failed": len(failed_products),
            }
        else:
            # All products failed
            failure_info = [
                f"• {f['product']['name']}: {f['error']}" for f in failed_products
            ]
            return {
                "success": False,
                "message": f"Failed to create all {len(failed_products)} products:\n"
                + "\n".join(failure_info),
                "type": "multiple_products_failed",
                "failed_products": failed_products,
                "total_failed": len(failed_products),
            }

    async def _parse_order_from_text(self, text: str) -> Dict[str, Any]:
        """Parse order information from natural language text."""
        import re

        order_info = {}

        # Try to extract customer name - look for patterns like "for [Name Name]"
        name_patterns = [
            r"(?:for|from|customer)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)",
            r"^.*?\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b.*?(?:order|wants|needs)",
        ]

        for pattern in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                full_name = match.group(1).strip()
                name_parts = full_name.split()
                if len(name_parts) >= 2:
                    order_info["customer_name"] = full_name
                    order_info["first_name"] = name_parts[0]
                    order_info["last_name"] = " ".join(name_parts[1:])
                break

        # Extract email if present
        email_match = re.search(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text
        )
        if email_match:
            order_info["customer_email"] = email_match.group(0)

            # If no name was found yet, try to extract name from email
            if "customer_name" not in order_info:
                email_local = email_match.group(0).split("@")[0]
                # Handle formats like "Eli.Gile", "eli_gile", "eliGile", etc.
                if "." in email_local:
                    parts = email_local.split(".")
                    if len(parts) >= 2:
                        first_name = parts[0].capitalize()
                        last_name = parts[1].capitalize()
                        order_info["customer_name"] = f"{first_name} {last_name}"
                        order_info["first_name"] = first_name
                        order_info["last_name"] = last_name
                elif "_" in email_local:
                    parts = email_local.split("_")
                    if len(parts) >= 2:
                        first_name = parts[0].capitalize()
                        last_name = parts[1].capitalize()
                        order_info["customer_name"] = f"{first_name} {last_name}"
                        order_info["first_name"] = first_name
                        order_info["last_name"] = last_name
                else:
                    # For camelCase or single names, use the local part as first name
                    # and create a reasonable last name or use email as fallback
                    order_info["customer_name"] = email_local.capitalize()
                    order_info["first_name"] = email_local.capitalize()
                    order_info["last_name"] = ""

        # Extract product information - look for patterns like "2 pens", "5 laptops", etc.
        product_patterns = [
            # "2 pens", "5 laptops"
            r"(\d+)\s+([a-zA-Z][a-zA-Z0-9\s\-_]*?)(?:\s|$|,|\.|!|\?)",
            # "order 2 pens"
            r"order\s+(\d+)\s+([a-zA-Z][a-zA-Z0-9\s\-_]*?)(?:\s|$|,|\.|!|\?)",
        ]

        products = []
        for pattern in product_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                quantity = int(match.group(1))
                product_name = match.group(2).strip()

                # Clean up product name - remove common words
                exclude_words = {
                    "for",
                    "the",
                    "a",
                    "an",
                    "and",
                    "of",
                    "in",
                    "on",
                    "at",
                    "to",
                    "from",
                }
                clean_name = " ".join(
                    [
                        word
                        for word in product_name.split()
                        if word.lower() not in exclude_words and len(word) > 1
                    ]
                )

                if clean_name and quantity > 0:
                    products.append({"name": clean_name, "quantity": quantity})

        if products:
            order_info["products"] = products

        return order_info

    async def _create_order_with_info(
        self, order_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create an order with the parsed information."""
        try:
            # First, find or create the customer
            customer_info = await self._find_or_create_customer(order_info)
            logger.info(f"Customer info result: {customer_info}")
            if not customer_info.get("success"):
                return customer_info

            customer_id = customer_info["customer_id"]
            logger.info(f"Using customer_id: '{customer_id}'")

            # Find products and build order items
            order_items = []
            missing_products = []

            for product_request in order_info["products"]:
                product_name = product_request["name"]
                quantity = product_request["quantity"]

                # Search for the product
                search_result = await self.ecommerce_agent.search_products(product_name)
                logger.info(
                    f"Product search for '{product_name}': success={search_result.success}, data={search_result.data}"
                )

                if (
                    search_result.success
                    and search_result.data
                    and len(search_result.data) > 0
                ):
                    try:
                        # Parse search results using robust JSON parsing
                        if (
                            isinstance(search_result.data, list)
                            and len(search_result.data) > 0
                        ):
                            logger.info(
                                f"Raw product data before parsing: {search_result.data[0]}"
                            )
                            products = robust_json_parse(
                                search_result.data[0], f"product_search_{product_name}"
                            )
                            logger.info(f"Parsed products: {products}")

                            # Handle both single product (dict) and multiple products (list)
                            if isinstance(products, dict):
                                # Single product returned
                                product = products
                                order_items.append(
                                    {
                                        "product_id": product["id"],
                                        "quantity": quantity,
                                        "price": float(product["price"]),
                                    }
                                )
                            elif isinstance(products, list) and len(products) > 0:
                                # Multiple products returned, use the first one
                                product = products[0]
                                order_items.append(
                                    {
                                        "product_id": product["id"],
                                        "quantity": quantity,
                                        "price": float(product["price"]),
                                    }
                                )
                            else:
                                logger.warning(
                                    f"No products found in parsed result for '{product_name}'"
                                )
                                # Try singular form if plural didn't work
                                if product_name.endswith("s") and len(product_name) > 1:
                                    singular_name = product_name[:-1]
                                    logger.info(
                                        f"Trying singular form: '{singular_name}'"
                                    )
                                    singular_result = (
                                        await self.ecommerce_agent.search_products(
                                            singular_name
                                        )
                                    )
                                    if (
                                        singular_result.success
                                        and singular_result.data
                                        and isinstance(singular_result.data, list)
                                        and len(singular_result.data) > 0
                                    ):
                                        singular_products = robust_json_parse(
                                            singular_result.data[0],
                                            f"product_search_{singular_name}",
                                        )
                                        if isinstance(singular_products, dict):
                                            product = singular_products
                                            order_items.append(
                                                {
                                                    "product_id": product["id"],
                                                    "quantity": quantity,
                                                    "price": float(product["price"]),
                                                }
                                            )
                                        elif (
                                            isinstance(singular_products, list)
                                            and len(singular_products) > 0
                                        ):
                                            product = singular_products[0]
                                            order_items.append(
                                                {
                                                    "product_id": product["id"],
                                                    "quantity": quantity,
                                                    "price": float(product["price"]),
                                                }
                                            )
                                        else:
                                            missing_products.append(product_name)
                                    else:
                                        missing_products.append(product_name)
                                else:
                                    missing_products.append(product_name)
                        else:
                            logger.warning(
                                f"Invalid search result data structure for '{product_name}': {search_result.data}"
                            )
                            missing_products.append(product_name)
                    except (KeyError, ValueError, TypeError) as e:
                        logger.error(
                            f"Error processing product search results for '{product_name}': {e}"
                        )
                        missing_products.append(product_name)
                else:
                    logger.warning(
                        f"Product search failed for '{product_name}': success={search_result.success}, error={getattr(search_result, 'error', 'No error')}"
                    )

                    # Try singular form if plural didn't work
                    if product_name.endswith("s") and len(product_name) > 1:
                        singular_name = product_name[:-1]
                        logger.info(f"Trying singular form: '{singular_name}'")
                        singular_result = await self.ecommerce_agent.search_products(
                            singular_name
                        )

                        if (
                            singular_result.success
                            and singular_result.data
                            and len(singular_result.data) > 0
                        ):
                            try:
                                singular_products = robust_json_parse(
                                    singular_result.data[0],
                                    f"product_search_{singular_name}",
                                )

                                if isinstance(singular_products, dict):
                                    product = singular_products
                                    order_items.append(
                                        {
                                            "product_id": product["id"],
                                            "quantity": quantity,
                                            "price": float(product["price"]),
                                        }
                                    )
                                elif (
                                    isinstance(singular_products, list)
                                    and len(singular_products) > 0
                                ):
                                    product = singular_products[0]
                                    order_items.append(
                                        {
                                            "product_id": product["id"],
                                            "quantity": quantity,
                                            "price": float(product["price"]),
                                        }
                                    )
                                else:
                                    missing_products.append(product_name)
                            except Exception as e:
                                logger.error(
                                    f"Error parsing singular search result for '{singular_name}': {e}"
                                )
                                missing_products.append(product_name)
                        else:
                            missing_products.append(product_name)
                    else:
                        missing_products.append(product_name)

            if missing_products:
                return {
                    "success": False,
                    "message": f"Could not find the following products: {', '.join(missing_products)}. "
                    + "Please check the product names and try again.",
                    "type": "products_not_found",
                    "missing_products": missing_products,
                }

            if not order_items:
                return {
                    "success": False,
                    "message": "No valid products found for the order.",
                    "type": "no_products",
                }

            # Create the order
            logger.info(
                f"Creating order with customer_id='{customer_id}' and {len(order_items)} items: {order_items}"
            )
            result = await self.ecommerce_agent.create_order(
                customer_id=customer_id, items=order_items
            )
            logger.info(
                f"Order creation result: success={result.success}, data={result.data}, error={getattr(result, 'error', 'None')}"
            )

            if result.success:
                # Build success message
                item_descriptions = []
                for i, item in enumerate(order_items):
                    product_name = order_info["products"][i]["name"]
                    item_descriptions.append(f"{item['quantity']} x {product_name}")

                customer_name = order_info.get(
                    "customer_name", order_info.get("customer_email", "customer")
                )

                return {
                    "success": True,
                    "message": f"Successfully created order for {customer_name}:\n"
                    + "\n".join([f"• {desc}" for desc in item_descriptions])
                    + f"\n\nOrder total: ${sum(item['price'] * item['quantity'] for item in order_items):.2f}",
                    "type": "order_created",
                    "order_info": {
                        "customer": customer_name,
                        "items": item_descriptions,
                        "total": sum(
                            item["price"] * item["quantity"] for item in order_items
                        ),
                    },
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to create order: {result.error}",
                    "type": "order_creation_failed",
                }

        except Exception as e:
            logger.error(f"Error creating order: {e}")
            return {
                "success": False,
                "message": f"Error creating order: {str(e)}",
                "type": "error",
            }

    async def _find_or_create_customer(
        self, order_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Find existing customer or create a new one."""
        try:
            customer_email = order_info.get("customer_email")
            customer_name = order_info.get("customer_name")

            if customer_email:
                # Try to find customer by email
                search_result = await self.ecommerce_agent.get_customer(
                    customer_email, "email"
                )
                if search_result.success and search_result.data:
                    try:
                        # Use robust JSON parsing
                        customer_data = robust_json_parse(
                            search_result.data[0], "existing_customer"
                        )
                        if customer_data is not None:
                            return {
                                "success": True,
                                "customer_id": customer_data.get("id"),
                                "found_existing": True,
                            }
                    except Exception as e:
                        logger.debug(f"Customer not found by email: {e}")

            # If customer not found by email, try to create a new one
            if customer_name and customer_email:
                first_name = order_info.get("first_name", customer_name.split()[0])
                last_name = order_info.get(
                    "last_name",
                    " ".join(customer_name.split()[1:])
                    if len(customer_name.split()) > 1
                    else "",
                )

                create_result = await self.ecommerce_agent.create_customer(
                    email=customer_email, first_name=first_name, last_name=last_name
                )

                logger.info(
                    f"Customer creation result: success={create_result.success}, data={create_result.data}"
                )

                if create_result.success:
                    try:
                        # Check if we got an error message indicating duplicate email
                        if (
                            create_result.data
                            and len(create_result.data) > 0
                            and isinstance(create_result.data[0], str)
                            and "UNIQUE constraint failed" in create_result.data[0]
                        ):
                            logger.info(
                                "Customer already exists due to UNIQUE constraint, finding existing customer"
                            )

                            # Customer already exists, find it by listing all customers
                            list_result = await self.ecommerce_agent.list_customers()
                            logger.info(
                                f"Listed customers for search: success={list_result.success}, data_length={len(list_result.data) if list_result.data else 0}"
                            )

                            if list_result.success and list_result.data:
                                customers = robust_json_parse(
                                    list_result.data[0], "all_customers_for_existing"
                                )

                                if customers and isinstance(customers, list):
                                    # Find customer with matching email
                                    for customer in customers:
                                        if customer.get("email") == customer_email:
                                            customer_id = customer.get("id")
                                            logger.info(
                                                f"Found existing customer: {customer.get('first_name', '')} {customer.get('last_name', '')} with ID: {customer_id}"
                                            )
                                            return {
                                                "success": True,
                                                "customer_id": customer_id,
                                                "found_existing": True,
                                            }

                                    logger.warning(
                                        f"Could not find customer with email {customer_email} in customer list"
                                    )
                                else:
                                    logger.warning(
                                        f"Failed to parse customer list: {customers}"
                                    )

                            # If all else fails, try the direct search approach
                            logger.info("Trying direct customer search as last resort")
                            search_result = await self.ecommerce_agent.get_customer(
                                customer_email, "email"
                            )

                            if search_result.success and search_result.data:
                                existing_customer = robust_json_parse(
                                    search_result.data[0], "existing_customer_direct"
                                )

                                if existing_customer and isinstance(
                                    existing_customer, dict
                                ):
                                    customer_id = existing_customer.get("id")
                                    if customer_id:
                                        logger.info(
                                            f"Found customer via direct search: {customer_id}"
                                        )
                                        return {
                                            "success": True,
                                            "customer_id": customer_id,
                                            "found_existing": True,
                                        }

                        # Normal customer creation case (not a duplicate)
                        if create_result.data and len(create_result.data) > 0:
                            customer_data = robust_json_parse(
                                create_result.data[0], "new_customer"
                            )
                            if customer_data is None:
                                logger.error(
                                    "Error parsing new customer data - using fallback"
                                )
                                # Use a fallback approach - generate a placeholder ID
                                return {
                                    "success": True,
                                    "customer_id": f"customer_{customer_email.split('@')[0]}",
                                    "created_new": True,
                                }

                            return {
                                "success": True,
                                "customer_id": customer_data.get(
                                    "id", f"customer_{customer_email.split('@')[0]}"
                                ),
                                "created_new": True,
                            }
                        else:
                            logger.warning("No customer data returned from creation")
                            return {
                                "success": True,
                                "customer_id": f"customer_{customer_email.split('@')[0]}",
                                "created_new": True,
                            }
                    except Exception as e:
                        logger.error(f"Error parsing new customer data: {e}")
                        return {
                            "success": True,
                            "customer_id": "new_customer",  # Fallback
                            "created_new": True,
                        }

            # If we only have a name, ask for email
            if customer_name and not customer_email:
                return {
                    "success": False,
                    "message": f"I found the customer name '{customer_name}', but I need an email address to create or find the customer. "
                    + "Please provide the customer's email address.",
                    "type": "needs_email",
                    "customer_name": customer_name,
                }

            return {
                "success": False,
                "message": "I need either a customer email address or both name and email to process the order.",
                "type": "needs_customer_info",
            }

        except Exception as e:
            logger.error(f"Error finding/creating customer: {e}")
            return {
                "success": False,
                "message": f"Error processing customer information: {str(e)}",
                "type": "error",
            }

    async def _classify_intent_with_llm(self, user_input: str) -> Dict[str, Any]:
        """Use LLM to classify user intent when rule-based approach fails."""
        try:
            import os

            # Check for available API keys (prefer XAI over OpenAI)
            xai_api_key = os.getenv("XAI_API_KEY")
            openai_api_key = os.getenv("OPENAI_API_KEY")

            if not xai_api_key and not openai_api_key:
                logger.warning("No LLM API key available for intent classification")
                return {
                    "type": "unknown",
                    "text": user_input.lower().strip(),
                    "original": user_input,
                }

            # Create intent classification prompt
            prompt = f"""
You are an intelligent assistant for an e-commerce system. Classify the following user request into one of these categories:

Categories:
1. "create_product" - Creating new products in the catalog
2. "create_customer" - Creating/registering new customer accounts (when explicitly asked to create a customer)
3. "create_order" - Creating orders/purchases for existing or new customers (includes phrases like "order for", "buy", "purchase")
4. "list_products" - Showing/listing products
5. "list_customers" - Showing/listing customers
6. "list_orders" - Showing/listing orders
7. "search_products" - Searching for products
8. "list_low_stock" - Showing low stock items
9. "complex_operation" - Complex multi-step operations like setting up demo stores, analytics
10. "help_request" - Asking for help or information about capabilities
11. "unknown" - Cannot determine intent

IMPORTANT: 
- If the request mentions "order for [person]" or "order for [email]", it's "create_order", NOT "create_customer"
- "create_customer" is only when explicitly asked to create/register a customer account
- "create_order" includes purchasing products for someone, even if customer details are provided

Examples:
- "create an order for john@email.com for 2 pens" → create_order
- "place order for jane doe for 3 laptops" → create_order  
- "register new customer john smith" → create_customer
- "add customer jane@email.com" → create_customer

User request: "{user_input}"

Respond with valid JSON only:
{{
    "type": "simple_query",
    "action": "[one of the actions above]",
    "original": "{user_input}",
    "confidence": [0.0-1.0]
}}

For complex operations, use:
{{
    "type": "complex_operation", 
    "operation": "[specific operation]",
    "original": "{user_input}",
    "confidence": [0.0-1.0]
}}

For help requests, use:
{{
    "type": "help_request",
    "original": "{user_input}",
    "confidence": [0.0-1.0]
}}
"""

            # Try XAI/Grok first (preferred)
            if xai_api_key:
                try:
                    from openai import AsyncOpenAI

                    logger.info("Using XAI/Grok for intent classification")
                    client = AsyncOpenAI(
                        api_key=xai_api_key, base_url="https://api.x.ai/v1"
                    )

                    # Try different Grok model names
                    grok_models = ["grok-3", "grok-2-1212", "grok-2", "grok-beta"]

                    for model_name in grok_models:
                        try:
                            response = await client.chat.completions.create(
                                model=model_name,
                                messages=[
                                    {
                                        "role": "system",
                                        "content": "You are an expert at understanding user intents in e-commerce contexts. Respond only with valid JSON.",
                                    },
                                    {"role": "user", "content": prompt},
                                ],
                                temperature=0.1,
                                max_tokens=150,
                            )

                            # Parse the LLM response
                            llm_output = response.choices[0].message.content.strip()
                            logger.info(
                                f"LLM intent classification response: {llm_output}"
                            )

                            parsed = self._parse_llm_response(llm_output)
                            if parsed and parsed.get("confidence", 0) > 0.5:
                                logger.info(f"LLM classified intent: {parsed}")
                                return parsed
                            break

                        except Exception as model_error:
                            logger.warning(
                                f"XAI model {model_name} failed for intent classification: {model_error}"
                            )
                            continue

                except Exception as e:
                    logger.error(f"Error with XAI/Grok intent classification: {e}")

            # Try OpenAI if XAI failed or isn't available
            if openai_api_key:
                try:
                    from openai import AsyncOpenAI

                    logger.info("Using OpenAI for intent classification")
                    client = AsyncOpenAI(api_key=openai_api_key)

                    response = await client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {
                                "role": "system",
                                "content": "You are an expert at understanding user intents in e-commerce contexts. Respond only with valid JSON.",
                            },
                            {"role": "user", "content": prompt},
                        ],
                        temperature=0.1,
                        max_tokens=150,
                    )

                    # Parse the LLM response
                    llm_output = response.choices[0].message.content.strip()
                    logger.info(f"OpenAI intent classification response: {llm_output}")

                    parsed = self._parse_llm_response(llm_output)
                    if parsed and parsed.get("confidence", 0) > 0.5:
                        logger.info(f"OpenAI classified intent: {parsed}")
                        return parsed

                except Exception as e:
                    logger.error(f"Error with OpenAI intent classification: {e}")

            # If all LLM attempts failed, return unknown
            logger.warning("All LLM attempts failed for intent classification")
            return {
                "type": "unknown",
                "text": user_input.lower().strip(),
                "original": user_input,
            }

        except ImportError as e:
            logger.error(f"OpenAI library not available for intent classification: {e}")
            return {
                "type": "unknown",
                "text": user_input.lower().strip(),
                "original": user_input,
            }
        except Exception as e:
            logger.error(f"Error in LLM intent classification: {e}")
            return {
                "type": "unknown",
                "text": user_input.lower().strip(),
                "original": user_input,
            }
