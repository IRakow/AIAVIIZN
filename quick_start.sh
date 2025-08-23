#!/bin/bash

# AIVIIZN Terminal Agent - Quick Start

echo "🔥 AIVIIZN Terminal Agent - PRODUCTION READY"
echo "============================================="

# Check if we're in the right directory
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please ensure you're in the AIVIIZN directory."
    exit 1
fi

# Check if dependencies are installed
# Use production dependencies if available
if [ -f "requirements_production.txt" ]; then
    echo "🔥 Using PRODUCTION dependencies..."
fi

if [ ! -d "venv" ]; then
    echo "📦 Setting up PRODUCTION virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    
    echo "📥 Installing LATEST dependencies..."
    pip install --upgrade pip
    
    if [ -f "requirements_production.txt" ]; then
        pip install -r requirements_production.txt
    else
        pip install playwright>=1.41.0 openai>=1.8.0 anthropic>=0.12.0 google-generativeai>=0.4.0 supabase>=2.3.0 beautifulsoup4>=4.12.2 requests>=2.32.0 python-dotenv>=1.0.1
    fi
    
    echo "🌐 Installing Playwright browsers..."
    playwright install chromium
    playwright install-deps
else
    source venv/bin/activate
fi

echo ""
echo "Available commands:"
echo ""
echo "1. Start with Reports Page (Recommended):"
echo "   python3 terminal_agent.py --start-reports"
echo ""
echo "2. Process Specific URL:"
echo "   python3 terminal_agent.py --url https://celticprop.appfolio.com/reports"
echo ""
echo "3. Check Link Status:"
echo "   python3 link_tracker.py --status"
echo ""
echo "4. Validate Calculations:"
echo "   python3 math_validator.py --batch"
echo ""
echo "5. Generate Progress Report:"
echo "   python3 link_tracker.py --report"
echo ""

read -p "Enter your choice (1-5) or press Enter to start with reports: " choice

case $choice in
    1|"")
        echo "🔥 PRODUCTION: Starting with AppFolio reports page..."
        echo "📋 Browser opening with NO THROTTLING enabled"
        echo "🚀 Maximum speed processing with latest AI models"
        echo "⏳ Login manually when prompted, then processing begins..."
        python3 terminal_agent.py --start-reports
        ;;
    2)
        read -p "Enter URL: " url
        python3 terminal_agent.py --url "$url"
        ;;
    3)
        python3 link_tracker.py --status
        ;;
    4)
        python3 math_validator.py --batch
        ;;
    5)
        python3 link_tracker.py --report
        ;;
    *)
        echo "Invalid choice. Starting with reports page..."
        python3 terminal_agent.py --start-reports
        ;;
esac

echo ""
echo "🎉 PRODUCTION SESSION COMPLETED!"
echo "📊 Generated production-ready files:"
echo "   - Screenshots: screenshots/"
echo "   - Templates: templates/ (ready for deployment)"
echo "   - Links: discovered_links.json"
echo "   - Reports: session_report_*.json"
echo "   - Database: All data saved to Supabase"
echo "💡 Use ./monitor_progress.sh to check status"
