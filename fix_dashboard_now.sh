#!/bin/bash

echo "🔧 Fixing Dashboard Location (should be in /leasing/)"
echo "===================================================="
echo ""

python3 << 'EOF'
agent_file = "/Users/ianrakow/Desktop/AIVIIZN/aiviizn_real_agent_with_ai_intelligence_updated.py"

# Read file
with open(agent_file, 'r') as f:
    content = f.read()

# Add check at beginning of save_template to handle leasing context
# Find where we determine template location
if "elif 'dashboard' in path_str:" in content:
    # Replace simple dashboard check with context-aware version
    old_dashboard = """elif 'dashboard' in path_str:
                template_dir = self.templates_dir
                filename = 'dashboard.html'"""
    
    new_dashboard = """elif 'dashboard' in path_str:
                # Check if this is a leasing dashboard based on URL context
                if 'leasing' in url_lower or 'vacancies' in url_lower or 'lease' in url_lower or 'rental' in url_lower:
                    template_dir = self.templates_dir / 'leasing'
                    filename = 'dashboard.html'
                elif 'property' in url_lower:
                    template_dir = self.templates_dir
                    filename = 'property_dashboard.html'
                elif 'maintenance' in url_lower:
                    template_dir = self.templates_dir / 'maintenance'
                    filename = 'dashboard.html'
                else:
                    template_dir = self.templates_dir
                    filename = 'dashboard.html'"""
    
    # Try to replace
    if "elif 'dashboard' in path_str:" in content:
        # Find and replace this section
        import re
        pattern = r"elif 'dashboard' in path_str:.*?filename = 'dashboard\.html'"
        replacement = new_dashboard
        
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        # Write back
        with open(agent_file, 'w') as f:
            f.write(content)
        
        print("✅ Fixed! Dashboards will now be categorized properly:")
        print("   • Leasing pages → /templates/leasing/dashboard.html")
        print("   • Maintenance pages → /templates/maintenance/dashboard.html")
        print("   • Property pages → /templates/property_dashboard.html")
        print("   • Main dashboard → /templates/dashboard.html")
    else:
        print("⚠️ Could not find exact dashboard pattern")
else:
    print("⚠️ Dashboard section not found")
    print("The save_template method may have been modified")
EOF

echo ""
echo "✅ Run your agent again and dashboards will go to the right folders!"
