# E-commerce MCP Server Project (Egile Package)

This project is now organized as a proper Python package called `egile`.

## 🚨 **IMPORTANT: Install MCP First!**

The most common issue is missing the MCP (Model Context Protocol) package:

```bash
# Make sure you're in the right environment
conda activate egile

# Install MCP
pip install mcp

# Verify it worked
python check_deps.py
```

**If you get "No module named 'mcp'" errors**, see [INSTALL_MCP.md](INSTALL_MCP.md) for detailed solutions.

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Check if everything is installed correctly
python check_deps.py
```

If you get dependency errors, install the MCP package:
```bash
pip install mcp
```

## Package Structure

```
egile/
├── __init__.py          # Package initialization
├── database.py          # SQLite database manager
├── agent.py            # MCP client agent
├── server_sqlite.py    # SQLite-based MCP server
└── cli.py              # Interactive CLI interface
```

## Running the Components

### **🎯 Recommended (Package-based):**

```bash
# Start MCP Server
python run_server.py
# or: python -m egile.server_sqlite

# Interactive CLI
python run_cli.py  
# or: python -m egile.cli

# Agent Demo
python run_agent_demo.py
# or: python -m egile.agent
```

### **🔧 Development/Testing:**

```bash
# Simple debugging agent
python simple_agent.py

# Low-level MCP testing  
python test_mcp.py
```

### **📦 Legacy (Deprecated):**

```bash
# Original implementations (still work, but use package versions above)
python ecommerce_agent.py           # → Use run_agent_demo.py
python ecommerce_cli.py             # → Use run_cli.py  
python ecommerce-mcp-server-sqlite.py  # → Use run_server.py
```

## Quick Start

**For new users:**
```bash
python run_cli.py
```

**For development:**
```bash
python simple_agent.py  # Test basic communication
python test_mcp.py      # Debug MCP protocol
```

## Troubleshooting

### Server won't start:
```bash
# 1. Check dependencies
python check_deps.py

# 2. Test database functionality 
python test_simple_server.py

# 3. Test MCP communication
python simple_agent.py
```

### Common Issues:
- **"Failed to import MCP modules"**: Install with `pip install mcp`
- **"Connection lost"**: Server crashed on startup, check dependencies
- **"Module not found"**: Make sure you're in the project directory

### Debug Steps:
1. Run `python check_deps.py` first
2. If MCP is missing: `pip install mcp`
3. Test database: `python test_simple_server.py`
4. Test full system: `python simple_agent.py`

### ✅ **Keep These:**
- `simple_agent.py` - Essential debugging tool
- `test_mcp.py` - MCP protocol testing
- `ecommerce_agent.py` - Legacy compatibility testing
- `ecommerce_cli.py` - Alternative CLI implementation

### ⚠️ **Deprecated (but functional):**
- `ecommerce-mcp-server.py` - Use `run_server.py` instead
- `ecommerce-mcp-server-sqlite.py` - Use `run_server.py` instead

### 🎯 **New Primary Tools:**
- `run_server.py` - Start server
- `run_cli.py` - Interactive CLI
- `run_agent_demo.py` - Full demonstration