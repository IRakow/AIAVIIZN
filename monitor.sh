#!/bin/bash

# AIVIIZN Terminal Agent Monitor

echo "📊 AIVIIZN Terminal Agent - System Monitor"
echo "========================================="

# Check system status
echo "🔍 System Status:"
echo "   Virtual environment: $([ -d "venv" ] && echo "✅ Active" || echo "❌ Missing")"
echo "   Screenshots: $(ls -1 screenshots 2>/dev/null | wc -l | tr -d ' ') files"
echo "   Templates: $(find templates -name "*.html" 2>/dev/null | wc -l | tr -d ' ') files"
echo "   Log files: $(ls -1 *.log 2>/dev/null | wc -l | tr -d ' ') files"
echo ""

# Show link status
echo "🔗 Link Processing Status:"
source venv/bin/activate
python3 link_tracker.py --status
echo ""

echo "💡 Commands:"
echo "   ./start_mcp.sh          - Start MCP agent (RECOMMENDED)"
echo "   ./start.sh              - Start standalone agent"
echo "   ./run_mcp_agent.sh --help - Show MCP options"
echo "   python3 link_tracker.py --report - Generate report"
