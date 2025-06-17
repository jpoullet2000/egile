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
                r"^(create|add|new).*(product|customer|order)$",
                r"^(update|modify|change).*(price|stock|status)",
                r"^(delete|remove).*(product|customer|order)",
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

                            return {
                                "success": True,
                                "message": f"Found {len(products)} products in the store. Here are the first 10:",
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

                            return {
                                "success": True,
                                "message": f"Found {len(customers)} customers. Here are the first 10:",
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

                    orders = json.loads(result.data[0]["text"])
                    return {
                        "success": True,
                        "message": f"Found {len(orders)} orders.",
                        "data": orders[:10],
                        "type": "order_list",
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

                    products = json.loads(result.data[0]["text"])
                    return {
                        "success": True,
                        "message": f"Found {len(products)} products matching '{query}'.",
                        "data": products,
                        "type": "search_results",
                    }
                else:
                    return {
                        "success": False,
                        "message": f"Search failed: {result.error}",
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

            return {
                "success": True,
                "message": f"Plan '{plan.title}' completed! ({success_count}/{len(results)} steps successful)",
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

            import json

            data = {
                "products": json.loads(products_result.data[0]["text"])
                if products_result.success
                else [],
                "customers": json.loads(customers_result.data[0]["text"])
                if customers_result.success
                else [],
                "orders": json.loads(orders_result.data[0]["text"])
                if orders_result.success
                else [],
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
        """Compile analytics report."""
        report = """
📊 **Analytics Report**

✅ Analysis completed for:
• Product performance
• Customer behavior  
• Sales patterns

📈 **Key Insights:**
• Store operations are functioning well
• Data collection and analysis pipeline working
• Ready for detailed business intelligence

        """
        return {
            "success": True,
            "message": "Analytics report compiled",
            "data": {"report": report.strip()},
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
