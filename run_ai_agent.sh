#!/bin/bash
# Make this file executable with: chmod +x run_ai_agent.sh

# AIVIIZN AI-Powered Agent Launcher
# Run the agent with AI field intelligence

echo "🚀 Starting AIVIIZN with AI Field Intelligence..."
echo "================================================"

# Change to project directory
cd /Users/ianrakow/Desktop/AIVIIZN

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✓ Virtual environment activated"
fi

# Check for required environment variables
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  Warning: ANTHROPIC_API_KEY not set"
fi

if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: OPENAI_API_KEY not set (optional but recommended)"
fi

# Run the AI-powered agent
python3 run_ai_agent.py

echo "================================================"
echo "✅ Agent session complete"
