#!/bin/bash

# AIVIIZN Real Agent Runner
echo "🚀 Starting AIVIIZN Real Agent..."
echo "=================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found!"
    exit 1
fi

# Check dependencies
echo "📦 Checking dependencies..."
pip3 install -q playwright supabase anthropic beautifulsoup4 python-dotenv openai openpyxl

# Install Playwright browsers if needed
echo "🌐 Setting up Playwright browsers..."
python3 -m playwright install chromium

# Run the agent
echo ""
echo "✅ All ready! Starting agent..."
echo "=================================="
echo ""

python3 /Users/ianrakow/Desktop/AIVIIZN/aiviizn_real_agent_complete.py
