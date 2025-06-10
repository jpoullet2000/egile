# MCP Installation Guide

## Quick Fix

The error shows that the `mcp` package is not installed. Here are the steps to fix it:

### 1. Install MCP Package

Try these commands in order until one works:

```bash
# First, make sure you're in the right environment
conda activate egile

# Try the standard MCP package
pip install mcp

# If that doesn't work, try these alternatives:
pip install model-context-protocol
pip install mcp-server
pip install anthropic-mcp
```

### 2. Verify Installation

```bash
python check_deps.py
```

### 3. Test the System

```bash
# Test database functionality (works without MCP)
python test_simple_server.py

# Test full system (requires MCP)
python run_cli.py
```

## Alternative: Use Without MCP

If MCP installation continues to fail, you can test the database layer directly:

```bash
python test_simple_server.py
```

This will verify that the SQLite database and core functionality work correctly.

## Troubleshooting

### Environment Issues
```bash
# Check which Python you're using
which python
python --version

# Check if you're in the right environment
conda info --envs
```

### Virtual Environment
If problems persist, try creating a fresh environment:

```bash
conda create -n egile-new python=3.11
conda activate egile-new
pip install mcp
```

### Manual MCP Installation

If pip doesn't work, try installing from source:

```bash
# Clone the MCP Python SDK
git clone https://github.com/modelcontextprotocol/python-sdk.git
cd python-sdk
pip install -e .
```

## Next Steps

Once MCP is installed:

1. **Start the server**: `python run_server.py`
2. **Use the CLI**: `python run_cli.py`
3. **Run demos**: `python run_agent_demo.py`

The key is getting the `mcp` package installed in your `egile` conda environment!