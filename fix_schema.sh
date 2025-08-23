#!/bin/bash

echo "🔧 Fixing Supabase Schema Issue: Missing 'html_content' column in 'pages' table"
echo "================================================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed"
    exit 1
fi

# Run the fix script
python3 fix_schema_now.py

echo ""
echo "📝 Next Steps:"
echo "1. If automatic fix didn't work, go to Supabase SQL Editor:"
echo "   https://supabase.com/dashboard/project/sejebqdhcilwcpjpznep/sql/new"
echo ""
echo "2. Copy and run this SQL:"
echo "   cat fix_pages_table_schema.sql"
echo ""
echo "3. After fixing, restart your agent:"
echo "   python3 aiviizn_real_agent_with_ai_intelligence_updated.py"
echo ""
