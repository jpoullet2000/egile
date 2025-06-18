#!/usr/bin/env python3
"""
Simple test for JSON parsing improvements
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from egile.smart_agent import robust_json_parse


def test_robust_json_parse():
    """Test the robust JSON parsing function."""
    print("=== Testing robust_json_parse ===")

    # Test cases that were problematic
    test_cases = [
        ("", "empty_string"),
        ("0", "number_as_string"),
        ('{"name": "pen"}', "valid_json"),
        ("{'name': 'pen'}", "single_quotes"),
        ("{name: 'pen'}", "unquoted_keys"),
        ('prod_000001", "name": "Test Product"', "malformed_start"),
        ('{"invalid": }', "invalid_json"),
        (None, "none_value"),
        ([], "empty_list"),
        ({}, "empty_dict"),
    ]

    for test_input, description in test_cases:
        try:
            result = robust_json_parse(test_input, description)
            print(f"✓ {description}: {test_input} -> {result}")
        except Exception as e:
            print(f"✗ {description}: {test_input} -> ERROR: {e}")

    print("\n=== Test completed ===")


if __name__ == "__main__":
    test_robust_json_parse()
