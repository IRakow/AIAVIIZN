#!/bin/bash

echo "🔧 FIXING DEPENDENCY ISSUES..."
echo "==============================="

# Uninstall conflicting packages
echo "📦 Cleaning up conflicting packages..."
pip3 uninstall -y supabase websockets realtime postgrest httpx

# Install dependencies in correct order
echo "📦 Installing dependencies in correct order..."
pip3 install websockets>=12.0
pip3 install httpx>=0.24.0
pip3 install postgrest==0.16.8
pip3 install realtime==1.0.0
pip3 install supabase==2.0.2

# Install other packages
pip3 install playwright==1.40.0
pip3 install anthropic==0.7.8
pip3 install beautifulsoup4==4.12.2
pip3 install python-dotenv==1.0.0

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
python3 -m playwright install

echo ""
echo "✅ DEPENDENCIES FIXED!"
echo ""
echo "🚀 NOW RUN THE AGENT:"
echo "python3 aiviizn_real_agent.py"
echo ""
