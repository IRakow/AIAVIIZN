#!/usr/bin/env python3
"""
Apply enhanced template logging to see exactly what files are being created
Run this BEFORE starting your agent
"""

print("\n" + "="*60)
print("🔧 APPLYING ENHANCED TEMPLATE LOGGING PATCH")
print("="*60)

# Create a modified version of the agent with enhanced logging
import shutil
from pathlib import Path

# Backup original
original = Path("/Users/ianrakow/Desktop/AIVIIZN/aiviizn_real_agent_with_ai_intelligence_updated.py")
backup = Path("/Users/ianrakow/Desktop/AIVIIZN/aiviizn_real_agent_with_ai_intelligence_updated.py.backup_before_logging")

if not backup.exists():
    shutil.copy(original, backup)
    print(f"✅ Created backup: {backup.name}")

# Read the original file
with open(original, 'r') as f:
    content = f.read()

# Find the save_template method and enhance it
enhanced_save_template = '''
    def save_template(self, url: str, html: str) -> str:
        """Save template to file with ENHANCED VISIBILITY LOGGING"""
        try:
            print("\\n" + "="*60)
            print("📁 CREATING TEMPLATE FILE")
            print("="*60)
            
            # Parse URL to determine file structure
            parsed = urlparse(url)
            print(f"🔗 Source URL: {url}")
            print(f"   • Domain: {parsed.netloc}")
            print(f"   • Path: {parsed.path}")
            
            path_parts = parsed.path.strip('/').split('/')
            print(f"   • Path parts: {path_parts}")
            
            # Determine template location
            if len(path_parts) > 1:
                # Create subdirectories matching URL structure
                template_dir = self.templates_dir / '/'.join(path_parts[:-1])
                filename = f"{path_parts[-1]}.html" if path_parts[-1] else 'index.html'
                template_path = template_dir / filename
                
                print(f"\\n📂 Creating directory structure:")
                print(f"   Base: {self.templates_dir}")
                print(f"   Subdirs: {'/'.join(path_parts[:-1])}")
                print(f"   Full path: {template_dir}")
                
                # Create directories
                template_dir.mkdir(parents=True, exist_ok=True)
                print(f"   ✅ Directory created/verified")
                
            else:
                # Root level template
                filename = f"{path_parts[0]}.html" if path_parts[0] else 'index.html'
                template_path = self.templates_dir / filename
                
                print(f"\\n📄 Creating root-level template:")
                print(f"   Directory: {self.templates_dir}")
            
            print(f"\\n📝 Template Details:")
            print(f"   Filename: {filename}")
            print(f"   Full path: {template_path}")
            print(f"   Relative: templates/{template_path.relative_to(self.templates_dir)}")
            
            # Determine template type based on URL
            template_type = "unknown"
            url_lower = url.lower()
            if 'dashboard' in url_lower:
                template_type = "Dashboard"
            elif 'report' in url_lower:
                if 'income' in url_lower:
                    template_type = "Income Statement Report"
                elif 'balance' in url_lower:
                    template_type = "Balance Sheet Report"
                elif 'rent_roll' in url_lower:
                    template_type = "Rent Roll Report"
                elif 'delinquency' in url_lower:
                    template_type = "Delinquency Report"
                else:
                    template_type = "Generic Report"
            elif 'form' in url_lower or 'edit' in url_lower or 'new' in url_lower:
                template_type = "Form Page"
            elif 'list' in url_lower or 'index' in url_lower:
                template_type = "List/Index Page"
            elif 'property' in url_lower:
                template_type = "Property Page"
            elif 'tenant' in url_lower:
                template_type = "Tenant Page"
            
            print(f"\\n🎨 Template Type: {template_type}")
            
            # Check if template already exists
            if template_path.exists():
                print(f"\\n⚠️  Template already exists - will overwrite")
            
            # Analyze template content
            print(f"\\n📊 Template Content Analysis:")
            print(f"   • Size: {len(html):,} bytes")
            
            # Count important elements
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            forms = soup.find_all('form')
            tables = soup.find_all('table')
            inputs = soup.find_all(['input', 'select', 'textarea'])
            ai_fields = soup.find_all(attrs={'data-ai-name': True})
            
            print(f"   • Forms: {len(forms)}")
            print(f"   • Tables: {len(tables)}")
            print(f"   • Input fields: {len(inputs)}")
            print(f"   • AI-enhanced fields: {len(ai_fields)}")
            
            # Save the template
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(html)
            
            print(f"\\n✅ TEMPLATE SAVED SUCCESSFULLY")
            print(f"   Path: {template_path}")
            
            # Show how to access it
            flask_route = str(template_path.relative_to(self.templates_dir).with_suffix('')).replace('\\\\', '/')
            print(f"\\n🌐 Access this page at:")
            print(f"   http://localhost:8080/{flask_route}")
            
            print("="*60 + "\\n")
            
            return str(template_path)
            
        except Exception as e:
            print(f"\\n❌ ERROR SAVING TEMPLATE: {e}")
            import traceback
            print(traceback.format_exc())
            return ""
'''

# Replace the save_template method
if 'def save_template(self, url: str, html: str) -> str:' in content:
    # Find the method and replace it
    import re
    
    # Find the start of the method
    start_pattern = r'def save_template\(self, url: str, html: str\) -> str:'
    match = re.search(start_pattern, content)
    
    if match:
        start_pos = match.start()
        
        # Find the end of the method (next method definition at same indentation)
        # Look for next "    def " at the same indentation level
        rest_of_content = content[start_pos:]
        next_method_match = re.search(r'\n    def \w+\(', rest_of_content[200:])  # Skip current method
        
        if next_method_match:
            end_pos = start_pos + 200 + next_method_match.start()
        else:
            # No next method found, might be last method
            # Look for class end or end of file
            end_pos = len(content)
        
        # Replace the method
        new_content = content[:start_pos] + enhanced_save_template.strip() + '\n' + content[end_pos:]
        
        # Write back
        with open(original, 'w') as f:
            f.write(new_content)
        
        print("✅ Enhanced logging applied to save_template method")
        print("\n📝 The agent will now show:")
        print("   • Exact directory and filename for each template")
        print("   • Template type detection (Dashboard, Report, Form, etc.)")
        print("   • Content analysis (forms, tables, AI fields)")
        print("   • Flask route for accessing the page")
        
    else:
        print("⚠️  Could not find save_template method to patch")
        print("   You may need to manually add the enhanced logging")
else:
    print("⚠️  save_template method not found in agent")
    print("   The agent might use a different method name")

print("\n✨ Now run your agent and watch the detailed template creation logs!")
print("   python3 aiviizn_real_agent_with_ai_intelligence_updated.py")
print("="*60)
