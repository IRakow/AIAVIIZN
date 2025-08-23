#!/bin/bash

# AIVIIZN Autonomous Builder - Startup Script
# This script starts the autonomous page builder that copies Appfolio to AIVIIZN

echo "╔══════════════════════════════════════════════════════════╗"
echo "║         AIVIIZN AUTONOMOUS PAGE BUILDER                   ║"
echo "║                                                            ║"
echo "║  This will copy pages from Appfolio to your AIVIIZN site  ║"
echo "║  with exact functionality and normalized database          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "❌ Python 3 is not installed. Please install Python 3.8+"
    exit 1
fi

# Check if required files exist
if [ ! -f "autonomous_aiviizn_builder.py" ]; then
    echo "❌ autonomous_aiviizn_builder.py not found!"
    echo "Please ensure all files are in the correct location."
    exit 1
fi

if [ ! -f "aiviizn_database_normalizer.py" ]; then
    echo "❌ aiviizn_database_normalizer.py not found!"
    echo "Please ensure all files are in the correct location."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q --upgrade pip
pip install -q playwright beautifulsoup4 supabase openai google-generativeai anthropic wolframalpha jinja2 numpy

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
playwright install chromium

# Menu function
show_menu() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║                    MAIN MENU                              ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo ""
    echo "1) Initialize Database Schema (First Time Setup)"
    echo "2) Start Autonomous Builder (Copy 1 Page)"
    echo "3) Batch Build (Copy Multiple Pages)"
    echo "4) View Build Reports"
    echo "5) Test Calculations"
    echo "6) View Normalized Data Report"
    echo "7) Exit"
    echo ""
    read -p "Select option: " choice
}

# Main loop
while true; do
    show_menu
    
    case $choice in
        1)
            echo "🔧 Initializing database schema..."
            python3 -c "
import asyncio
from aiviizn_database_normalizer import AIVIIZNDataNormalizer

async def init():
    normalizer = AIVIIZNDataNormalizer(
        'https://sejebqdhcilwcpjpznep.supabase.co',
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNlamVicWRoY2lsd2NwanB6bmVwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTg5NjQsImV4cCI6MjA3MDAzNDk2NH0.vFM0Gr3QZF4MN3vtDGghjyCpnIkyC_mmUOOkVO3ahPQ'
    )
    await normalizer.initialize_schema()
    print('✅ Database schema initialized!')

asyncio.run(init())
"
            ;;
        2)
            echo "🚀 Starting Autonomous Builder..."
            echo "This will copy 1 page from Appfolio to AIVIIZN"
            read -p "Press Enter to continue..."
            python3 autonomous_aiviizn_builder.py
            ;;
        3)
            read -p "How many pages to build? (1-30): " num_pages
            echo "🚀 Starting batch build for $num_pages pages..."
            python3 -c "
import asyncio
from autonomous_aiviizn_builder import AutonomousAIVIIZNBuilder, Config

async def batch_build():
    config = Config()
    config.MAX_PAGES_PER_RUN = $num_pages
    builder = AutonomousAIVIIZNBuilder(config)
    await builder.run_autonomous_build('https://celticprop.appfolio.com/reports')

asyncio.run(batch_build())
"
            ;;
        4)
            echo "📊 Available Build Reports:"
            ls -la build_report_*.json 2>/dev/null || echo "No reports found"
            ;;
        5)
            echo "🧮 Testing calculation extraction..."
            python3 -c "
import asyncio
from autonomous_aiviizn_builder import AutonomousAIVIIZNBuilder, Config

async def test():
    config = Config()
    builder = AutonomousAIVIIZNBuilder(config)
    await builder._init_browser()
    await builder.page.goto('https://celticprop.appfolio.com/reports')
    calcs = await builder._extract_calculations(await builder.page.content())
    print(f'Found {len(calcs)} calculations')
    for calc in calcs[:5]:
        print(f'  - {calc}')
    await builder._cleanup()

asyncio.run(test())
"
            ;;
        6)
            echo "📈 Generating Normalized Data Report..."
            python3 -c "
import asyncio
from aiviizn_database_normalizer import AIVIIZNDataNormalizer

async def report():
    normalizer = AIVIIZNDataNormalizer(
        'https://sejebqdhcilwcpjpznep.supabase.co',
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNlamVicWRoY2lsd2NwanB6bmVwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTg5NjQsImV4cCI6MjA3MDAzNDk2NH0.vFM0Gr3QZF4MN3vtDGghjyCpnIkyC_mmUOOkVO3ahPQ'
    )
    report = await normalizer.generate_normalized_report()
    import json
    print(json.dumps(report, indent=2))

asyncio.run(report())
"
            ;;
        7)
            echo "👋 Exiting..."
            exit 0
            ;;
        *)
            echo "Invalid option. Please try again."
            ;;
    esac
done
