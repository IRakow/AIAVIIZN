#!/bin/bash

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║          AIVIIZN REAL AUTOMATED AGENT - SETUP                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3"
    exit 1
fi

echo "✓ Python 3 found"

# Check and install requirements
echo ""
echo "📦 Installing required packages..."
echo ""

pip3 install playwright supabase anthropic python-dotenv

echo ""
echo "🌐 Installing Playwright browser..."
echo ""

playwright install chromium

echo ""
echo "✅ Setup complete!"
echo ""
echo "▶️  To run the automated agent:"
echo ""
echo "   python3 aiviizn_real_automated.py"
echo ""
echo "The agent will:"
echo "  • Login to AppFolio (you provide credentials)"
echo "  • Process pages automatically"
echo "  • Generate templates with your base.html"
echo "  • Store in Supabase (normalized)"
echo "  • Continue until all pages done"
echo "  • No token limits - runs forever"
echo ""
