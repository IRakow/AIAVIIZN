#!/bin/bash

# AIVIIZN MCP Terminal Agent - Quick Start Menu

echo "🚀 AIVIIZN MCP Terminal Agent - AppFolio Replicator"
echo "==============================================="
echo "✅ Using your configured MCP servers"
echo "🤖 Coordinates with Claude Desktop for processing"
echo ""
echo "Choose an option:"
echo ""
echo "1. Start with Reports Page (Recommended)"
echo "2. Process specific URL"
echo "3. Check current status"
echo "4. Add URL to queue"
echo ""

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo "🔍 Starting with AppFolio reports page..."
        echo "🤖 Will coordinate with Claude MCP servers..."
        ./run_mcp_agent.sh --start-reports
        ;;
    2)
        read -p "Enter URL: " url
        ./run_mcp_agent.sh --url "$url"
        ;;
    3)
        ./run_mcp_agent.sh --status
        ;;
    4)
        read -p "Enter URL to add: " url
        ./run_mcp_agent.sh --add "$url"
        ;;
    *)
        echo "Invalid choice. Starting with reports page..."
        ./run_mcp_agent.sh --start-reports
        ;;
esac

echo ""
echo "✅ MCP session completed!"
echo "📊 Check templates/ for generated files"
echo "🗄️ Check Supabase for stored analysis"
