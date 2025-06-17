#!/usr/bin/env python3
"""
Test customer help patterns in isolation
"""


def test_customer_help_patterns():
    """Test if customer help patterns are being detected correctly"""

    # These are the patterns from the agent
    customer_help_patterns = [
        "how to create a customer",
        "how do I create a customer",
        "help me create a customer",
        "how to add a customer",
        "how do I add a customer",
        "help me add a customer",
        "customer creation help",
        "how to create customer",
        "how do I make a customer",
        "help with customer creation",
    ]

    test_messages = [
        "how to create a customer",
        "help me create a customer",
        "how do I add a customer",
        "customer creation help",
        "how to create customer",
        "how do I create a customer",
    ]

    print("🔍 Testing customer help pattern detection:")
    print("=" * 50)

    for message in test_messages:
        message_lower = message.lower()

        # Check if any pattern matches
        matched = any(pattern in message_lower for pattern in customer_help_patterns)

        print(f"Message: '{message}' (lower: '{message_lower}')")
        print(f"Matched: {'✅ YES' if matched else '❌ NO'}")

        if matched:
            # Find which pattern matched
            for pattern in customer_help_patterns:
                if pattern in message_lower:
                    print(f"  Matched pattern: '{pattern}'")
                    break
        else:
            # Debug which patterns were checked
            print("  Checked patterns:")
            for pattern in customer_help_patterns:
                in_message = pattern in message_lower
                print(f"    '{pattern}' in '{message_lower}': {in_message}")
        print()


if __name__ == "__main__":
    test_customer_help_patterns()
