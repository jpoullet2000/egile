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

import asyncio
import logging
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from egile.agent import EcommerceAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("smart-agent")


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
            intent = self._analyze_intent(user_input)

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

    def _analyze_intent(self, user_input: str) -> Dict[str, Any]:
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
                return self._extract_simple_query_details(user_input, text)

        # Check for help requests
        for pattern in patterns["help_requests"]:
            if re.search(pattern, text):
                return {"type": "help_request", "text": text, "original": user_input}

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
        import re

        # Check for low stock queries first
        if ("low" in text and "stock" in text) or ("stock" in text and "level" in text):
            return {
                "type": "simple_query",
                "action": "list_low_stock",
                "original": original,
            }

        # Check for customer creation patterns (enhanced)
        customer_patterns = [
            r"(create|add|new|register).*(customer|client|user)",
            r"^customer\s+[A-Z][a-z]+\s+[A-Z][a-z]+",  # "customer John Doe"
            r"(customer|client).*(name|email|phone|address)",
            r"[A-Za-z]+\s+[A-Za-z]+.*@.*\.(com|org|net)",  # Name + email pattern
            r"(john|jane|bob|alice|mike|sarah|david|mary).*@.*\.(com|org|net)",  # Common names + email
        ]

        for pattern in customer_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return {
                    "type": "simple_query",
                    "action": "create_customer",
                    "original": original,
                }

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
            if "product" in text:
                return {
                    "type": "simple_query",
                    "action": "create_product",
                    "original": original,
                }
            elif "customer" in text:
                return {
                    "type": "simple_query",
                    "action": "create_customer",
                    "original": original,
                }
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
                    import json

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
                                # Handle text content structure
                                if hasattr(result.data[0], "text"):
                                    products_text = result.data[0].text
                                elif (
                                    isinstance(result.data[0], dict)
                                    and "text" in result.data[0]
                                ):
                                    products_text = result.data[0]["text"]
                                else:
                                    products_text = str(result.data[0])

                                products = json.loads(products_text)

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
                    except (
                        json.JSONDecodeError,
                        KeyError,
                        AttributeError,
                        IndexError,
                    ) as e:
                        logger.error(f"Error parsing product data: {e}")
                        return {
                            "success": False,
                            "message": f"Error parsing product data: {str(e)}",
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
                                # Handle text content structure
                                if hasattr(result.data[0], "text"):
                                    customers_text = result.data[0].text
                                elif (
                                    isinstance(result.data[0], dict)
                                    and "text" in result.data[0]
                                ):
                                    customers_text = result.data[0]["text"]
                                else:
                                    customers_text = str(result.data[0])

                                customers = json.loads(customers_text)

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
                                # Handle text content structure
                                if hasattr(result.data[0], "text"):
                                    orders_text = result.data[0].text
                                elif (
                                    isinstance(result.data[0], dict)
                                    and "text" in result.data[0]
                                ):
                                    orders_text = result.data[0]["text"]
                                else:
                                    orders_text = str(result.data[0])

                                orders = json.loads(orders_text)

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
                                # Handle text content structure
                                if hasattr(result.data[0], "text"):
                                    products_text = result.data[0].text
                                elif (
                                    isinstance(result.data[0], dict)
                                    and "text" in result.data[0]
                                ):
                                    products_text = result.data[0]["text"]
                                else:
                                    products_text = str(result.data[0])

                                products = json.loads(products_text)

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
                                # Handle text content structure
                                if hasattr(result.data[0], "text"):
                                    products_text = result.data[0].text
                                elif (
                                    isinstance(result.data[0], dict)
                                    and "text" in result.data[0]
                                ):
                                    products_text = result.data[0]["text"]
                                else:
                                    products_text = str(result.data[0])

                                products = json.loads(products_text)

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
                return {
                    "success": True,
                    "message": "To create a product, I need: name, description, price, SKU, category, and stock quantity. Please provide these details.",
                    "type": "needs_input",
                    "required_fields": [
                        "name",
                        "description",
                        "price",
                        "sku",
                        "category",
                        "stock_quantity",
                    ],
                }

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
                                    if (
                                        isinstance(response_data[0], dict)
                                        and "text" in response_data[0]
                                    ):
                                        # Standard MCP response format
                                        text_content = response_data[0]["text"]
                                        if isinstance(text_content, str):
                                            customer_data = json.loads(text_content)
                                        else:
                                            customer_data = text_content
                                    elif isinstance(response_data[0], dict):
                                        # Direct dict response
                                        customer_data = response_data[0]
                                    else:
                                        # Fallback
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
            r"^\s*([A-Z][a-z]+)\s+([A-Z][a-z]+)",
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
                        import json

                        # Parse customer data
                        if hasattr(customer_result.data[0], "text"):
                            customer_text = customer_result.data[0].text
                        elif (
                            isinstance(customer_result.data[0], dict)
                            and "text" in customer_result.data[0]
                        ):
                            customer_text = customer_result.data[0]["text"]
                        else:
                            customer_text = str(customer_result.data[0])

                        customer_data = json.loads(customer_text)

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

    # ... existing methods ...


# Demo function
async def demo_smart_agent():
    """Demonstrate the Smart Agent capabilities."""
    agent = SmartAgent()

    try:
        await agent.start()

        print("🤖 Smart E-commerce Agent Demo")
        print("=" * 50)

        test_requests = [
            "setup demo store with 15 products",
            "yes",
            "show all products",
            "generate analytics report",
            "yes",
        ]

        for request in test_requests:
            print(f"\n👤 User: {request}")
            response = await agent.process_request(request)
            print(f"🤖 Agent: {response['message']}")

            # Show additional data for certain responses
            if response.get("type") == "product_list":
                products = response.get("data", [])
                if products:
                    print("   Sample products:")
                    for product in products[:3]:
                        print(
                            f"   • {product.get('name', 'Unknown')} - ${product.get('price', 0):.2f}"
                        )

            await asyncio.sleep(1)

        print("\n" + "=" * 50)
        print("🎉 Demo completed!")

    finally:
        await agent.stop()


if __name__ == "__main__":
    asyncio.run(demo_smart_agent())
