#!/bin/bash

# BEAUTIFUL AIVIIZN Terminal Agent Launcher
# Creates stunning AppFolio replicas with perfect styling

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment
source venv/bin/activate

echo "🎨 BEAUTIFUL AIVIIZN Terminal Agent"
echo "=================================="
echo "✨ Creates pixel-perfect AppFolio replicas"
echo "🎯 Beautiful design with exact functionality"
echo "🗄️ Perfect database integration"
echo "📊 Accurate calculations and forms"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create it with your API keys."
    exit 1
fi

echo "🚀 Starting beautiful automation..."
echo "📍 Will start at: https://celticprop.appfolio.com/reports"
echo "🔢 Will process exactly 30 pages"
echo "💾 Will save beautiful templates to templates/ folders"
echo ""

# Run the beautiful terminal agent
python3 beautiful_terminal_agent.py --start-reports

echo ""
echo "✨ Beautiful AIVIIZN templates created!"
echo "📁 Check your templates/ folder for stunning results"
