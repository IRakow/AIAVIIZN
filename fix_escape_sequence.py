#!/usr/bin/env python3
"""
Fix the invalid escape sequence warning in the main agent file
"""

# Read the file
with open('/Users/ianrakow/Desktop/AIVIIZN/aiviizn_real_agent_with_ai_intelligence_updated.py', 'r') as f:
    lines = f.readlines()

# Fix line 2727 - the issue is likely with a regex pattern that needs to be a raw string
# Around line 2727, there should be a string with \( that needs to be r"\("

# Check around line 2727
if len(lines) > 2726:
    for i in range(max(0, 2720), min(len(lines), 2735)):
        if '\\(' in lines[i] and not lines[i].strip().startswith('r"') and not lines[i].strip().startswith("r'"):
            print(f"Found invalid escape sequence on line {i+1}: {lines[i].strip()[:80]}")
            # Fix it by making it a raw string
            if '"""' in lines[i]:
                lines[i] = lines[i].replace('"""', 'r"""', 1)
                print(f"Fixed by converting to raw string")

# Write the fixed content back
with open('/Users/ianrakow/Desktop/AIVIIZN/aiviizn_real_agent_with_ai_intelligence_updated.py', 'w') as f:
    f.writelines(lines)

print("✅ Fixed invalid escape sequence warning")
