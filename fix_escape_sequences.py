#!/usr/bin/env python3
"""
Fix escape sequence warnings in aiviizn_real_agent.py
"""

import re

def fix_escape_sequences():
    """Fix JavaScript regex escape sequences in the agent file"""
    
    print("🔧 Fixing escape sequence warnings...")
    
    # Read the file
    with open('aiviizn_real_agent.py', 'r') as f:
        content = f.read()
    
    # Count fixes needed
    original_content = content
    
    # Fix the specific lines with escape sequence issues
    # Line 887 - formulas_found
    content = content.replace(
        'formulas_found = await self.page.evaluate("""',
        'formulas_found = await self.page.evaluate(r"""'
    )
    
    # Line 971 - current_data  
    content = content.replace(
        'current_data = await self.page.evaluate("""',
        'current_data = await self.page.evaluate(r"""'
    )
    
    # Line 1041 - new_data
    content = content.replace(
        'new_data = await self.page.evaluate("""',
        'new_data = await self.page.evaluate(r"""'
    )
    
    # Also fix any other evaluate calls that might have regex
    content = re.sub(
        r'await self\.page\.evaluate\("""',
        r'await self.page.evaluate(r"""',
        content
    )
    
    # Write back the fixed content
    if content != original_content:
        with open('aiviizn_real_agent.py', 'w') as f:
            f.write(content)
        print("✅ Fixed escape sequence warnings!")
        print("   - Used raw strings (r\"\"\") for JavaScript code with regex")
        return True
    else:
        print("⚠️ No changes needed or already fixed")
        return False

if __name__ == "__main__":
    fix_escape_sequences()
    print("\n✨ You can now run:")
    print("   python3 aiviizn_real_agent.py")
