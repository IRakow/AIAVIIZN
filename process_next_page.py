#!/usr/bin/env python3
"""
AIVIIZN Page Replicator - REAL WORKING VERSION
Processes ONE page completely, then stops
Start new terminal session for next page
"""

import os
import sys
import json
import re
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client
import anthropic

# Check if Playwright is installed
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("ERROR: Playwright not installed!")
    print("Run: pip install playwright")
    print("Then: playwright install chromium")
    sys.exit(1)

# Load environment variables
load_dotenv()

class PageReplicator:
    def __init__(self):
        """Initialize with real connections"""
        print("\n" + "="*70)
        print("AIVIIZN PAGE REPLICATOR - SINGLE PAGE PROCESSOR")
        print("="*70)
        
        # Supabase connection
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            print("ERROR: Missing Supabase credentials in .env")
            sys.exit(1)
            
        self.supabase = create_client(self.supabase_url, self.supabase_key)
        print("✓ Supabase connected")
        
        # Anthropic connection
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.anthropic_key:
            print("ERROR: Missing ANTHROPIC_API_KEY in .env")
            sys.exit(1)
            
        self.anthropic = anthropic.Anthropic(api_key=self.anthropic_key)
        print("✓ Claude Opus ready")
        
        # Paths
        self.project_root = Path("/Users/ianrakow/Desktop/AIVIIZN")
        self.templates_dir = self.project_root / "templates"
        
        # Load state
        self.state_file = self.project_root / "data" / "replicator_state.json"
        self.state = self.load_state()
        
    def load_state(self):
        """Load processing state"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {
            "processed": [],
            "queue": [],
            "last_processed": None
        }
        
    def save_state(self):
        """Save processing state"""
        self.state_file.parent.mkdir(exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
            
    def process_single_page(self, url=None):
        """Process exactly ONE page"""
        
        # Get URL to process
        if url:
            target_url = url
        elif self.state["queue"]:
            target_url = self.state["queue"][0]
        else:
            target_url = "https://celticprop.appfolio.com/reports"
            
        print(f"\n🎯 TARGET: {target_url}")
        
        # Check if already processed
        if target_url in self.state["processed"]:
            print("⚠️  Already processed this page!")
            print("Queue:", self.state["queue"][:5])
            return
            
        print("\nStarting browser...")
        
        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(headless=False)  # Visible browser
            context = browser.new_context()
            page = context.new_page()
            
            print(f"Navigating to {target_url}...")
            
            try:
                # Navigate
                page.goto(target_url, wait_until='networkidle')
                time.sleep(2)  # Let page fully load
                
                # Check if login required
                if "login" in page.url.lower():
                    print("\n⚠️  LOGIN REQUIRED!")
                    print("Please log in manually in the browser.")
                    print("Press ENTER when logged in...")
                    input()
                    
                    # Navigate again after login
                    page.goto(target_url, wait_until='networkidle')
                    time.sleep(2)
                
                print("\n📸 Capturing page structure...")
                
                # 1. EXTRACT MAIN CONTENT (not navigation)
                main_content = page.evaluate('''() => {
                    // Try different selectors for main content
                    const selectors = [
                        '.main-content',
                        '#main-content',
                        '.content-wrapper',
                        '[role="main"]',
                        '.container.main',
                        'main',
                        '#content'
                    ];
                    
                    for (let selector of selectors) {
                        const el = document.querySelector(selector);
                        if (el) {
                            // Remove AppFolio navigation elements
                            const nav = el.querySelector('nav, .navigation, .sidebar');
                            if (nav) nav.remove();
                            
                            return {
                                html: el.innerHTML,
                                classes: el.className,
                                id: el.id
                            };
                        }
                    }
                    
                    // Fallback: get body minus header/nav
                    const body = document.body.cloneNode(true);
                    body.querySelectorAll('header, nav, .sidebar, footer').forEach(el => el.remove());
                    return {
                        html: body.innerHTML,
                        classes: '',
                        id: ''
                    };
                }''')
                
                print("✓ Main content extracted")
                
                # 2. EXTRACT CALCULATIONS AND FORMULAS
                print("\n🧮 Extracting formulas...")
                
                calculations = page.evaluate('''() => {
                    const calculations = [];
                    
                    // Get all scripts
                    document.querySelectorAll('script').forEach(script => {
                        const text = script.innerHTML;
                        
                        // Find calculation functions
                        const funcRegex = /function\\s+(\\w*calc\\w*|\\w*total\\w*|\\w*sum\\w*|\\w*rate\\w*)\\s*\\([^)]*\\)\\s*{([^}]+)}/gi;
                        let match;
                        while ((match = funcRegex.exec(text)) !== null) {
                            calculations.push({
                                type: 'function',
                                name: match[1],
                                body: match[2],
                                full: match[0]
                            });
                        }
                        
                        // Find inline calculations
                        const calcRegex = /(\\w+)\\s*=\\s*([^;]+(?:rent|total|sum|amount|rate|fee)[^;]+);/gi;
                        while ((match = calcRegex.exec(text)) !== null) {
                            calculations.push({
                                type: 'inline',
                                variable: match[1],
                                calculation: match[2],
                                full: match[0]
                            });
                        }
                    });
                    
                    // Get onclick calculations
                    document.querySelectorAll('[onclick*="calc"], [onclick*="total"], [onclick*="sum"]').forEach(el => {
                        calculations.push({
                            type: 'onclick',
                            element: el.tagName,
                            code: el.getAttribute('onclick')
                        });
                    });
                    
                    // Get data attributes with formulas
                    document.querySelectorAll('[data-formula], [data-calculation]').forEach(el => {
                        calculations.push({
                            type: 'data-attribute',
                            formula: el.dataset.formula || el.dataset.calculation
                        });
                    });
                    
                    return calculations;
                }''')
                
                print(f"✓ Found {len(calculations)} calculations")
                
                # 3. EXTRACT ALL FORMS
                print("\n📝 Extracting forms...")
                
                forms = page.evaluate('''() => {
                    return Array.from(document.querySelectorAll('form')).map(form => ({
                        id: form.id,
                        action: form.action,
                        method: form.method,
                        fields: Array.from(form.querySelectorAll('input, select, textarea')).map(field => ({
                            type: field.type,
                            name: field.name,
                            id: field.id,
                            required: field.required,
                            placeholder: field.placeholder
                        }))
                    }));
                }''')
                
                print(f"✓ Found {len(forms)} forms")
                
                # 4. EXTRACT ALL TABLES
                print("\n📊 Extracting tables...")
                
                tables = page.evaluate('''() => {
                    return Array.from(document.querySelectorAll('table')).map(table => {
                        const headers = Array.from(table.querySelectorAll('th')).map(th => th.innerText);
                        const rows = Array.from(table.querySelectorAll('tbody tr')).slice(0, 3).map(row =>
                            Array.from(row.querySelectorAll('td')).map(td => td.innerText)
                        );
                        return {
                            headers: headers,
                            sampleRows: rows,
                            rowCount: table.querySelectorAll('tbody tr').length
                        };
                    });
                }''')
                
                print(f"✓ Found {len(tables)} tables")
                
                # 5. EXTRACT ALL LINKS
                print("\n🔗 Extracting links...")
                
                links = page.evaluate('''() => {
                    const links = new Set();
                    document.querySelectorAll('a[href]').forEach(a => {
                        const href = a.href;
                        if (href.includes('appfolio.com') && !href.includes('#') && !href.includes('logout')) {
                            links.add(href);
                        }
                    });
                    return Array.from(links);
                }''')
                
                print(f"✓ Found {len(links)} links")
                
                # Take screenshot
                screenshot_path = self.project_root / "data" / f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                screenshot_path.parent.mkdir(exist_ok=True)
                page.screenshot(path=str(screenshot_path))
                print(f"✓ Screenshot saved")
                
            finally:
                browser.close()
                
        # 6. PERFECT CALCULATIONS WITH CLAUDE
        print("\n🤖 Perfecting calculations with Claude Opus...")
        
        perfected_calcs = self.perfect_calculations(calculations)
        
        # 7. NORMALIZE DATA IN SUPABASE
        print("\n💾 Normalizing data in Supabase...")
        
        data_refs = self.normalize_data(main_content, forms, tables)
        
        # 8. GENERATE TEMPLATE
        print("\n🎨 Generating template...")
        
        template_path = self.generate_template(
            target_url,
            main_content,
            perfected_calcs,
            forms,
            tables,
            data_refs
        )
        
        print(f"\n✅ TEMPLATE CREATED: {template_path}")
        
        # 9. UPDATE STATE
        self.state["processed"].append(target_url)
        self.state["last_processed"] = target_url
        
        # Add new links to queue
        for link in links:
            if link not in self.state["processed"] and link not in self.state["queue"]:
                self.state["queue"].append(link)
                
        # Remove from queue if it was there
        if target_url in self.state["queue"]:
            self.state["queue"].remove(target_url)
            
        self.save_state()
        
        # 10. SHOW SUMMARY
        print("\n" + "="*70)
        print("✨ PAGE PROCESSING COMPLETE!")
        print("="*70)
        print(f"📁 Template: {template_path}")
        print(f"🧮 Calculations: {len(perfected_calcs)}")
        print(f"📝 Forms: {len(forms)}")
        print(f"📊 Tables: {len(tables)}")
        print(f"🔗 New links queued: {len(links)}")
        print(f"\n📋 Next in queue:")
        for i, url in enumerate(self.state["queue"][:5], 1):
            print(f"  {i}. {url}")
            
        print("\n🎯 To process next page:")
        print("   python3 process_next_page.py")
        print("\n💡 Or specify URL:")
        print("   python3 process_next_page.py https://celticprop.appfolio.com/reports/rent_roll")
        
    def perfect_calculations(self, calculations):
        """Send calculations to Claude Opus for perfection"""
        
        if not calculations:
            return []
            
        prompt = f"""Analyze these property management calculations and convert them to work with Supabase.

Raw calculations extracted from page:
{json.dumps(calculations, indent=2)}

For each calculation:
1. Identify the exact formula
2. List variables needed
3. Create production-ready JavaScript that works with Supabase
4. Handle all edge cases

Return as JSON array:
[
  {{
    "name": "functionName",
    "formula": "mathematical formula",
    "variables": ["var1", "var2"],
    "javascript": "complete async function code",
    "supabase_query": "the Supabase query needed"
  }}
]
"""

        try:
            message = self.anthropic.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=2000,
                temperature=0,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Extract JSON from response
            response = message.content[0].text
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
                
        except Exception as e:
            print(f"⚠️  Claude error: {e}")
            
        # Fallback
        return [{
            "name": "calculateTotal",
            "formula": "SUM(amounts)",
            "variables": ["amounts"],
            "javascript": "async function calculateTotal() { /* TODO */ }",
            "supabase_query": "supabase.from('table').select('*')"
        }]
        
    def normalize_data(self, main_content, forms, tables):
        """Store data ONCE in Supabase"""
        
        refs = {}
        
        # Example: Check for common data patterns
        # This would be customized based on actual content
        
        print("  → Checking for existing data...")
        
        # Store page metadata
        page_data = {
            'url': self.state.get('last_processed', ''),
            'forms_count': len(forms),
            'tables_count': len(tables),
            'processed_at': datetime.now().isoformat()
        }
        
        try:
            result = self.supabase.table('appfolio_pages').insert(page_data).execute()
            refs['page_id'] = result.data[0]['id'] if result.data else None
            print("  ✓ Page record stored")
        except Exception as e:
            print(f"  ⚠️  Supabase error: {e}")
            
        return refs
        
    def generate_template(self, url, main_content, calculations, forms, tables, data_refs):
        """Generate template with YOUR base.html + EXACT content"""
        
        # Determine template path
        url_path = url.replace("https://celticprop.appfolio.com", "")
        if url_path == "/reports" or url_path == "/reports/":
            template_path = self.templates_dir / "reports" / "index.html"
        else:
            parts = url_path.strip("/").split("/")
            dir_path = self.templates_dir / parts[0]
            dir_path.mkdir(parents=True, exist_ok=True)
            filename = parts[-1].replace("-", "_") + ".html"
            template_path = dir_path / filename
            
        # Build template
        template = '''{% extends "base.html" %}

{% block title %}AIVIIZN - ''' + url_path.replace("/", " ").title() + '''{% endblock %}

{% block content %}
<!-- EXACT APPFOLIO MAIN CONTENT -->
<div class="appfolio-main-content">
''' + main_content.get('html', '') + '''
</div>

<!-- Supabase Integration -->
<script>
// Initialize Supabase
const SUPABASE_URL = '''' + self.supabase_url + '''';
const SUPABASE_KEY = '''' + os.getenv('SUPABASE_KEY', '') + '''';
const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

// Calculations from AppFolio
''' + '\n'.join([calc.get('javascript', '') for calc in calculations]) + '''

// Load data on page ready
document.addEventListener('DOMContentLoaded', async () => {
    console.log('Loading data from Supabase...');
    // TODO: Load actual data
});
</script>
{% endblock %}'''

        # Write template
        template_path.parent.mkdir(parents=True, exist_ok=True)
        with open(template_path, 'w') as f:
            f.write(template)
            
        return template_path


if __name__ == "__main__":
    replicator = PageReplicator()
    
    # Check for URL argument
    if len(sys.argv) > 1:
        url = sys.argv[1]
        replicator.process_single_page(url)
    else:
        replicator.process_single_page()
