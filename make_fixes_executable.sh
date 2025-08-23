#!/bin/bash
# Make all fix scripts executable

chmod +x fix_websockets.py
chmod +x fix_escape_sequences.py
chmod +x fix_all_issues.py
chmod +x FINAL_FIX.py
chmod +x fix_everything.py
chmod +x quickfix.sh
chmod +x onefix.sh
chmod +x quickstart.py
chmod +x diagnose_setup.py
chmod +x test_playwright.py

echo "✅ All fix scripts are now executable"
echo ""
echo "Run the complete fix:"
echo "  python3 FINAL_FIX.py"
echo ""
echo "Or the quick bash fix:"
echo "  ./onefix.sh"
