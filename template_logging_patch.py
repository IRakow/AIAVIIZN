#!/usr/bin/env python3
"""
Enhanced logging patch for template creation visibility
Add this to your agent to see exactly what templates are being created where
"""

import os
from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime

def save_template_with_detailed_logging(self, url: str, html: str) -> str:
    """
    Enhanced save_template function with detailed logging
    Shows exactly what directory and filename is being created
    """
    try:
        print("\n" + "="*60)
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
            
            print(f"\n📂 Creating directory structure:")
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
            
            print(f"\n📄 Creating root-level template:")
            print(f"   Directory: {self.templates_dir}")
        
        print(f"\n📝 Template Details:")
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
        elif 'login' in url_lower or 'auth' in url_lower:
            template_type = "Authentication Page"
        elif 'property' in url_lower or 'properties' in url_lower:
            template_type = "Property Page"
        elif 'tenant' in url_lower or 'resident' in url_lower:
            template_type = "Tenant/Resident Page"
        elif 'payment' in url_lower or 'transaction' in url_lower:
            template_type = "Payment/Transaction Page"
        elif 'maintenance' in url_lower or 'work_order' in url_lower:
            template_type = "Maintenance Page"
        
        print(f"\n🎨 Template Type: {template_type}")
        
        # Check if template already exists
        if template_path.exists():
            print(f"\n⚠️  Template already exists!")
            print(f"   Will overwrite: {template_path}")
            # Backup existing
            backup_path = template_path.with_suffix(f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html')
            with open(template_path, 'r', encoding='utf-8') as f:
                backup_content = f.read()
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(backup_content)
            print(f"   📋 Backup saved: {backup_path.name}")
        
        # Analyze template content
        print(f"\n📊 Template Content Analysis:")
        print(f"   • Size: {len(html):,} bytes")
        
        # Count important elements
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        forms = soup.find_all('form')
        tables = soup.find_all('table')
        inputs = soup.find_all(['input', 'select', 'textarea'])
        ai_fields = soup.find_all(attrs={'data-ai-name': True})
        calculated_fields = soup.find_all(attrs={'data-calculated': 'true'})
        
        print(f"   • Forms: {len(forms)}")
        print(f"   • Tables: {len(tables)}")
        print(f"   • Input fields: {len(inputs)}")
        print(f"   • AI-enhanced fields: {len(ai_fields)}")
        print(f"   • Calculated fields: {len(calculated_fields)}")
        
        # Check for Jinja2 template syntax
        if '{% extends' in html:
            extends_match = html[html.find('{% extends'):html.find('%}', html.find('{% extends'))+2]
            print(f"   • Base template: {extends_match}")
        else:
            print(f"   • Base template: None (standalone)")
        
        if '{% block' in html:
            blocks = []
            import re
            for match in re.finditer(r'{%\s*block\s+(\w+)\s*%}', html):
                blocks.append(match.group(1))
            if blocks:
                print(f"   • Template blocks: {', '.join(blocks)}")
        
        # Save the template
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"\n✅ TEMPLATE SAVED SUCCESSFULLY")
        print(f"   Path: {template_path}")
        print(f"   URL route: /{template_path.relative_to(self.templates_dir).with_suffix('')}")
        
        # Show how to access it
        flask_route = str(template_path.relative_to(self.templates_dir).with_suffix('')).replace('\\', '/')
        if flask_route == 'index':
            flask_route = ''
        print(f"\n🌐 Access this page at:")
        print(f"   http://localhost:8080/{flask_route}")
        
        print("="*60 + "\n")
        
        return str(template_path)
        
    except Exception as e:
        print(f"\n❌ ERROR SAVING TEMPLATE: {e}")
        import traceback
        print(traceback.format_exc())
        return ""

# Monkey-patch this function into your agent class
print("""
📝 TO USE THIS ENHANCED LOGGING:

1. Add this to your agent after class initialization:

   from template_logging_patch import save_template_with_detailed_logging
   AIVIIZNRealAgent.save_template = save_template_with_detailed_logging

2. Or replace the save_template method in your agent directly with this code.

This will show you:
- Exact directory structure being created
- Full file paths 
- Template type detection
- Content analysis (forms, tables, AI fields)
- How to access the page via Flask
""")
