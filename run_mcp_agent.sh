#!/bin/bash

# AIVIIZN MCP Terminal Agent Launcher

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create it with your API keys."
    exit 1
fi

echo "🚀 AIVIIZN MCP Terminal Agent"
echo "✅ Using your configured MCP servers:"
echo "   - Filesystem MCP (file operations)"
echo "   - Playwright MCP (browser automation)"  
echo "   - Supabase MCP (database operations)"
echo "🤖 This agent coordinates with Claude Desktop MCP servers"
echo ""

# Run the MCP terminal agent
python3 mcp_terminal_agent.py "$@"
