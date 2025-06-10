# Egile E-commerce MCP Server

A complete Model Context Protocol (MCP) server for e-commerce operations, packaged as the `egile` Python package. This system provides tools and resources for managing products, customers, orders, and inventory with persistent SQLite storage.

## 🚀 Quick Start

### Installation
```bash
# 1. Install MCP dependency
pip install mcp

# 2. Verify installation
python check_deps.py

# 3. Start the interactive CLI
python run_cli.py
```

### Basic Usage
```bash
# In the CLI:
ecommerce> demo                    # Run demonstration
ecommerce> help                    # Show all commands
ecommerce> create product "Widget" 29.99 WID-001 Electronics 50
ecommerce> list products           # Show all products
ecommerce> quit                    # Exit CLI
```

## 📦 Package Structure

The system is organized as the `egile` package:

```
egile/
├── __init__.py          # Package exports
├── database.py          # SQLite database layer
├── agent.py            # MCP client agent
├── server_sqlite.py    # MCP server with SQLite
└── cli.py              # Interactive CLI interface
```

## 🎯 Complete Step-by-Step Guide

### Step 1: Start the CLI
```bash
python run_cli.py
```

### Step 2: Create Products
```bash
# Syntax: create product "<name>" <price> <sku> <category> <stock>
ecommerce> create product "Wireless Mouse" 29.99 MOUSE-001 Electronics 25
ecommerce> create product "USB-C Cable" 12.99 USB-001 Accessories 100
ecommerce> create product "Bluetooth Speaker" 89.99 SPEAKER-001 Electronics 15
```

### Step 3: Create Customers
```bash
# Syntax: create customer <email> "<first_name>" "<last_name>" [phone]
ecommerce> create customer john@example.com "John" "Doe" "+1-555-0123"
ecommerce> create customer jane@example.com "Jane" "Smith"
ecommerce> create customer alice@example.com "Alice" "Johnson" "+1-555-0456"
```

### Step 4: View Your Data
```bash
# List all products
ecommerce> list products

# List all customers  
ecommerce> list customers

# Get specific items
ecommerce> get product MOUSE-001
ecommerce> get customer john@example.com
```

### Step 5: Create Orders
```bash
# Get the customer and product IDs first (from the list/get commands above)
# Syntax: order create <customer_id> <product_id> <quantity>
ecommerce> order create cust_000001 prod_000001 2
ecommerce> order create cust_000002 prod_000003 1
```

### Step 6: Manage Inventory
```bash
# Check low stock
ecommerce> stock low 20

# Update stock
ecommerce> stock update prod_000001 50

# Restock low inventory items
ecommerce> stock restock 25
```

### Step 7: Search and Filter
```bash
# Search products
ecommerce> search products wireless

# View all orders
ecommerce> list orders

# Get order details
ecommerce> order get order_000001
```

## 🔧 CLI Command Reference

### Product Commands
- `create product "<name>" <price> <sku> <category> <stock>` - Create new product
- `get product <id_or_sku>` - Get product details
- `search products <query>` - Search products by name/description
- `list products` - Show all products

### Customer Commands
- `create customer <email> "<first>" "<last>" [phone]` - Create customer
- `get customer <id_or_email>` - Get customer details
- `list customers` - Show all customers

### Order Commands
- `order create <customer_id> <product_id> <quantity>` - Create order
- `order get <order_id>` - Get order details
- `order status <order_id> <status>` - Update order status
- `list orders` - Show all orders

### Inventory Commands
- `stock update <product_id> <quantity>` - Set stock level
- `stock low [threshold]` - Show low stock products (default: 10)
- `stock restock [quantity]` - Restock all low items (default: 50)

### Utility Commands
- `demo` - Run demonstration with sample data
- `help` - Show all available commands
- `quit` - Exit the CLI

## 💡 Pro Tips

1. **Use the demo first**: Run `demo` to see sample data creation
2. **Copy IDs**: Note the generated IDs (like `prod_000001`) for creating orders
3. **Check stock before orders**: Use `list products` to see available quantities
4. **Use SKUs for products**: You can reference products by SKU instead of ID
5. **Use emails for customers**: You can reference customers by email instead of ID

### 2. Using the Agent API (Programmatic)

```python
from egile import EcommerceAgent

async def create_sample_data():
    agent = EcommerceAgent()
    await agent.start_server()
    
    # Create a product
    product = await agent.create_product(
        name="Laptop Pro",
        description="High-performance laptop", 
        price=1299.99,
        sku="LAPTOP-001",
        category="Electronics",
        stock_quantity=10
    )
    
    # Create a customer
    customer = await agent.create_customer(
        email="customer@example.com",
        first_name="Alice",
        last_name="Johnson",
        phone="+1-555-0199"
    )
    
    # Create an order
    order = await agent.create_order(
        customer_id="cust_000001",
        items=[{"product_id": "prod_000001", "quantity": 1}]
    )
    
    await agent.stop_server()
```

### 3. Direct Database Access (For Testing)

```python
from egile.database import EcommerceDatabase, Product, Customer

db = EcommerceDatabase()

# Create product directly
product = Product(
    id="prod_test",
    name="Test Product",
    description="A test product",
    price=19.99,
    sku="TEST-001", 
    category="Test",
    stock_quantity=5
)
db.create_product(product)
```

## Available Tools

### Product Tools
- `create_product` - Add new products to catalog
- `get_product` - Retrieve product by ID or SKU
- `update_product` - Modify product information
- `search_products` - Search and filter products

### Customer Tools
- `create_customer` - Add new customers
- `get_customer` - Retrieve customer by ID or email

### Order Tools
- `create_order` - Create new orders
- `get_order` - Retrieve order details
- `update_order_status` - Change order status

### Inventory Tools
- `update_stock` - Modify product stock levels
- `get_low_stock_products` - Find products with low inventory

## Resources

The server provides three main resources:
- `ecommerce://products` - Product catalog data
- `ecommerce://customers` - Customer database
- `ecommerce://orders` - Order management data

## Data Models

### Product
```json
{
  "id": "prod_000001",
  "name": "Product Name",
  "description": "Product description",
  "price": 29.99,
  "currency": "USD",
  "sku": "SKU-001",
  "category": "Electronics",
  "stock_quantity": 100,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

### Customer
```json
{
  "id": "cust_000001",
  "email": "customer@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "address": {
    "street": "123 Main St",
    "city": "Anytown",
    "state": "ST",
    "zip": "12345",
    "country": "US"
  },
  "created_at": "2024-01-01T00:00:00"
}
```

### Order
```json
{
  "id": "order_000001",
  "customer_id": "cust_000001",
  "items": [
    {
      "product_id": "prod_000001",
      "quantity": 2,
      "unit_price": 29.99,
      "total_price": 59.98
    }
  ],
  "total_amount": 59.98,
  "currency": "USD",
  "status": "pending",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

## Usage Examples

### Creating a Product
```python
# Tool call: create_product
{
  "name": "Wireless Headphones",
  "description": "High-quality wireless headphones with noise cancellation",
  "price": 199.99,
  "currency": "USD",
  "sku": "WH-001",
  "category": "Electronics",
  "stock_quantity": 50
}
```

### Creating an Order
```python
# Tool call: create_order
{
  "customer_id": "cust_000001",
  "items": [
    {"product_id": "prod_000001", "quantity": 2},
    {"product_id": "prod_000002", "quantity": 1}
  ],
  "currency": "USD"
}
```

### Searching Products
```python
# Tool call: search_products
{
  "query": "wireless",
  "category": "Electronics",
  "min_price": 50,
  "max_price": 300,
  "in_stock_only": true
}
```

## Extensibility

This MCP server is designed to be generic and extensible. You can:

1. **Add custom fields** to the data models
2. **Implement database persistence** (currently uses in-memory storage)
3. **Add payment processing** tools
4. **Integrate with external APIs** (shipping, tax calculation, etc.)
5. **Add authentication and authorization**
6. **Implement caching and performance optimizations**

## Integration

To integrate this MCP server with your e-commerce application:

1. Configure your MCP client to connect to this server
2. Use the provided tools in your application logic
3. Access the resources to display data in your UI
4. Extend the server with custom tools for your specific needs

## License

MIT License - feel free to use and modify for your e-commerce projects.