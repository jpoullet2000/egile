#!/usr/bin/env python3
"""
Database manager for E-commerce MCP Server using SQLite

This module handles all database operations for products, customers, and orders.
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger("ecommerce-database")


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


class EcommerceDatabase:
    """SQLite database manager for e-commerce data."""

    def __init__(self, db_path: str = "ecommerce.db"):
        """Initialize the database connection and create tables."""
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Create database tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                currency TEXT DEFAULT 'USD',
                sku TEXT UNIQUE NOT NULL,
                category TEXT,
                stock_quantity INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at TEXT,
                updated_at TEXT
            )
        """)

        # Customers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                phone TEXT,
                address TEXT,  -- JSON string
                created_at TEXT
            )
        """)

        # Orders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                total_amount REAL NOT NULL,
                currency TEXT DEFAULT 'USD',
                status TEXT DEFAULT 'pending',
                created_at TEXT,
                updated_at TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            )
        """)

        # Order items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT NOT NULL,
                product_id TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                total_price REAL NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        """)

        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id)"
        )

        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")

    def get_connection(self):
        """Get a database connection."""
        return sqlite3.connect(self.db_path)

    # Product methods
    def create_product(self, product: Product) -> Product:
        """Create a new product."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO products 
                (id, name, description, price, currency, sku, category, stock_quantity, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    product.id,
                    product.name,
                    product.description,
                    product.price,
                    product.currency,
                    product.sku,
                    product.category,
                    product.stock_quantity,
                    product.is_active,
                    product.created_at,
                    product.updated_at,
                ),
            )
            conn.commit()
            return product
        finally:
            conn.close()

    def get_product(self, product_id: str) -> Optional[Product]:
        """Get product by ID."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
            row = cursor.fetchone()
            if row:
                return Product(*row)
            return None
        finally:
            conn.close()

    def get_product_by_sku(self, sku: str) -> Optional[Product]:
        """Get product by SKU."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM products WHERE sku = ?", (sku,))
            row = cursor.fetchone()
            if row:
                return Product(*row)
            return None
        finally:
            conn.close()

    def update_product(self, product_id: str, updates: Dict[str, Any]) -> bool:
        """Update product fields."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Add updated_at timestamp
            updates["updated_at"] = datetime.now().isoformat()

            # Build dynamic update query
            set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
            values = list(updates.values()) + [product_id]

            cursor.execute(f"UPDATE products SET {set_clause} WHERE id = ?", values)
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def search_products(
        self,
        query: str = None,
        category: str = None,
        min_price: float = None,
        max_price: float = None,
        in_stock_only: bool = False,
    ) -> List[Product]:
        """Search products with filters."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            sql = "SELECT * FROM products WHERE 1=1"
            params = []

            if query:
                sql += " AND (name LIKE ? OR description LIKE ?)"
                params.extend([f"%{query}%", f"%{query}%"])

            if category:
                sql += " AND category = ?"
                params.append(category)

            if min_price is not None:
                sql += " AND price >= ?"
                params.append(min_price)

            if max_price is not None:
                sql += " AND price <= ?"
                params.append(max_price)

            if in_stock_only:
                sql += " AND stock_quantity > 0"

            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [Product(*row) for row in rows]
        finally:
            conn.close()

    def get_all_products(self) -> List[Product]:
        """Get all products."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM products ORDER BY created_at DESC")
            rows = cursor.fetchall()
            return [Product(*row) for row in rows]
        finally:
            conn.close()

    def update_stock(
        self, product_id: str, quantity: int, operation: str = "set"
    ) -> bool:
        """Update product stock."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            if operation == "set":
                cursor.execute(
                    """
                    UPDATE products 
                    SET stock_quantity = ?, updated_at = ?
                    WHERE id = ?
                """,
                    (quantity, datetime.now().isoformat(), product_id),
                )
            elif operation == "add":
                cursor.execute(
                    """
                    UPDATE products 
                    SET stock_quantity = stock_quantity + ?, updated_at = ?
                    WHERE id = ?
                """,
                    (quantity, datetime.now().isoformat(), product_id),
                )
            elif operation == "subtract":
                cursor.execute(
                    """
                    UPDATE products 
                    SET stock_quantity = MAX(0, stock_quantity - ?), updated_at = ?
                    WHERE id = ?
                """,
                    (quantity, datetime.now().isoformat(), product_id),
                )

            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def get_low_stock_products(self, threshold: int = 10) -> List[Product]:
        """Get products with low stock."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT * FROM products WHERE stock_quantity <= ? ORDER BY stock_quantity ASC",
                (threshold,),
            )
            rows = cursor.fetchall()
            return [Product(*row) for row in rows]
        finally:
            conn.close()

    # Customer methods
    def create_customer(self, customer: Customer) -> Customer:
        """Create a new customer."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            address_json = json.dumps(customer.address) if customer.address else None
            cursor.execute(
                """
                INSERT INTO customers 
                (id, email, first_name, last_name, phone, address, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    customer.id,
                    customer.email,
                    customer.first_name,
                    customer.last_name,
                    customer.phone,
                    address_json,
                    customer.created_at,
                ),
            )
            conn.commit()
            return customer
        finally:
            conn.close()

    def get_customer(self, customer_id: str) -> Optional[Customer]:
        """Get customer by ID."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
            row = cursor.fetchone()
            if row:
                # Parse address JSON
                address = json.loads(row[5]) if row[5] else None
                return Customer(row[0], row[1], row[2], row[3], row[4], address, row[6])
            return None
        finally:
            conn.close()

    def get_customer_by_email(self, email: str) -> Optional[Customer]:
        """Get customer by email."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM customers WHERE email = ?", (email,))
            row = cursor.fetchone()
            if row:
                # Parse address JSON
                address = json.loads(row[5]) if row[5] else None
                return Customer(row[0], row[1], row[2], row[3], row[4], address, row[6])
            return None
        finally:
            conn.close()

    def get_all_customers(self) -> List[Customer]:
        """Get all customers."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM customers ORDER BY created_at DESC")
            rows = cursor.fetchall()
            customers = []
            for row in rows:
                address = json.loads(row[5]) if row[5] else None
                customers.append(
                    Customer(row[0], row[1], row[2], row[3], row[4], address, row[6])
                )
            return customers
        finally:
            conn.close()

    # Order methods
    def create_order(self, order: Order) -> Order:
        """Create a new order with items."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Insert order
            cursor.execute(
                """
                INSERT INTO orders 
                (id, customer_id, total_amount, currency, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    order.id,
                    order.customer_id,
                    order.total_amount,
                    order.currency,
                    order.status,
                    order.created_at,
                    order.updated_at,
                ),
            )

            # Insert order items
            for item in order.items:
                cursor.execute(
                    """
                    INSERT INTO order_items 
                    (order_id, product_id, quantity, unit_price, total_price)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        order.id,
                        item.product_id,
                        item.quantity,
                        item.unit_price,
                        item.total_price,
                    ),
                )

            conn.commit()
            return order
        finally:
            conn.close()

    def get_order(self, order_id: str) -> Optional[Order]:
        """Get order by ID with items."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Get order
            cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
            order_row = cursor.fetchone()
            if not order_row:
                return None

            # Get order items
            cursor.execute(
                "SELECT product_id, quantity, unit_price, total_price FROM order_items WHERE order_id = ?",
                (order_id,),
            )
            item_rows = cursor.fetchall()

            items = [OrderItem(row[0], row[1], row[2], row[3]) for row in item_rows]

            return Order(
                order_row[0],
                order_row[1],
                items,
                order_row[2],
                order_row[3],
                order_row[4],
                order_row[5],
                order_row[6],
            )
        finally:
            conn.close()

    def update_order_status(self, order_id: str, status: str) -> bool:
        """Update order status."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                UPDATE orders 
                SET status = ?, updated_at = ?
                WHERE id = ?
            """,
                (status, datetime.now().isoformat(), order_id),
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def get_all_orders(self) -> List[Order]:
        """Get all orders with items."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM orders ORDER BY created_at DESC")
            order_rows = cursor.fetchall()

            orders = []
            for order_row in order_rows:
                # Get items for this order
                cursor.execute(
                    "SELECT product_id, quantity, unit_price, total_price FROM order_items WHERE order_id = ?",
                    (order_row[0],),
                )
                item_rows = cursor.fetchall()
                items = [OrderItem(row[0], row[1], row[2], row[3]) for row in item_rows]

                orders.append(
                    Order(
                        order_row[0],
                        order_row[1],
                        items,
                        order_row[2],
                        order_row[3],
                        order_row[4],
                        order_row[5],
                        order_row[6],
                    )
                )

            return orders
        finally:
            conn.close()

    def get_next_id(self, prefix: str) -> str:
        """Generate next ID for entities."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            if prefix == "prod":
                cursor.execute("SELECT COUNT(*) FROM products")
            elif prefix == "cust":
                cursor.execute("SELECT COUNT(*) FROM customers")
            elif prefix == "order":
                cursor.execute("SELECT COUNT(*) FROM orders")
            else:
                return f"{prefix}_000001"

            count = cursor.fetchone()[0]
            return f"{prefix}_{count + 1:06d}"
        finally:
            conn.close()
