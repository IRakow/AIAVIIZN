#!/usr/bin/env python3
"""
Simple patch to add real-time visibility to template creation
Shows EXACTLY what's being created as it happens
"""

import sys
import os

# Read the agent file
agent_file = "/Users/ianrakow/Desktop/AIVIIZN/aiviizn_real_agent_with_ai_intelligence_updated.py"

with open(agent_file, 'r') as f:
    content = f.read()

# Find and replace the save_template method with enhanced version
new_save_template = '''    def save_template(self, url: str, html: str) -> str:
        """Save template to file with REAL-TIME VISIBILITY"""
        try:
            parsed = urlparse(url)
            path_parts = parsed.path.strip('/').split('/')
            
            # Determine template location
            if len(path_parts) > 1:
                # Create subdirectories
                template_dir = self.templates_dir / '/'.join(path_parts[:-1])
                filename = f"{path_parts[-1]}.html" if path_parts[-1] else 'index.html'
                template_path = template_dir / filename
                template_dir.mkdir(parents=True, exist_ok=True)
            else:
                # Root level
                filename = f"{path_parts[0]}.html" if path_parts[0] else 'index.html'
                template_path = self.templates_dir / filename
            
            # SHOW WHAT'S BEING CREATED RIGHT NOW
            print(f"\\n{'='*60}")
            print(f"📁 CREATING TEMPLATE NOW:")
            print(f"📂 Directory: {template_path.parent}")
            print(f"📄 Filename: {filename}")
            print(f"🔗 Full Path: {template_path}")
            print(f"💾 Size: {len(html):,} bytes")
            print(f"{'='*60}\\n")
            
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(html)
            
            return str(template_path)
            
        except Exception as e:
            print(f"❌ ERROR SAVING: {e}")
            return ""'''

# Replace the method
import re

# Find the save_template method
pattern = r'(    def save_template\(self.*?\n(?:.*?\n)*?        except Exception.*?\n.*?\n.*?\n)'
match = re.search(pattern, content)

if match:
    # Replace with new version
    content = content[:match.start()] + new_save_template + content[match.end():]
    
    # Write back
    with open(agent_file, 'w') as f:
        f.write(content)
    
    print("✅ PATCHED! Now you'll see:")
    print("   📂 Exact directory being created")
    print("   📄 Exact filename being saved")
    print("   🔗 Full path to the template")
    print("   💾 File size")
    print("\nRun your agent now to see real-time output!")
else:
    print("❌ Could not find save_template method")
    print("Adding new version at the end of the class...")
