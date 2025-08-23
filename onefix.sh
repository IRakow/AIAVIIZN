#!/bin/bash
# ONE COMMAND FIX

echo "🚀 ONE-COMMAND FIX FOR ALL ISSUES"
echo "================================="
echo ""

# Fix websockets
pip3 uninstall -y websockets realtime supabase postgrest gotrue storage3 2>/dev/null
pip3 install supabase

# Run the Python fixer for escape sequences
python3 -c "
import re
try:
    with open('aiviizn_real_agent.py', 'r') as f:
        content = f.read()
    content = content.replace('await self.page.evaluate(\"\"\"', 'await self.page.evaluate(r\"\"\"')
    content = content.replace('await page.evaluate(\"\"\"', 'await page.evaluate(r\"\"\"')
    with open('aiviizn_real_agent.py', 'w') as f:
        f.write(content)
    print('✅ Fixed escape sequences')
except:
    print('⚠️ Could not fix escape sequences')
"

echo ""
echo "✅ DONE! Now run:"
echo "   python3 aiviizn_real_agent.py"
