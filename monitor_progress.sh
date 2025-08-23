#!/bin/bash

# AIVIIZN Terminal Agent - Progress Monitor

echo "📊 AIVIIZN Terminal Agent - Progress Monitor"
echo "=========================================="

# Check if we're in the right directory
if [ ! -f ".env" ]; then
    echo "❌ Please run from the AIVIIZN directory"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "🔗 Link Processing Status:"
python3 link_tracker.py --status

echo ""
echo "📈 System Files:"
echo "- Screenshots: $(ls -1 screenshots 2>/dev/null | wc -l) files"
echo "- Templates: $(find templates -name "*.html" 2>/dev/null | wc -l) templates"  
echo "- Log files: $(ls -1 *.log 2>/dev/null | wc -l) files"
echo "- Reports: $(ls -1 *_report_*.json 2>/dev/null | wc -l) reports"

echo ""
echo "🎯 Next Priority Links:"
python3 link_tracker.py --next

echo ""
echo "📋 Quick Actions:"
echo "1. Continue processing: ./quick_start.sh"
echo "2. Validate math: python3 math_validator.py --batch"
echo "3. Generate report: python3 link_tracker.py --report"
echo "4. Check database: python3 -c \"from supabase import create_client; import os; print('Database connected') if create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY')).table('appfolio_pages').select('count').execute() else print('Database error')\""

echo ""
echo "📊 Database Status:"
python3 -c "
import os
from supabase import create_client
try:
    client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))
    pages = client.table('appfolio_pages').select('count').execute()
    calcs = client.table('calculation_formulas').select('count').execute()
    validations = client.table('multi_ai_validations').select('count').execute()
    print(f'✅ Database connected')
    print(f'📄 Pages captured: {len(pages.data) if pages.data else 0}')
    print(f'🧮 Calculations: {len(calcs.data) if calcs.data else 0}')
    print(f'✓ Validations: {len(validations.data) if validations.data else 0}')
except Exception as e:
    print(f'❌ Database error: {e}')
"
