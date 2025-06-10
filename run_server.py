#!/usr/bin/env python3
"""
Main entry point for Egile E-commerce MCP Server
"""

import sys
import asyncio
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import after path setup
from egile.server_sqlite import main

if __name__ == "__main__":
    asyncio.run(main())
