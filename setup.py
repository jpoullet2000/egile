#!/usr/bin/env python3
"""
Setup script for Egile E-commerce MCP Server

This script helps install dependencies and set up the environment.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} failed")
            print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False


def install_mcp():
    """Try different methods to install MCP."""
    print("🚀 Installing MCP (Model Context Protocol)...")

    # Try different package names
    mcp_packages = ["mcp", "model-context-protocol", "mcp-server", "anthropic-mcp"]

    for package in mcp_packages:
        print(f"\n🔍 Trying to install {package}...")
        if run_command(
            f"{sys.executable} -m pip install {package}", f"Installing {package}"
        ):
            # Test if it worked
            try:
                import mcp.types

                print(f"✅ Successfully installed {package}!")
                return True
            except ImportError:
                print(f"⚠️  {package} installed but mcp.types not available")
                continue

    return False


def install_from_git():
    """Try installing MCP from git if PyPI versions don't work."""
    print("\n🔍 Trying to install MCP from git repository...")

    git_urls = [
        "https://github.com/modelcontextprotocol/python-sdk.git",
        "https://github.com/anthropics/mcp.git",
    ]

    for url in git_urls:
        if run_command(
            f"{sys.executable} -m pip install git+{url}", f"Installing from {url}"
        ):
            try:
                import mcp.types

                print("✅ Successfully installed MCP from git!")
                return True
            except ImportError:
                continue

    return False


def create_requirements_file():
    """Create a requirements.txt file."""
    requirements_content = """# Model Context Protocol (MCP) - Core dependency
# Note: Install manually if this doesn't work:
# pip install mcp

# SQLite3 is included with Python standard library

# For development/testing (optional)
# pytest>=7.0.0
# black>=22.0.0
# isort>=5.0.0
"""

    requirements_path = Path("requirements.txt")
    with open(requirements_path, "w") as f:
        f.write(requirements_content)
    print(f"✅ Created {requirements_path}")


def main():
    """Main setup function."""
    print("🎯 Egile E-commerce MCP Server Setup")
    print("=" * 50)

    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 8):
        print(f"❌ Python {python_version.major}.{python_version.minor} detected")
        print("   Python 3.8+ is required")
        return False

    print(
        f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}"
    )

    # Create requirements file
    create_requirements_file()

    # Check if MCP is already installed
    try:
        import mcp.types

        print("✅ MCP is already installed and working!")
    except ImportError:
        print("📦 MCP not found, attempting installation...")

        # Try standard installation
        if not install_mcp():
            print("\n🔧 Standard installation failed, trying git...")
            if not install_from_git():
                print("\n❌ All MCP installation methods failed!")
                print("\n🔍 Manual installation options:")
                print("   1. pip install mcp")
                print("   2. pip install model-context-protocol")
                print("   3. Check if MCP is available in your environment")
                print("   4. Visit: https://github.com/modelcontextprotocol/python-sdk")
                return False

    # Test the installation
    print("\n🧪 Testing installation...")
    if run_command(f"{sys.executable} check_deps.py", "Checking dependencies"):
        print("\n🎉 Setup completed successfully!")
        print("\n🚀 You can now run:")
        print("   python run_server.py    # Start the MCP server")
        print("   python run_cli.py       # Interactive CLI")
        print("   python run_agent_demo.py # Full demonstration")
        return True
    else:
        print("\n❌ Setup verification failed")
        return False


if __name__ == "__main__":
    success = main()
    if not success:
        print("\n💡 If installation continues to fail, you can:")
        print("   1. Run the server without MCP: python test_simple_server.py")
        print("   2. Check your Python environment")
        print("   3. Try creating a new virtual environment")
    sys.exit(0 if success else 1)
