#!/bin/bash

echo "🚀 AIVIIZN MCP Agent - Quick Setup"
echo "================================="

# Make scripts executable
chmod +x start_mcp.sh
chmod +x run_mcp_agent.sh
chmod +x mcp_terminal_agent.py

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install minimal dependencies for MCP agent
echo "📥 Installing MCP agent dependencies..."
pip install --upgrade pip
pip install -r requirements_mcp.txt

echo "✅ MCP Agent Ready!"
echo ""
echo "🚀 Next Steps:"
echo "   ./start_mcp.sh  - Start the MCP agent"
echo ""
echo "🤖 The agent will coordinate with your Claude Desktop MCP servers"
