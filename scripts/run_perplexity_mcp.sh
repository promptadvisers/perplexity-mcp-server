#!/bin/bash

# Perplexity MCP Server Wrapper Script
# This script activates the virtual environment and runs the server

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the script directory
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "mcp_venv" ]; then
    echo "Error: Virtual environment not found at $SCRIPT_DIR/mcp_venv" >&2
    echo "Please run the setup instructions first:" >&2
    echo "  python3 -m venv mcp_venv" >&2
    echo "  source mcp_venv/bin/activate" >&2
    echo "  pip install -r requirements.txt" >&2
    exit 1
fi

# Check if .env file exists and source it if available
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Activate the virtual environment and run the server
source mcp_venv/bin/activate
exec python perplexity_mcp_server.py