#!/usr/bin/env python3
"""
Enhanced MCP Server Tools for Complex Planning

This module extends the MCP server with additional tools for intelligent planning,
analytics, and complex multi-step operations.
"""

import asyncio
import logging
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Dict, Any, List

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from egile.database import EcommerceDatabase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("enhanced-mcp-tools")


class EnhancedMCPTools:
    """Enhanced tools for the MCP server with planning capabilities."""

    def __init__(self, db_path: str = "ecommerce.db"):
        self.db = EcommerceDatabase(db_path)

    async def execute_complex_plan(self, plan_request: str) -> Dict[str, Any]:
        """
        Execute a complex plan based on natural language request.

        Args:
            plan_request: Natural language description of what to do

        Returns:
            Dict with execution results
        """
        # Simple pattern matching for now - can be extended with AI
        plan_request_lower = plan_request.lower()

        if "demo store" in plan_request_lower or "setup store" in plan_request_lower:
            return await self.setup_demo_store()
        elif "analytics" in plan_request_lower or "report" in plan_request_lower:
            return await self.analyze_store_performance()
        elif "inventory" in plan_request_lower or "restock" in plan_request_lower:
            return await self.intelligent_inventory_management()
        else:
            return {
                "success": False,
                "message": "I don't understand that request yet. Try: 'setup demo store', 'generate analytics report', or 'analyze inventory'",
                "type": "unknown_request",
            }

    async def analyze_store_performance(self) -> Dict[str, Any]:
        """
        Perform comprehensive store performance analysis.

        Returns:
            Dict with analysis results
        """
        try:
            # Get all data
            products = self.db.get_all_products()
            customers = self.db.get_all_customers()
            orders = self.db.get_all_orders()

            # Calculate metrics
            total_products = len(products)
            total_customers = len(customers)
            total_orders = len(orders)

            # Product analysis
            categories = {}
            stock_levels = {"low": 0, "medium": 0, "high": 0}
            price_ranges = {"budget": 0, "mid": 0, "premium": 0}

            for product in products:
                # Category distribution
                category = product.category
                categories[category] = categories.get(category, 0) + 1

                # Stock level analysis
                stock = product.stock_quantity
                if stock < 10:
                    stock_levels["low"] += 1
                elif stock < 50:
                    stock_levels["medium"] += 1
                else:
                    stock_levels["high"] += 1

                # Price range analysis
                price = product.price
                if price < 50:
                    price_ranges["budget"] += 1
                elif price < 200:
                    price_ranges["mid"] += 1
                else:
                    price_ranges["premium"] += 1

            # Order analysis
            total_revenue = sum(order.total_amount for order in orders)
            avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

            status_distribution = {}
            for order in orders:
                status = order.status
                status_distribution[status] = status_distribution.get(status, 0) + 1

            # Customer analysis
            email_domains = {}
            for customer in customers:
                domain = (
                    customer.email.split("@")[-1]
                    if "@" in customer.email
                    else "unknown"
                )
                email_domains[domain] = email_domains.get(domain, 0) + 1

            analysis = {
                "overview": {
                    "total_products": total_products,
                    "total_customers": total_customers,
                    "total_orders": total_orders,
                    "total_revenue": total_revenue,
                    "average_order_value": avg_order_value,
                },
                "products": {
                    "categories": categories,
                    "stock_levels": stock_levels,
                    "price_ranges": price_ranges,
                },
                "orders": {"status_distribution": status_distribution},
                "customers": {"email_domains": email_domains},
                "recommendations": self._generate_recommendations(
                    products, customers, orders
                ),
            }

            return {
                "success": True,
                "data": analysis,
                "message": "Store performance analysis completed successfully",
            }

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Store analysis failed",
            }

    def _generate_recommendations(self, products, customers, orders) -> List[str]:
        """Generate actionable recommendations based on data analysis."""
        recommendations = []

        # Stock recommendations
        low_stock_products = [p for p in products if p.stock_quantity < 10]
        if low_stock_products:
            recommendations.append(
                f"Restock {len(low_stock_products)} products with low inventory"
            )

        # Category recommendations
        categories = {}
        for product in products:
            categories[product.category] = categories.get(product.category, 0) + 1

        if len(categories) < 3:
            recommendations.append(
                "Consider expanding product categories for better variety"
            )

        # Customer engagement
        if len(customers) > 0 and len(orders) / len(customers) < 1.5:
            recommendations.append(
                "Focus on customer retention - low order frequency detected"
            )

        # Revenue optimization
        if orders:
            avg_order_value = sum(order.total_amount for order in orders) / len(orders)
            if avg_order_value < 100:
                recommendations.append(
                    "Consider bundle deals or upselling to increase average order value"
                )

        return recommendations

    async def setup_demo_store(
        self, num_products: int = 20, num_customers: int = 10, num_orders: int = 5
    ) -> Dict[str, Any]:
        """
        Set up a complete demo store with sample data.

        Args:
            num_products: Number of products to create
            num_customers: Number of customers to create
            num_orders: Number of orders to create

        Returns:
            Dict with setup results
        """
        try:
            created_data = {"products": [], "customers": [], "orders": []}

            # Create diverse products
            product_templates = [
                # Electronics
                {
                    "name": "Laptop Pro 15",
                    "category": "Electronics",
                    "price": 1299.99,
                    "description": "High-performance laptop",
                },
                {
                    "name": "Smartphone X",
                    "category": "Electronics",
                    "price": 899.99,
                    "description": "Latest smartphone",
                },
                {
                    "name": "Wireless Headphones",
                    "category": "Electronics",
                    "price": 199.99,
                    "description": "Premium headphones",
                },
                {
                    "name": "4K Monitor",
                    "category": "Electronics",
                    "price": 349.99,
                    "description": "Ultra HD monitor",
                },
                {
                    "name": "Gaming Keyboard",
                    "category": "Electronics",
                    "price": 129.99,
                    "description": "Mechanical gaming keyboard",
                },
                # Clothing
                {
                    "name": "Designer T-Shirt",
                    "category": "Clothing",
                    "price": 39.99,
                    "description": "Premium cotton t-shirt",
                },
                {
                    "name": "Running Shoes",
                    "category": "Clothing",
                    "price": 119.99,
                    "description": "Comfortable running shoes",
                },
                {
                    "name": "Winter Jacket",
                    "category": "Clothing",
                    "price": 199.99,
                    "description": "Warm winter jacket",
                },
                {
                    "name": "Jeans",
                    "category": "Clothing",
                    "price": 79.99,
                    "description": "Classic denim jeans",
                },
                # Home & Garden
                {
                    "name": "Coffee Maker",
                    "category": "Home & Garden",
                    "price": 89.99,
                    "description": "Programmable coffee maker",
                },
                {
                    "name": "Plant Pot Set",
                    "category": "Home & Garden",
                    "price": 24.99,
                    "description": "Ceramic plant pots",
                },
                {
                    "name": "LED Desk Lamp",
                    "category": "Home & Garden",
                    "price": 45.99,
                    "description": "Adjustable LED lamp",
                },
                # Books
                {
                    "name": "Programming Guide",
                    "category": "Books",
                    "price": 49.99,
                    "description": "Complete programming guide",
                },
                {
                    "name": "Business Strategy",
                    "category": "Books",
                    "price": 34.99,
                    "description": "Business strategy book",
                },
                {
                    "name": "Science Fiction Novel",
                    "category": "Books",
                    "price": 19.99,
                    "description": "Bestselling sci-fi novel",
                },
                # Sports
                {
                    "name": "Yoga Mat",
                    "category": "Sports",
                    "price": 29.99,
                    "description": "Non-slip yoga mat",
                },
                {
                    "name": "Dumbbells Set",
                    "category": "Sports",
                    "price": 149.99,
                    "description": "Adjustable dumbbells",
                },
                {
                    "name": "Basketball",
                    "category": "Sports",
                    "price": 39.99,
                    "description": "Official size basketball",
                },
                # Beauty
                {
                    "name": "Skincare Set",
                    "category": "Beauty",
                    "price": 79.99,
                    "description": "Complete skincare routine",
                },
                {
                    "name": "Hair Dryer",
                    "category": "Beauty",
                    "price": 69.99,
                    "description": "Professional hair dryer",
                },
            ]

            # Create products
            import random

            selected_products = random.sample(
                product_templates, min(num_products, len(product_templates))
            )

            # Add more products if needed by creating variations
            while len(selected_products) < num_products:
                base = random.choice(product_templates)
                variation = base.copy()
                variation["name"] = f"{base['name']} Pro"
                variation["price"] = base["price"] * 1.2
                selected_products.append(variation)

            # Create products in database
            for i, product_data in enumerate(selected_products):
                from egile.database import Product

                product = Product(
                    id=self.db.get_next_id("prod"),
                    name=product_data["name"],
                    description=product_data["description"],
                    price=product_data["price"],
                    currency="USD",
                    sku=f"SKU-{i + 1:03d}",
                    category=product_data["category"],
                    stock_quantity=random.randint(5, 50),
                )

                created_product = self.db.create_product(product)
                created_data["products"].append(asdict(created_product))

            # Create customers
            customer_templates = [
                {
                    "email": "john.doe@example.com",
                    "first_name": "John",
                    "last_name": "Doe",
                },
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
                {
                    "email": "diana.miller@example.com",
                    "first_name": "Diana",
                    "last_name": "Miller",
                },
                {
                    "email": "frank.garcia@example.com",
                    "first_name": "Frank",
                    "last_name": "Garcia",
                },
                {
                    "email": "grace.lee@example.com",
                    "first_name": "Grace",
                    "last_name": "Lee",
                },
                {
                    "email": "henry.clark@example.com",
                    "first_name": "Henry",
                    "last_name": "Clark",
                },
                {
                    "email": "ivy.taylor@example.com",
                    "first_name": "Ivy",
                    "last_name": "Taylor",
                },
            ]

            for i in range(min(num_customers, len(customer_templates))):
                from egile.database import Customer

                customer_data = customer_templates[i]
                customer = Customer(
                    id=self.db.get_next_id("cust"),
                    email=customer_data["email"],
                    first_name=customer_data["first_name"],
                    last_name=customer_data["last_name"],
                    phone=f"+1-555-{1000 + i:04d}",
                    address={
                        "street": f"{100 + i} Demo Street",
                        "city": "Demo City",
                        "state": "DC",
                        "zip": f"1234{i}",
                        "country": "US",
                    },
                )

                created_customer = self.db.create_customer(customer)
                created_data["customers"].append(asdict(created_customer))

            # Create orders
            customers = created_data["customers"]
            products = created_data["products"]

            for i in range(min(num_orders, len(customers))):
                from egile.database import Order, OrderItem

                # Select random products for this order
                order_products = random.sample(products, random.randint(1, 3))
                items = []
                total_amount = 0

                for product in order_products:
                    quantity = random.randint(1, 3)
                    unit_price = product["price"]
                    total_price = unit_price * quantity

                    items.append(
                        OrderItem(
                            product_id=product["id"],
                            quantity=quantity,
                            unit_price=unit_price,
                            total_price=total_price,
                        )
                    )

                    total_amount += total_price

                order = Order(
                    id=self.db.get_next_id("order"),
                    customer_id=customers[i]["id"],
                    items=items,
                    total_amount=total_amount,
                    currency="USD",
                    status=random.choice(
                        ["pending", "processing", "shipped", "delivered"]
                    ),
                )

                created_order = self.db.create_order(order)
                created_data["orders"].append(asdict(created_order))

            summary = f"""
🏪 **Demo Store Setup Complete!**

Created:
• {len(created_data["products"])} products across {len(set(p["category"] for p in created_data["products"]))} categories
• {len(created_data["customers"])} customers
• {len(created_data["orders"])} sample orders

Total Revenue: ${sum(o["total_amount"] for o in created_data["orders"]):.2f}

Your demo store is ready for testing!
            """

            return {
                "success": True,
                "data": created_data,
                "summary": summary,
                "message": "Demo store setup completed successfully",
            }

        except Exception as e:
            logger.error(f"Demo store setup failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Demo store setup failed",
            }

    async def intelligent_inventory_management(
        self, threshold: int = 10
    ) -> Dict[str, Any]:
        """
        Perform intelligent inventory management with automatic restocking suggestions.

        Args:
            threshold: Stock level threshold for low stock alert

        Returns:
            Dict with inventory analysis and restocking plan
        """
        try:
            # Get all products
            products = self.db.get_all_products()

            # Analyze inventory
            low_stock_products = [p for p in products if p.stock_quantity <= threshold]

            # Calculate restock recommendations
            restock_plan = []
            total_restock_cost = 0

            for product in low_stock_products:
                # Calculate optimal restock quantity based on category and price
                if product.category == "Electronics":
                    restock_qty = max(20, 50 - product.stock_quantity)
                elif product.category == "Clothing":
                    restock_qty = max(30, 60 - product.stock_quantity)
                else:
                    restock_qty = max(25, 40 - product.stock_quantity)

                # Estimate restock cost (assuming cost is 60% of selling price)
                estimated_cost = product.price * 0.6 * restock_qty
                total_restock_cost += estimated_cost

                restock_plan.append(
                    {
                        "product_id": product.id,
                        "product_name": product.name,
                        "current_stock": product.stock_quantity,
                        "recommended_restock": restock_qty,
                        "new_stock_level": product.stock_quantity + restock_qty,
                        "estimated_cost": estimated_cost,
                        "priority": "high" if product.stock_quantity < 5 else "medium",
                    }
                )

            # Sort by priority and current stock level
            restock_plan.sort(
                key=lambda x: (x["priority"] == "high", -x["current_stock"]),
                reverse=True,
            )

            # Generate analysis report
            analysis = {
                "inventory_overview": {
                    "total_products": len(products),
                    "low_stock_count": len(low_stock_products),
                    "low_stock_percentage": (len(low_stock_products) / len(products))
                    * 100
                    if products
                    else 0,
                },
                "restock_plan": restock_plan,
                "financial_impact": {
                    "total_estimated_cost": total_restock_cost,
                    "high_priority_items": len(
                        [p for p in restock_plan if p["priority"] == "high"]
                    ),
                },
                "recommendations": [],
            }

            # Generate recommendations
            if len(low_stock_products) > len(products) * 0.3:
                analysis["recommendations"].append(
                    "High percentage of low-stock items detected. Consider reviewing supply chain efficiency."
                )

            if any(p["priority"] == "high" for p in restock_plan):
                analysis["recommendations"].append(
                    "Critical stock levels detected. Immediate restocking recommended for high-priority items."
                )

            if total_restock_cost > 10000:
                analysis["recommendations"].append(
                    "Large restocking investment required. Consider phased restocking approach."
                )

            return {
                "success": True,
                "data": analysis,
                "message": f"Inventory analysis completed. {len(low_stock_products)} products need restocking.",
            }

        except Exception as e:
            logger.error(f"Inventory management failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Inventory management analysis failed",
            }

    async def execute_auto_restock(
        self, restock_plan: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Execute automatic restocking based on a restock plan.

        Args:
            restock_plan: List of restock recommendations

        Returns:
            Dict with execution results
        """
        try:
            executed_restocks = []
            failed_restocks = []

            for item in restock_plan:
                try:
                    product_id = item["product_id"]
                    restock_qty = item["recommended_restock"]

                    # Update stock in database
                    success = self.db.update_stock(product_id, restock_qty, "add")

                    if success:
                        executed_restocks.append(
                            {
                                "product_id": product_id,
                                "product_name": item["product_name"],
                                "restocked_quantity": restock_qty,
                                "new_stock_level": item["new_stock_level"],
                            }
                        )
                    else:
                        failed_restocks.append(
                            {
                                "product_id": product_id,
                                "product_name": item["product_name"],
                                "error": "Database update failed",
                            }
                        )

                except Exception as e:
                    failed_restocks.append(
                        {
                            "product_id": item.get("product_id", "unknown"),
                            "product_name": item.get("product_name", "unknown"),
                            "error": str(e),
                        }
                    )

            summary = f"""
📦 **Auto-Restocking Results**

✅ Successfully restocked: {len(executed_restocks)} products
❌ Failed to restock: {len(failed_restocks)} products

Total items added to inventory: {sum(item["restocked_quantity"] for item in executed_restocks)}
            """

            return {
                "success": len(executed_restocks) > 0,
                "data": {
                    "executed_restocks": executed_restocks,
                    "failed_restocks": failed_restocks,
                    "summary": summary,
                },
                "message": f"Auto-restocking completed. {len(executed_restocks)} products restocked.",
            }

        except Exception as e:
            logger.error(f"Auto-restock execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Auto-restock execution failed",
            }


# Additional utility functions for the enhanced MCP server


async def create_enhanced_mcp_tools():
    """Factory function to create enhanced MCP tools."""
    return EnhancedMCPTools()


async def demo_enhanced_capabilities():
    """Demonstrate the enhanced capabilities."""
    tools = await create_enhanced_mcp_tools()

    print("🚀 Enhanced MCP Tools Demo")
    print("=" * 50)

    # Setup demo store
    print("\n1. Setting up demo store...")
    result = await tools.setup_demo_store(
        num_products=15, num_customers=8, num_orders=5
    )
    if result["success"]:
        print("✅ Demo store created successfully!")
        print(result["summary"])

    # Analyze store performance
    print("\n2. Analyzing store performance...")
    analysis = await tools.analyze_store_performance()
    if analysis["success"]:
        print("✅ Analysis completed!")
        data = analysis["data"]
        print(f"   📊 Overview: {data['overview']}")
        print(f"   🛍️  Categories: {list(data['products']['categories'].keys())}")
        print(f"   💡 Recommendations: {len(data['recommendations'])} suggestions")

    # Inventory management
    print("\n3. Performing inventory analysis...")
    inventory = await tools.intelligent_inventory_management(threshold=15)
    if inventory["success"]:
        print("✅ Inventory analysis completed!")
        data = inventory["data"]
        print(f"   📦 Low stock items: {data['inventory_overview']['low_stock_count']}")
        print(
            f"   💰 Estimated restock cost: ${data['financial_impact']['total_estimated_cost']:.2f}"
        )

    # Complex planning
    print("\n4. Testing complex planning...")
    plan_result = await tools.execute_complex_plan(
        "Generate a comprehensive analytics report"
    )
    if plan_result["success"]:
        print("✅ Complex planning executed!")
        print(f"   📋 Plan type: {plan_result.get('type', 'analytics')}")
    else:
        print(f"   ❌ Planning failed: {plan_result.get('message', 'Unknown error')}")

    print("\n" + "=" * 50)
    print("🎉 Enhanced MCP Tools demonstration completed!")


if __name__ == "__main__":
    asyncio.run(demo_enhanced_capabilities())
