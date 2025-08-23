#!/bin/bash

echo "🔧 REPLACING save_template method with proper directory structure"
echo "================================================================"
echo ""

python3 /Users/ianrakow/Desktop/AIVIIZN/replace_save_template.py

echo ""
echo "✅ Done! Restart your agent to use the fixed directory structure."
echo ""
echo "Next time you process /vacancies, it will save to:"
echo "  📁 /templates/leasing/vacancies.html"
echo ""
