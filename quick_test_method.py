#!/usr/bin/env python3
"""
Quick test to check if post_process_product_list method exists
"""

import sys
import os

sys.path.append("/home/jbp/projects/egile/chatbot-agent")

try:
    from grok_agent import GrokEcommerceAgent

    agent = GrokEcommerceAgent()

    print("✅ Agent created successfully")
    print(
        f"Has post_process_product_list: {hasattr(agent, 'post_process_product_list')}"
    )

    if hasattr(agent, "post_process_product_list"):
        method = getattr(agent, "post_process_product_list")
        print(f"Method type: {type(method)}")
        print(f"Method callable: {callable(method)}")

    # List all methods starting with 'post'
    post_methods = [m for m in dir(agent) if m.startswith("post")]
    print(f"Methods starting with 'post': {post_methods}")

    # List all methods
    all_methods = [m for m in dir(agent) if not m.startswith("_")]
    print(f"All public methods: {all_methods}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
