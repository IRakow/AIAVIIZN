#!/bin/bash

echo "🚀 AIVIIZN REAL AGENT SETUP"
echo "=========================="
echo ""
echo "Setting up REAL terminal agent that creates BEAUTIFUL, FUNCTIONAL pages"
echo ""

# Navigate to project directory
cd /Users/ianrakow/Desktop/AIVIIZN

# Create virtual environment (recommended)
echo "🐍 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies in correct order to avoid conflicts
echo "📦 Installing dependencies (this may take a moment)..."
pip install websockets>=12.0
pip install httpx>=0.24.0
pip install postgrest==0.16.8
pip install realtime==1.0.0
pip install supabase==2.0.2
pip install playwright==1.40.0
pip install anthropic==0.7.8
pip install beautifulsoup4==4.12.2
pip install python-dotenv==1.0.0

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
python -m playwright install

# Create data directory
mkdir -p data/screenshots

echo ""
echo "✅ SETUP COMPLETE!"
echo ""
echo "🎯 WHAT THIS DOES:"
echo "• Navigates to REAL AppFolio pages"
echo "• Extracts EXACT main content (not their navigation)"
echo "• Creates BEAUTIFUL templates with YOUR base.html"
echo "• Makes everything FULLY FUNCTIONAL with Supabase" 
echo "• Stores normalized data (no duplicates)"
echo "• Generates production-ready pages"
echo ""
echo "🚀 TO RUN THE AGENT:"
echo "source venv/bin/activate  # (activate virtual environment)"
echo "python aiviizn_real_agent.py"
echo ""
echo "📋 OR USE THE QUICK START:"
echo "./run_agent.sh"
echo ""
