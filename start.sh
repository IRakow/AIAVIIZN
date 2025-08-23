#!/bin/bash

# AIVIIZN Terminal Agent - Quick Start Menu

echo "🚀 AIVIIZN Terminal Agent - AppFolio Replicator"
echo "==============================================="
echo ""
echo "Choose an option:"
echo ""
echo "1. Start with Reports Page (Recommended)"
echo "2. Process specific URL"
echo "3. Check link status"
echo "4. Validate calculations"
echo "5. Generate progress report"
echo ""

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo "🔍 Starting with AppFolio reports page..."
        ./run_agent.sh --start-reports
        ;;
    2)
        read -p "Enter URL: " url
        ./run_agent.sh --url "$url"
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
        ./run_agent.sh --start-reports
        ;;
esac

echo ""
echo "✅ Session completed!"
echo "📊 Check generated files in templates/ and screenshots/"
