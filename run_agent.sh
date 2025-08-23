#!/bin/bash

echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                    AIVIIZN REAL TERMINAL AGENT                    ║"
echo "║                  BEAUTIFUL • FUNCTIONAL • REAL                    ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""
echo "🎯 Starting REAL page replication..."
echo "📍 Source: AppFolio pages"
echo "🎨 Output: Beautiful templates with YOUR base.html"
echo "⚡ Database: Supabase (normalized, no duplicates)"
echo "💯 Quality: Production-ready, fully functional"
echo ""

cd /Users/ianrakow/Desktop/AIVIIZN

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "🐍 Activating virtual environment..."
    source venv/bin/activate
fi

echo "Starting in 3 seconds..."
sleep 3

python aiviizn_real_agent.py
