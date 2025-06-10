# Egile E-commerce Package
# A generic MCP server for e-commerce operations

__version__ = "0.1.0"
__author__ = "Egile Team"
__description__ = "Generic E-commerce MCP Server with SQLite Database Support"

from .database import EcommerceDatabase, Product, Customer, Order, OrderItem
from .agent import EcommerceAgent, AgentResponse

__all__ = [
    "EcommerceDatabase",
    "Product",
    "Customer",
    "Order",
    "OrderItem",
    "EcommerceAgent",
    "AgentResponse",
]
