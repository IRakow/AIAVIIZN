#!/bin/bash
# AIVIIZN One-Command Fix
# This script resolves all installation issues

echo "🚀 AIVIIZN One-Command Fix"
echo "============================"
echo ""

# Use pip3 since pip is not available
PIP_CMD="pip3"

echo "📦 Installing packages without version conflicts..."
$PIP_CMD install --upgrade playwright
$PIP_CMD install --upgrade anthropic  
$PIP_CMD install --upgrade supabase
$PIP_CMD install --upgrade beautifulsoup4
$PIP_CMD install --upgrade python-dotenv
$PIP_CMD install --upgrade wolframalpha
$PIP_CMD install --upgrade openpyxl

echo ""
echo "🌐 Installing Playwright browser..."
python3 -m playwright install chromium

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Test Playwright: python3 test_playwright.py"
echo "2. Check setup:     python3 diagnose_setup.py"
echo "3. Run agent:       python3 aiviizn_real_agent.py"
