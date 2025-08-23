#!/usr/bin/env python3
"""
Simple fix: Put leasing-related pages in leasing folder
"""

agent_file = "/Users/ianrakow/Desktop/AIVIIZN/aiviizn_real_agent_with_ai_intelligence_updated.py"

# Read the file
with open(agent_file, 'r') as f:
    lines = f.readlines()

# Find the save_template method and update it
in_save_template = False
for i, line in enumerate(lines):
    if 'def save_template(self, url: str, html: str) -> str:' in line:
        in_save_template = True
    
    # Find where we check for dashboard
    if in_save_template and "elif 'dashboard' in path_str:" in line:
        # Replace this line with context-aware logic
        indent = len(line) - len(line.lstrip())
        lines[i] = ' ' * indent + "elif 'dashboard' in path_str:\n"
        # Insert new logic after
        new_lines = [
            ' ' * (indent + 4) + "# Check context from URL\n",
            ' ' * (indent + 4) + "if any(x in url_lower for x in ['/leasing', 'vacancies', 'rental', 'lease']):\n",
            ' ' * (indent + 8) + "template_dir = self.templates_dir / 'leasing'\n",
            ' ' * (indent + 8) + "filename = 'dashboard.html'\n",
            ' ' * (indent + 4) + "elif 'property' in url_lower:\n",
            ' ' * (indent + 8) + "template_dir = self.templates_dir\n",
            ' ' * (indent + 8) + "filename = 'property_dashboard.html'\n",
            ' ' * (indent + 4) + "else:\n",
            ' ' * (indent + 8) + "template_dir = self.templates_dir\n",
            ' ' * (indent + 8) + "filename = 'dashboard.html'\n"
        ]
        
        # Find next elif/else and insert before it
        j = i + 1
        while j < len(lines):
            if lines[j].strip().startswith(('elif ', 'else:')):
                # Insert our new lines here
                lines[i+1:i+1] = new_lines
                break
            j += 1
        
        print("✅ Updated dashboard logic!")
        break

# Write back
with open(agent_file, 'w') as f:
    f.writelines(lines)

print("\n📁 Dashboards will now go to:")
print("   • Leasing context → /templates/leasing/dashboard.html ✅")
print("   • Property context → /templates/property_dashboard.html")
print("   • Default → /templates/dashboard.html")
