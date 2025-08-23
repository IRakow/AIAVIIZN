#!/bin/bash

# AIVIIZN Builder Setup Script
# Handles Python 3 installation and dependency setup

echo "🚀 AIVIIZN BUILDER SETUP"
echo "========================"

# Check if Python 3 is installed
echo "🐍 Checking Python 3..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ Found: $PYTHON_VERSION"
else
    echo "❌ Python 3 not found!"
    echo ""
    echo "📥 INSTALL PYTHON 3:"
    echo "  macOS: brew install python3"
    echo "  Ubuntu: sudo apt-get install python3 python3-pip"
    echo "  Windows: Download from python.org"
    exit 1
fi

# Check if pip3 is available
echo "📦 Checking pip3..."
if command -v pip3 &> /dev/null; then
    echo "✅ pip3 is available"
else
    echo "❌ pip3 not found!"
    echo "📥 Install with: sudo apt-get install python3-pip"
    exit 1
fi

# Install dependencies
echo "📥 Installing dependencies..."
pip3 install -r requirements-builder.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    echo "Try manually: pip3 install anthropic"
    exit 1
fi

# Test system
echo "🧪 Testing system..."
python3 check_system.py

echo ""
echo "🎉 SETUP COMPLETE!"
echo ""
echo "🚀 Choose your builder version:"
echo "  📦 With Bootstrap:    python3 enhanced_aiviizn_builder_with_db.py"
echo "  🎨 No Bootstrap:      python3 enhanced_aiviizn_builder_no_bootstrap.py"
