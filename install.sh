#!/bin/bash

# AIVIIZN Installation Script
echo "🚀 Installing AIVIIZN Real Agent dependencies..."
echo "============================================="

# Check if pip3 is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install Python 3 first."
    exit 1
fi

# Install Python dependencies
echo ""
echo "📦 Installing Python packages..."
pip3 install -r requirements.txt

# Check if installation was successful
if [ $? -eq 0 ]; then
    echo "✅ Python packages installed successfully!"
else
    echo "❌ Failed to install Python packages"
    echo ""
    echo "💡 If you see dependency conflicts, try:"
    echo "   pip3 install --upgrade supabase"
    echo "   pip3 install -r requirements.txt"
    exit 1
fi

# Install Playwright browsers
echo ""
echo "🌐 Installing Playwright browsers..."
python3 -m playwright install chromium

if [ $? -eq 0 ]; then
    echo "✅ Playwright browsers installed successfully!"
else
    echo "⚠️  Failed to install Playwright browsers"
    echo "   Try manually: python3 -m playwright install"
fi

# Check for .env file
echo ""
echo "🔧 Checking configuration..."
if [ ! -f .env ]; then
    echo "⚠️  No .env file found!"
    echo "   Creating from .env.example..."
    cp .env.example .env
    echo "   ✅ Created .env file - please edit it with your API keys:"
    echo ""
    echo "   Required keys:"
    echo "   - SUPABASE_URL"
    echo "   - SUPABASE_KEY (anon key)"
    echo "   - SUPABASE_SERVICE_KEY (service role key)"
    echo "   - ANTHROPIC_API_KEY"
    echo "   - WOLFRAM_APP_ID (optional but recommended)"
else
    echo "✅ .env file exists"
fi

echo ""
echo "✨ Installation complete!"
echo ""
echo "To run the agent:"
echo "   python3 aiviizn_real_agent.py"
echo ""
echo "To test the calculation extraction:"
echo "   python3 test_calculations_advanced.py"
