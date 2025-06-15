#!/usr/bin/env python3
import sys

sys.path.append(".")

from egile.database import EcommerceDatabase, Product

# Test the EcommerceDatabase class
try:
    print("Testing EcommerceDatabase...")
    db = EcommerceDatabase("/home/jbp/projects/egile/ecommerce.db")

    print("Calling get_all_products()...")
    products = db.get_all_products()

    print(f"Number of products returned: {len(products)}")

    if products:
        product = products[0]
        print(f"First product type: {type(product)}")
        print(f"First product: {product}")
        print(f"Product name: {product.name}")
        print(f"Product SKU: {product.sku}")
        print(f"Product price: {product.price}")
        print(f"Product stock: {product.stock_quantity}")

    # Test customers too
    print("\nTesting customers...")
    customers = db.get_all_customers()
    print(f"Number of customers returned: {len(customers)}")

    if customers:
        customer = customers[0]
        print(f"First customer type: {type(customer)}")
        print(f"First customer: {customer}")
        print(f"Customer first name: {customer.first_name}")
        print(f"Customer last name: {customer.last_name}")
        print(f"Customer email: {customer.email}")

except Exception as e:
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()
