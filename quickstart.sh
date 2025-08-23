#!/bin/bash

echo "🔍 Quick Diagnostic for AIVIIZN"
echo "===================================="

# Make scripts executable
chmod +x *.py
chmod +x *.sh

# Run diagnostic
python3 diagnose.py

echo ""
echo "🚑 QUICK START COMMANDS:"
echo "1. python3 diagnose.py          (run this diagnostic)"
echo "2. python3 test_claude_opening.py   (test Claude opening)"
echo "3. ./start_builder.sh           (start main script)"
echo "4. Choose option 5 in main script for immediate start"
echo ""
