#!/usr/bin/env python3
"""
Check if all required dependencies are installed
"""

import sys
import importlib.util


def check_dependency(module_name, install_command=None):
    """Check if a module can be imported."""
    spec = importlib.util.find_spec(module_name)
    if spec is not None:
        print(f"✅ {module_name} is installed")
        return True
    else:
        print(f"❌ {module_name} is NOT installed")
        if install_command:
            print(f"   Install with: {install_command}")
        return False


def main():
    """Check all dependencies."""
    print("Checking dependencies for Egile E-commerce MCP Server...")
    print("=" * 60)

    all_good = True

    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 8):
        print(
            f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}"
        )
    else:
        print(f"❌ Python {python_version.major}.{python_version.minor} (need 3.8+)")
        all_good = False

    # Check standard library modules
    stdlib_modules = ["sqlite3", "asyncio", "json", "logging", "dataclasses"]

    for module in stdlib_modules:
        if not check_dependency(module):
            all_good = False

    # Check third-party dependencies
    third_party = [
        ("mcp", "pip install mcp"),
        ("mcp.types", None),
        ("mcp.server", None),
    ]

    for module, install_cmd in third_party:
        if not check_dependency(module, install_cmd):
            all_good = False

    print("=" * 60)

    if all_good:
        print("🎉 All dependencies are installed!")
        print("You can now run:")
        print("  python run_server.py")
        print("  python run_cli.py")
        print("  python run_agent_demo.py")
    else:
        print("❌ Some dependencies are missing.")
        print("Install missing dependencies with:")
        print("  pip install -r requirements.txt")

    return all_good


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
