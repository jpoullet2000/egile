#!/usr/bin/env python3
"""
Debug server startup issues
"""

import sys
import subprocess
import asyncio
from pathlib import Path


async def test_server_startup():
    """Test if the server can start."""
    print("Testing server startup...")

    # Test 1: Check if MCP is installed
    try:
        import mcp.types

        print("✅ MCP package is available")
    except ImportError as e:
        print(f"❌ MCP package not found: {e}")
        print("Install with: pip install mcp")
        return

    # Test 2: Check if database module can be imported
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from egile.database import EcommerceDatabase

        print("✅ Database module can be imported")
    except ImportError as e:
        print(f"❌ Database import failed: {e}")
        return

    # Test 3: Try to create database
    try:
        db = EcommerceDatabase("test_ecommerce.db")
        print("✅ Database can be created")
    except Exception as e:
        print(f"❌ Database creation failed: {e}")
        return

    # Test 4: Try to start server process
    server_path = Path(__file__).parent / "egile" / "server_sqlite.py"
    print(f"Testing server at: {server_path}")

    try:
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            str(server_path),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        # Wait a moment to see if it crashes immediately
        await asyncio.sleep(1)

        if process.returncode is None:
            print("✅ Server process started successfully")
            process.terminate()
            await process.wait()
        else:
            print(f"❌ Server process exited with code: {process.returncode}")
            stderr = await process.stderr.read()
            print(f"Error output: {stderr.decode()}")

    except Exception as e:
        print(f"❌ Failed to start server process: {e}")


if __name__ == "__main__":
    asyncio.run(test_server_startup())
