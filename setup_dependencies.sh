#!/bin/bash

# AIVIIZN Terminal Agent - Setup Dependencies

echo "🔧 Setting up AIVIIZN Terminal Agent Dependencies"
echo "=============================================="

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📥 Installing Python packages..."
pip install playwright==1.40.0
pip install openai>=1.3.0
pip install anthropic>=0.8.0
pip install google-generativeai>=0.3.0
pip install supabase>=2.0.0
pip install beautifulsoup4>=4.12.0
pip install requests>=2.31.0

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
playwright install chromium
playwright install-deps

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p screenshots
mkdir -p logs
mkdir -p reports
mkdir -p templates/reports
mkdir -p templates/admin
mkdir -p templates/properties

# Make scripts executable
echo "🔐 Setting script permissions..."
chmod +x *.sh
chmod +x *.py

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "🚀 Next steps:"
echo "1. Ensure your .env file has all API keys"
echo "2. Run: ./quick_start.sh"
echo "3. Monitor progress with: ./monitor_progress.sh"
echo ""
echo "📋 Your .env file should contain:"
echo "   SUPABASE_URL=..."
echo "   SUPABASE_SERVICE_KEY=..."
echo "   OPENAI_API_KEY=..."
echo "   ANTHROPIC_API_KEY=..."
echo "   GEMINI_API_KEY=..."
echo "   WOLFRAM_APP_ID=..."
echo ""

# Deactivate virtual environment
deactivate

echo "🎉 Ready to start processing AppFolio pages!"
