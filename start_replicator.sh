#!/bin/bash

echo "🚀 QUICK START - APPFOLIO PIXEL-PERFECT REPLICATOR"
echo "=================================================="

# Check if setup has been run
if [ ! -f "requirements_replicator.txt" ]; then
    echo "❌ Please run setup_replicator.sh first"
    exit 1
fi

# Check if API keys are set
if [ -z "$OPENAI_API_KEY" ] && [ ! -f ".env" ]; then
    echo "⚠️  WARNING: No API keys detected"
    echo "   Please add to .env file:"
    echo "   OPENAI_API_KEY=your_key"
    echo "   GEMINI_API_KEY=your_key"
    echo "   WOLFRAM_APP_ID=your_id"
    echo ""
    read -p "Continue anyway? (y/N): " continue_choice
    if [ "$continue_choice" != "y" ]; then
        exit 1
    fi
fi

echo ""
echo "🎯 Starting AppFolio Pixel-Perfect Replicator..."
echo "   This will create exact replicas with multi-AI validation"
echo ""

# Run the main script
python3 appfolio_pixel_perfect_replicator.py
