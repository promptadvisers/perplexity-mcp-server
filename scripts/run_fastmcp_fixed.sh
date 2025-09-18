#!/bin/bash

# Perplexity FastMCP Server Runner Script (Fixed for Claude Desktop)
# All diagnostic output goes to stderr, only JSON-RPC goes to stdout

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the script directory
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "mcp_venv" ]; then
    # Create virtual environment silently
    python3 -m venv mcp_venv >&2
fi

# Activate virtual environment
source mcp_venv/bin/activate

# Install dependencies if needed (silently)
pip install -q -r requirements_fastmcp.txt >&2 2>/dev/null || true

# Check for API key
if [ -z "$PERPLEXITY_API_KEY" ]; then
    # Try to load from .env file
    if [ -f ".env" ]; then
        export $(cat .env | grep PERPLEXITY_API_KEY | xargs)
    fi
fi

if [ -z "$PERPLEXITY_API_KEY" ]; then
    echo "ERROR: PERPLEXITY_API_KEY not found!" >&2
    echo "Please set it in your .env file or environment" >&2
    exit 1
fi

# Run the server in stdio mode (no diagnostic output)
exec python perplexity_fastmcp.py