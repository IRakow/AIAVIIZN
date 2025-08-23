#!/bin/bash

echo "🎯 APPFOLIO PIXEL-PERFECT REPLICATOR SETUP"
echo "=========================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

echo "✅ Python 3 found"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements_replicator.txt

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
python3 -m playwright install chromium

# Make the main script executable
chmod +x appfolio_pixel_perfect_replicator.py

# Create directories
echo "📁 Creating required directories..."
mkdir -p screenshots
mkdir -p docs/reports
mkdir -p static/js/reports

echo ""
echo "✅ SETUP COMPLETE!"
echo ""
echo "🚀 To run the replicator:"
echo "   python3 appfolio_pixel_perfect_replicator.py"
echo ""
echo "⚠️  IMPORTANT: Make sure your .env file contains:"
echo "   OPENAI_API_KEY=your_key_here"
echo "   GEMINI_API_KEY=your_key_here" 
echo "   WOLFRAM_APP_ID=your_app_id_here"
echo ""
echo "🎯 The script will:"
echo "   1. Open AppFolio in browser"
echo "   2. Wait for you to authenticate"
echo "   3. Extract every page with pixel-perfect detail"
echo "   4. Validate with 4 AI systems"
echo "   5. Generate exact replicas in your AIVIIZN framework"
echo ""
