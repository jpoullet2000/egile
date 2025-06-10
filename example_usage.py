#!/usr/bin/env python3
"""
Example usage and testing script for the E-commerce MCP Server
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional


# Import the data models (these would normally come from the server module)
@dataclass
class Product:
    id: str
    name: str
    description: str
    price: float
    currency: str
    sku: str
    category: str
    stock_quantity: int
    is_active: bool = True
    created_at: str = None
    updated_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.now().isoformat()


@dataclass
class Customer:
    id: str
    email: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    address: Optional[Dict[str, str]] = None
    created_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


@dataclass
class OrderItem:
    product_id: str
    quantity: int
    unit_price: float
    total_price: float


@dataclass
class Order:
    id: str
    customer_id: str
    items: List[OrderItem]
    total_amount: float
    currency: str
    status: str = "pending"
    created_at: str = None
    updated_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.now().isoformat()


# Mock databases for demonstration
products_db: Dict[str, Product] = {}
customers_db: Dict[str, Customer] = {}
orders_db: Dict[str, Order] = {}


def setup_sample_data():
    """Set up some sample data for testing."""

    # Sample products
    products = [
        Product(
            id="prod_000001",
            name="Wireless Headphones",
            description="Premium wireless headphones with active noise cancellation",
            price=199.99,
            currency="USD",
            sku="WH-NC-001",
            category="Electronics",
            stock_quantity=25,
        ),
        Product(
            id="prod_000002",
            name="Bluetooth Speaker",
            description="Portable bluetooth speaker with 12-hour battery life",
            price=79.99,
            currency="USD",
            sku="BT-SPK-002",
            category="Electronics",
            stock_quantity=40,
        ),
        Product(
            id="prod_000003",
            name="USB-C Cable",
            description="High-speed USB-C charging cable, 6ft length",
            price=19.99,
            currency="USD",
            sku="USB-C-6FT",
            category="Accessories",
            stock_quantity=100,
        ),
        Product(
            id="prod_000004",
            name="Phone Case",
            description="Protective phone case with drop protection",
            price=29.99,
            currency="USD",
            sku="CASE-PROT-001",
            category="Accessories",
            stock_quantity=5,  # Low stock example
        ),
    ]

    for product in products:
        products_db[product.id] = product

    # Sample customers
    customers = [
        Customer(
            id="cust_000001",
            email="john.doe@example.com",
            first_name="John",
            last_name="Doe",
            phone="+1-555-0123",
            address={
                "street": "123 Main Street",
                "city": "Anytown",
                "state": "CA",
                "zip": "12345",
                "country": "US",
            },
        ),
        Customer(
            id="cust_000002",
            email="jane.smith@example.com",
            first_name="Jane",
            last_name="Smith",
            phone="+1-555-0456",
            address={
                "street": "456 Oak Avenue",
                "city": "Other City",
                "state": "NY",
                "zip": "67890",
                "country": "US",
            },
        ),
    ]

    for customer in customers:
        customers_db[customer.id] = customer

    # Sample order
    order_items = [
        OrderItem(
            product_id="prod_000001", quantity=1, unit_price=199.99, total_price=199.99
        ),
        OrderItem(
            product_id="prod_000003", quantity=2, unit_price=19.99, total_price=39.98
        ),
    ]

    order = Order(
        id="order_000001",
        customer_id="cust_000001",
        items=order_items,
        total_amount=239.97,
        currency="USD",
        status="confirmed",
    )

    orders_db[order.id] = order

    print("Sample data loaded successfully!")


def print_sample_data():
    """Print the current state of all data."""

    print("\n=== PRODUCTS ===")
    for product in products_db.values():
        print(f"ID: {product.id}")
        print(f"Name: {product.name}")
        print(f"Price: ${product.price} {product.currency}")
        print(f"SKU: {product.sku}")
        print(f"Stock: {product.stock_quantity}")
        print(f"Category: {product.category}")
        print("-" * 40)

    print("\n=== CUSTOMERS ===")
    for customer in customers_db.values():
        print(f"ID: {customer.id}")
        print(f"Name: {customer.first_name} {customer.last_name}")
        print(f"Email: {customer.email}")
        print(f"Phone: {customer.phone}")
        if customer.address:
            print(
                f"Address: {customer.address['street']}, {customer.address['city']}, {customer.address['state']}"
            )
        print("-" * 40)

    print("\n=== ORDERS ===")
    for order in orders_db.values():
        print(f"ID: {order.id}")
        print(f"Customer: {order.customer_id}")
        print(f"Total: ${order.total_amount} {order.currency}")
        print(f"Status: {order.status}")
        print(f"Items: {len(order.items)}")
        for item in order.items:
            product = products_db.get(item.product_id)
            product_name = product.name if product else "Unknown Product"
            print(f"  - {item.quantity}x {product_name} @ ${item.unit_price}")
        print("-" * 40)


def demonstrate_search():
    """Demonstrate product search functionality."""

    print("\n=== PRODUCT SEARCH EXAMPLES ===")

    # Search by keyword
    print("\nSearching for 'wireless':")
    for product in products_db.values():
        if (
            "wireless" in product.name.lower()
            or "wireless" in product.description.lower()
        ):
            print(f"  - {product.name} (${product.price})")

    # Search by category
    print("\nElectronics category:")
    for product in products_db.values():
        if product.category == "Electronics":
            print(f"  - {product.name} (Stock: {product.stock_quantity})")

    # Low stock items
    print("\nLow stock items (≤10):")
    for product in products_db.values():
        if product.stock_quantity <= 10:
            print(f"  - {product.name} (Stock: {product.stock_quantity})")


def simulate_order_workflow():
    """Simulate a complete order workflow."""

    print("\n=== ORDER WORKFLOW SIMULATION ===")

    # Check stock before order
    print(
        "\nBefore order - Bluetooth Speaker stock:",
        products_db["prod_000002"].stock_quantity,
    )

    # Create new order
    new_order_items = [
        OrderItem(
            product_id="prod_000002", quantity=2, unit_price=79.99, total_price=159.98
        )
    ]

    new_order = Order(
        id="order_000002",
        customer_id="cust_000002",
        items=new_order_items,
        total_amount=159.98,
        currency="USD",
        status="pending",
    )

    # Simulate stock reduction
    products_db["prod_000002"].stock_quantity -= 2
    orders_db[new_order.id] = new_order

    print(f"Order {new_order.id} created for customer {new_order.customer_id}")
    print(
        "After order - Bluetooth Speaker stock:",
        products_db["prod_000002"].stock_quantity,
    )

    # Update order status
    new_order.status = "confirmed"
    print(f"Order status updated to: {new_order.status}")


if __name__ == "__main__":
    print("E-commerce MCP Server - Example Usage")
    print("=" * 50)

    # Load sample data
    setup_sample_data()

    # Display current data
    print_sample_data()

    # Demonstrate search functionality
    demonstrate_search()

    # Simulate order workflow
    simulate_order_workflow()

    print("\n" + "=" * 50)
    print("Example completed! Start the MCP server with:")
    print("python ecommerce-mcp-server.py")
