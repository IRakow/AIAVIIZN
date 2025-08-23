#!/bin/bash
# Quick fix for websockets issue

echo "🔧 Quick Fix for websockets.asyncio error"
echo "========================================="
echo ""

# Simple approach - reinstall everything fresh
echo "📦 Reinstalling packages..."
pip3 uninstall -y websockets realtime supabase postgrest gotrue storage3
pip3 install supabase

echo ""
echo "✅ Packages reinstalled!"
echo ""
echo "Testing import..."
python3 -c "from supabase import create_client; print('✅ Import successful!')" 2>/dev/null

if [ $? -eq 0 ]; then
    echo ""
    echo "✨ Fix successful! Now fixing escape sequences..."
    python3 fix_escape_sequences.py 2>/dev/null
    echo ""
    echo "You can now run:"
    echo "  python3 aiviizn_real_agent.py"
else
    echo ""
    echo "⚠️ Still having issues. Try:"
    echo "  python3 fix_all_issues.py"
fi
