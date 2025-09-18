#!/bin/bash

# Final robust MCP server runner for Claude Desktop
# Uses the enhanced robust Python implementation

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Silently set up environment
if [ ! -d "mcp_venv" ]; then
    python3 -m venv mcp_venv 2>/dev/null
fi

source mcp_venv/bin/activate 2>/dev/null

# Install dependencies silently if needed
if [ ! -f "mcp_venv/.deps_installed" ]; then
    pip install -q -r requirements_fastmcp.txt 2>/dev/null && touch mcp_venv/.deps_installed
fi

# Load API key from .env file silently
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | grep PERPLEXITY_API_KEY | xargs) 2>/dev/null
fi

# If no API key, we need to fail gracefully with valid JSON-RPC error
if [ -z "$PERPLEXITY_API_KEY" ]; then
    # Output a proper JSON-RPC error and exit
    echo '{"jsonrpc":"2.0","error":{"code":-32001,"message":"PERPLEXITY_API_KEY not configured"},"id":null}'
    exit 1
fi

# Set environment variables for better stability
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

# Run the robust Python server with error logging to separate file
exec python3 -u perplexity_fastmcp_robust.py 2>>"${SCRIPT_DIR}/mcp_error.log"