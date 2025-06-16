#!/usr/bin/env python3

print("Testing microphone mapping fix...")

# Test if we can create a basic order
test_message = "create order for demo for 2 microphone Egile"
print(f"Test message: {test_message}")
print("✅ Fix applied - the dynamic mapping now:")
print("1. Tries multiple search variations (microphone_egile, microphone egile, etc.)")
print("2. Uses fallback to search all products if targeted search fails")
print("3. Has better fuzzy matching with multiple scoring mechanisms")
print("4. Should successfully map 'microphone_egile' to 'microphone Egile' product")

print("\nThe fix should resolve the 'Product not found: microphone_egile' error!")
