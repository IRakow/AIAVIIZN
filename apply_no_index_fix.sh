#!/bin/bash

echo "🚫 REMOVING index.html DEFAULTS"
echo "================================"
echo ""
echo "Updating save_template to always use descriptive names..."
echo ""

python3 /Users/ianrakow/Desktop/AIVIIZN/fix_no_index_html.py

echo ""
echo "✅ Done! Your agent will now:"
echo "   • NEVER create index.html files"
echo "   • ALWAYS use descriptive names based on the page"
echo ""
echo "Examples:"
echo "   / → dashboard.html"
echo "   /vacancies → leasing/vacancies.html"
echo "   /work_orders → maintenance/work_orders.html"
echo ""
