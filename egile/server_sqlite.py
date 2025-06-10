#!/usr/bin/env python3
"""
Generic E-commerce MCP Server with SQLite Database

This MCP server provides tools and resources for common e-commerce operations
including products, orders, customers, and inventory management.
Uses SQLite for persistent data storage.
"""

import asyncio
import json
import logging
import sys
from dataclasses import asdict

try:
    import mcp.types as types
    from mcp.server import Server, NotificationOptions
    from mcp.server.models import InitializationOptions
    import mcp.server.stdio
except ImportError as e:
    print(f"Failed to import MCP modules: {e}", file=sys.stderr)
    print("Please install the MCP package: pip install mcp", file=sys.stderr)
    sys.exit(1)

# Import database components
try:
    from .database import EcommerceDatabase, Product, Customer, Order, OrderItem
except ImportError:
    # Fallback for direct execution
    try:
        from database import EcommerceDatabase, Product, Customer, Order, OrderItem
    except ImportError as e:
        print(f"Failed to import database modules: {e}", file=sys.stderr)
        sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ecommerce-mcp-server")

# Initialize database
db = EcommerceDatabase()

# Initialize MCP server
server = Server("ecommerce-mcp-server")


@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """List available e-commerce resources."""
    return [
        types.Resource(
            uri="ecommerce://products",
            name="Products Database",
            description="Access to product catalog",
            mimeType="application/json",
        ),
        types.Resource(
            uri="ecommerce://customers",
            name="Customers Database",
            description="Access to customer information",
            mimeType="application/json",
        ),
        types.Resource(
            uri="ecommerce://orders",
            name="Orders Database",
            description="Access to order management",
            mimeType="application/json",
        ),
    ]


@server.read_resource()
async def handle_read_resource(uri: str) -> list[types.TextContent]:
    """Read e-commerce resource data."""
    logger.info(f"🔍 RESOURCE HANDLER CALLED: {uri}")
    logger.info(f"   Handler function: handle_read_resource")

    try:
        if uri == "ecommerce://products":
            products = db.get_all_products()
            logger.info(f"Found {len(products)} products")
            data = json.dumps([asdict(product) for product in products], indent=2)
            result = [types.TextContent(type="text", text=data)]
            logger.info(f"   Returning {len(result)} TextContent objects")
            return result
        elif uri == "ecommerce://customers":
            customers = db.get_all_customers()
            logger.info(f"Found {len(customers)} customers")
            data = json.dumps([asdict(customer) for customer in customers], indent=2)
            return [types.TextContent(type="text", text=data)]
        elif uri == "ecommerce://orders":
            orders = db.get_all_orders()
            logger.info(f"Found {len(orders)} orders")
            data = json.dumps(
                [asdict(order) for order in orders], indent=2, default=str
            )
            return [types.TextContent(type="text", text=data)]
        else:
            logger.error(f"❌ Unknown resource URI: {uri}")
            raise ValueError(f"Unknown resource: {uri}")
    except Exception as e:
        logger.error(f"❌ Error reading resource {uri}: {e}")
        raise


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available e-commerce tools."""
    logger.info("Tools list requested")

    tools = [
        # Product management tools
        types.Tool(
            name="create_product",
            description="Create a new product in the catalog",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Product name"},
                    "description": {
                        "type": "string",
                        "description": "Product description",
                    },
                    "price": {"type": "number", "description": "Product price"},
                    "currency": {
                        "type": "string",
                        "default": "USD",
                        "description": "Currency code",
                    },
                    "sku": {"type": "string", "description": "Stock keeping unit"},
                    "category": {"type": "string", "description": "Product category"},
                    "stock_quantity": {
                        "type": "integer",
                        "description": "Initial stock quantity",
                    },
                },
                "required": [
                    "name",
                    "description",
                    "price",
                    "sku",
                    "category",
                    "stock_quantity",
                ],
            },
        ),
        types.Tool(
            name="get_product",
            description="Get product details by ID or SKU",
            inputSchema={
                "type": "object",
                "properties": {
                    "identifier": {
                        "type": "string",
                        "description": "Product ID or SKU",
                    },
                    "search_by": {
                        "type": "string",
                        "enum": ["id", "sku"],
                        "default": "id",
                    },
                },
                "required": ["identifier"],
            },
        ),
        types.Tool(
            name="update_product",
            description="Update product information",
            inputSchema={
                "type": "object",
                "properties": {
                    "product_id": {"type": "string", "description": "Product ID"},
                    "updates": {"type": "object", "description": "Fields to update"},
                },
                "required": ["product_id", "updates"],
            },
        ),
        types.Tool(
            name="search_products",
            description="Search products by name, category, or description",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "category": {"type": "string", "description": "Filter by category"},
                    "min_price": {
                        "type": "number",
                        "description": "Minimum price filter",
                    },
                    "max_price": {
                        "type": "number",
                        "description": "Maximum price filter",
                    },
                    "in_stock_only": {"type": "boolean", "default": False},
                },
                "required": ["query"],
            },
        ),
        # Customer management tools
        types.Tool(
            name="create_customer",
            description="Create a new customer",
            inputSchema={
                "type": "object",
                "properties": {
                    "email": {"type": "string", "description": "Customer email"},
                    "first_name": {"type": "string", "description": "First name"},
                    "last_name": {"type": "string", "description": "Last name"},
                    "phone": {"type": "string", "description": "Phone number"},
                    "address": {"type": "object", "description": "Customer address"},
                },
                "required": ["email", "first_name", "last_name"],
            },
        ),
        types.Tool(
            name="get_customer",
            description="Get customer details by ID or email",
            inputSchema={
                "type": "object",
                "properties": {
                    "identifier": {
                        "type": "string",
                        "description": "Customer ID or email",
                    },
                    "search_by": {
                        "type": "string",
                        "enum": ["id", "email"],
                        "default": "id",
                    },
                },
                "required": ["identifier"],
            },
        ),
        # Order management tools
        types.Tool(
            name="create_order",
            description="Create a new order",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string", "description": "Customer ID"},
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "product_id": {"type": "string"},
                                "quantity": {"type": "integer"},
                            },
                            "required": ["product_id", "quantity"],
                        },
                    },
                    "currency": {"type": "string", "default": "USD"},
                },
                "required": ["customer_id", "items"],
            },
        ),
        types.Tool(
            name="get_order",
            description="Get order details by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "order_id": {"type": "string", "description": "Order ID"},
                },
                "required": ["order_id"],
            },
        ),
        types.Tool(
            name="update_order_status",
            description="Update order status",
            inputSchema={
                "type": "object",
                "properties": {
                    "order_id": {"type": "string", "description": "Order ID"},
                    "status": {
                        "type": "string",
                        "enum": [
                            "pending",
                            "confirmed",
                            "shipped",
                            "delivered",
                            "cancelled",
                        ],
                    },
                },
                "required": ["order_id", "status"],
            },
        ),
        # Inventory tools
        types.Tool(
            name="update_stock",
            description="Update product stock quantity",
            inputSchema={
                "type": "object",
                "properties": {
                    "product_id": {"type": "string", "description": "Product ID"},
                    "quantity": {
                        "type": "integer",
                        "description": "New stock quantity",
                    },
                    "operation": {
                        "type": "string",
                        "enum": ["set", "add", "subtract"],
                        "default": "set",
                    },
                },
                "required": ["product_id", "quantity"],
            },
        ),
        types.Tool(
            name="get_low_stock_products",
            description="Get products with low stock",
            inputSchema={
                "type": "object",
                "properties": {
                    "threshold": {
                        "type": "integer",
                        "default": 10,
                        "description": "Low stock threshold",
                    },
                },
            },
        ),
        # Data access tools (workaround for resource issues)
        types.Tool(
            name="get_all_products",
            description="Get all products from the database",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="get_all_customers",
            description="Get all customers from the database",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="get_all_orders",
            description="Get all orders from the database",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]

    logger.info(f"Returning {len(tools)} tools")
    return tools


# Tool implementations
@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls for e-commerce operations."""

    if name == "create_product":
        product_id = db.get_next_id("prod")
        product = Product(
            id=product_id,
            name=arguments["name"],
            description=arguments["description"],
            price=arguments["price"],
            currency=arguments.get("currency", "USD"),
            sku=arguments["sku"],
            category=arguments["category"],
            stock_quantity=arguments["stock_quantity"],
        )
        created_product = db.create_product(product)
        return [
            types.TextContent(
                type="text",
                text=f"Product created successfully: {json.dumps(asdict(created_product), indent=2)}",
            )
        ]

    elif name == "get_product":
        identifier = arguments["identifier"]
        search_by = arguments.get("search_by", "id")

        if search_by == "id":
            product = db.get_product(identifier)
        else:  # search by SKU
            product = db.get_product_by_sku(identifier)

        if product:
            return [
                types.TextContent(
                    type="text", text=json.dumps(asdict(product), indent=2)
                )
            ]
        else:
            return [
                types.TextContent(type="text", text=f"Product not found: {identifier}")
            ]

    elif name == "update_product":
        product_id = arguments["product_id"]
        updates = arguments["updates"]

        success = db.update_product(product_id, updates)
        if success:
            updated_product = db.get_product(product_id)
            return [
                types.TextContent(
                    type="text",
                    text=f"Product updated: {json.dumps(asdict(updated_product), indent=2)}",
                )
            ]
        else:
            return [
                types.TextContent(type="text", text=f"Product not found: {product_id}")
            ]

    elif name == "search_products":
        query = arguments["query"]
        category = arguments.get("category")
        min_price = arguments.get("min_price")
        max_price = arguments.get("max_price")
        in_stock_only = arguments.get("in_stock_only", False)

        results = db.search_products(
            query, category, min_price, max_price, in_stock_only
        )
        return [
            types.TextContent(
                type="text", text=json.dumps([asdict(p) for p in results], indent=2)
            )
        ]

    elif name == "create_customer":
        customer_id = db.get_next_id("cust")
        customer = Customer(
            id=customer_id,
            email=arguments["email"],
            first_name=arguments["first_name"],
            last_name=arguments["last_name"],
            phone=arguments.get("phone"),
            address=arguments.get("address"),
        )
        created_customer = db.create_customer(customer)
        return [
            types.TextContent(
                type="text",
                text=f"Customer created: {json.dumps(asdict(created_customer), indent=2)}",
            )
        ]

    elif name == "get_customer":
        identifier = arguments["identifier"]
        search_by = arguments.get("search_by", "id")

        if search_by == "id":
            customer = db.get_customer(identifier)
        else:  # search by email
            customer = db.get_customer_by_email(identifier)

        if customer:
            return [
                types.TextContent(
                    type="text", text=json.dumps(asdict(customer), indent=2)
                )
            ]
        else:
            return [
                types.TextContent(type="text", text=f"Customer not found: {identifier}")
            ]

    elif name == "create_order":
        customer_id = arguments["customer_id"]
        items_data = arguments["items"]
        currency = arguments.get("currency", "USD")

        # Verify customer exists
        customer = db.get_customer(customer_id)
        if not customer:
            return [
                types.TextContent(
                    type="text", text=f"Customer not found: {customer_id}"
                )
            ]

        order_items = []
        total_amount = 0.0

        for item_data in items_data:
            product_id = item_data["product_id"]
            quantity = item_data["quantity"]

            product = db.get_product(product_id)
            if not product:
                return [
                    types.TextContent(
                        type="text", text=f"Product not found: {product_id}"
                    )
                ]

            if product.stock_quantity < quantity:
                return [
                    types.TextContent(
                        type="text", text=f"Insufficient stock for product {product_id}"
                    )
                ]

            unit_price = product.price
            item_total = unit_price * quantity

            order_items.append(
                OrderItem(
                    product_id=product_id,
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=item_total,
                )
            )
            total_amount += item_total

            # Update stock
            db.update_stock(product_id, quantity, "subtract")

        order_id = db.get_next_id("order")
        order = Order(
            id=order_id,
            customer_id=customer_id,
            items=order_items,
            total_amount=total_amount,
            currency=currency,
        )
        created_order = db.create_order(order)

        return [
            types.TextContent(
                type="text",
                text=f"Order created: {json.dumps(asdict(created_order), indent=2, default=str)}",
            )
        ]

    elif name == "get_order":
        order_id = arguments["order_id"]
        order = db.get_order(order_id)

        if order:
            return [
                types.TextContent(
                    type="text", text=json.dumps(asdict(order), indent=2, default=str)
                )
            ]
        else:
            return [types.TextContent(type="text", text=f"Order not found: {order_id}")]

    elif name == "update_order_status":
        order_id = arguments["order_id"]
        new_status = arguments["status"]

        success = db.update_order_status(order_id, new_status)
        if success:
            return [
                types.TextContent(
                    type="text", text=f"Order status updated to {new_status}"
                )
            ]
        else:
            return [types.TextContent(type="text", text=f"Order not found: {order_id}")]

    elif name == "update_stock":
        product_id = arguments["product_id"]
        quantity = arguments["quantity"]
        operation = arguments.get("operation", "set")

        success = db.update_stock(product_id, quantity, operation)
        if success:
            product = db.get_product(product_id)
            return [
                types.TextContent(
                    type="text",
                    text=f"Stock updated for {product_id}: {product.stock_quantity}",
                )
            ]
        else:
            return [
                types.TextContent(type="text", text=f"Product not found: {product_id}")
            ]

    elif name == "get_low_stock_products":
        threshold = arguments.get("threshold", 10)
        low_stock_products = db.get_low_stock_products(threshold)

        return [
            types.TextContent(
                type="text",
                text=json.dumps([asdict(p) for p in low_stock_products], indent=2),
            )
        ]

    # Data access tools (workaround for resource issues)
    elif name == "get_all_products":
        products = db.get_all_products()
        return [
            types.TextContent(
                type="text",
                text=json.dumps([asdict(p) for p in products], indent=2),
            )
        ]

    elif name == "get_all_customers":
        customers = db.get_all_customers()
        return [
            types.TextContent(
                type="text",
                text=json.dumps([asdict(c) for c in customers], indent=2),
            )
        ]

    elif name == "get_all_orders":
        orders = db.get_all_orders()
        return [
            types.TextContent(
                type="text",
                text=json.dumps([asdict(o) for o in orders], indent=2, default=str),
            )
        ]

    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Run the server using stdin/stdout streams."""
    logger.info("Starting E-commerce MCP Server...")

    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="ecommerce-mcp-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
