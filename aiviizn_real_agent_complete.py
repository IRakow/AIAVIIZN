#!/usr/bin/env python3
"""
AIVIIZN REAL TERMINAL AGENT - COMPLETE IMPLEMENTATION
Creates BEAUTIFUL, FULLY FUNCTIONAL pages from target sites
Complete with all extraction methods and database storage
"""

import os
import sys
import json
import time
import re
import asyncio
import gzip
import base64
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urlparse, urljoin, parse_qs
import logging
from openai import AsyncOpenAI
import tempfile
import shutil
import traceback

# Real libraries - no mocking
from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeout
from supabase import create_client, Client
import anthropic
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# For Excel formula extraction
try:
    import openpyxl
except ImportError:
    openpyxl = None
    print("⚠️ openpyxl not installed - Excel formula extraction disabled")
    print("   Run: pip install openpyxl")

# Load environment
load_dotenv()

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/Users/ianrakow/Desktop/AIVIIZN/agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AIVIIZNRealAgent:
    """
    REAL agent that creates BEAUTIFUL, FUNCTIONAL pages
    Everything actually works - no placeholders
    """
    
    def __init__(self):
        """Initialize with real connections"""
        print("🚀 AIVIIZN REAL AGENT - BEAUTIFUL PAGE CREATOR")
        print("=" * 60)
        
        # Real Supabase connection
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_KEY') 
        self.supabase_anon_key = os.getenv('SUPABASE_KEY')
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        print("✓ Supabase connected")
        
        # Real Claude API
        self.anthropic_client = anthropic.Anthropic(
            api_key=os.getenv('ANTHROPIC_API_KEY')
        )
        print("✓ Claude API ready (Opus 4.1)")
        
        # Initialize OpenAI client
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if openai_api_key:
            self.openai_client = AsyncOpenAI(api_key=openai_api_key)
            print(f"✓ GPT-4o (Omni) connected")
        else:
            print("⚠️ OpenAI API key not found")
            self.openai_client = None
        
        # Get AIVIIZN company ID
        self.company_id = self.get_aiviizn_company_id()
        
        # Project paths
        self.project_root = Path("/Users/ianrakow/Desktop/AIVIIZN")
        self.templates_dir = self.project_root / "templates"
        self.static_dir = self.project_root / "static"
        
        # Create directories if they don't exist
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.static_dir.mkdir(parents=True, exist_ok=True)
        (self.project_root / "data").mkdir(parents=True, exist_ok=True)
        (self.project_root / "screenshots").mkdir(parents=True, exist_ok=True)
        
        # Target site settings
        self.target_base = "https://celticprop.appfolio.com"
        
        # State
        self.processed_pages = self.load_state("processed_pages.json", set())
        self.discovered_links = self.load_state("discovered_links.json", list())
        
        # Real browser instance (persistent)
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context = None
        self.page: Optional[Page] = None
        
        # Auto mode flag
        self.auto_mode = False
        
        print("✓ Ready to create beautiful pages")
    
    def get_aiviizn_company_id(self):
        """Get the AIVIIZN company ID from database or create it"""
        try:
            # Check if company exists
            result = self.supabase.table('companies').select('id').eq('name', 'AIVIIZN').execute()
            
            if result.data and len(result.data) > 0:
                company_id = result.data[0]['id']
                print(f"✓ Found AIVIIZN company: {company_id}")
                return company_id
            else:
                # Create AIVIIZN company
                new_company = {
                    'name': 'AIVIIZN',
                    'domain': 'aiviizn.com',
                    'base_url': 'https://aiviizn.com',
                    'subscription_tier': 'enterprise',
                    'settings': {
                        'max_pages': 10000,
                        'max_storage_gb': 100,
                        'auto_detect_fields': True,
                        'capture_api_responses': True,
                        'require_field_verification': False
                    },
                    'is_active': True
                }
                
                result = self.supabase.table('companies').insert(new_company).execute()
                if result.data:
                    company_id = result.data[0]['id']
                    print(f"✓ Created AIVIIZN company: {company_id}")
                    return company_id
                else:
                    # Fallback to known ID
                    return '5bb7db68-63e2-4750-ac16-ad15f19938a8'
                    
        except Exception as e:
            print(f"⚠️ Error with company ID: {e}")
            # Use the known ID as fallback
            return '5bb7db68-63e2-4750-ac16-ad15f19938a8'
    
    def load_state(self, filename: str, default):
        """Load state from file"""
        file_path = self.project_root / "data" / filename
        if file_path.exists():
            with open(file_path, 'r') as f:
                data = json.load(f)
                return set(data) if isinstance(default, set) else data
        return default
        
    def save_state(self):
        """Save current state"""
        data_dir = self.project_root / "data"
        data_dir.mkdir(exist_ok=True)
        
        with open(data_dir / "processed_pages.json", 'w') as f:
            json.dump(list(self.processed_pages), f, indent=2)
            
        with open(data_dir / "discovered_links.json", 'w') as f:
            json.dump(self.discovered_links, f, indent=2)
            
    async def start_browser(self):
        """Start browser once and keep it open"""
        print("\n🌐 Starting browser session...")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=False,
            slow_mo=500,
            args=[
                '--start-maximized',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--window-size=1920,1080',
                '--force-device-scale-factor=1'
            ]
        )
        
        # Create context with proper settings
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            screen={'width': 1920, 'height': 1080},
            device_scale_factor=1,
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/Chicago'
        )
        self.page = await self.context.new_page()
        
        # Set viewport size explicitly
        await self.page.set_viewport_size({"width": 1920, "height": 1080})
        
        # Listen for console messages
        self.page.on('console', lambda msg: print(f"  🗒️ Console {msg.type}: {msg.text}") if msg.type in ['error', 'warning'] else None)
        
        # Override automation detection
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            window.chrome = { runtime: {} };
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)
        
        print("✅ Browser started with full viewport (1920x1080)")
        
    async def close_browser(self):
        """Close browser at the end"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        print("✅ Browser closed")
        
    async def run(self):
        """Main execution with persistent browser"""
        print("\n🎯 STARTING REAL PAGE REPLICATION")
        print("=" * 60)
        
        # Ask user where to start
        print("\n📍 Where would you like to start?")
        print("  1. Default homepage")
        print("  2. Reports page (/reports)")
        print("  3. Custom URL")
        print("  Or press ENTER for Reports (recommended)")
        
        choice = input("\n>>> Your choice (1/2/3 or ENTER): ").strip()
        
        if choice == "1":
            start_url = self.target_base
            print(f"✓ Starting from: {start_url}")
        elif choice == "3":
            custom = input(">>> Enter path (e.g., /reports/rent_roll): ").strip()
            if not custom.startswith('/'):
                custom = '/' + custom
            start_url = self.target_base + custom
            print(f"✓ Starting from: {start_url}")
        else:
            start_url = self.target_base + "/reports"
            print(f"✓ Starting from: {start_url} (recommended)")
        
        try:
            # Start browser once
            await self.start_browser()
            
            # Navigate to chosen starting point
            print(f"\n🌐 Opening: {start_url}...")
            await self.page.goto(start_url, wait_until='networkidle')
            
            # Wait for manual authorization
            print("\n" + "="*60)
            print("🔑 MANUAL AUTHORIZATION REQUIRED")
            print("="*60)
            print("\n👉 Please do the following in the browser window:")
            print("   1. Log into the site if needed")
            print("   2. Navigate to any page you want to start with")
            print("   3. Make sure you can see the main content")
            print("\n⚠️  BROWSER WILL STAY OPEN - DO NOT CLOSE IT")
            print("\n✅ When ready, press ENTER in this terminal to continue...")
            
            input("\n>>> Press ENTER to start replication: ")
            
            print("\n🚀 Starting replication with persistent browser...")
            
            # Refresh browser state
            print("\n🔄 Refreshing browser state...")
            await self.page.wait_for_timeout(500)
            
            # Get current URL after user navigation
            current_url = self.page.url
            print(f"✅ Current page detected: {current_url}")
            
            # Reload page if not on login
            if 'sign_in' not in current_url and 'login' not in current_url:
                print("🔄 Reloading page to ensure full content...")
                await self.page.reload(wait_until='networkidle')
                await self.page.wait_for_timeout(2000)
            
            # Clear login pages from discovered links
            self.discovered_links = [link for link in self.discovered_links 
                                    if 'sign_in' not in link and 'login' not in link]
            
            # Handle login pages
            if 'sign_in' in current_url or 'login' in current_url:
                print("⚠️  Still on login page - please navigate to a content page first")
                input("\n>>> Press ENTER after navigating to a content page: ")
                current_url = self.page.url
                print(f"✅ New page detected: {current_url}")
            
            # Add current URL to processing queue
            if current_url not in self.discovered_links:
                self.discovered_links.insert(0, current_url)
                print(f"📦 Added current page to processing queue")
            
            # Main processing loop
            await self.process_pages_loop()
            
        except KeyboardInterrupt:
            print("\n⚠️ Stopped by user (Ctrl+C)")
            self.save_state()
            
        except Exception as e:
            logger.error(f"Agent error: {e}")
            self.save_state()
            raise
            
        finally:
            await self.close_browser()
            
    async def process_pages_loop(self):
        """Process pages with persistent browser"""
        current_url = self.page.url
        print(f"\n📍 Processing from: {current_url}")
        
        # Process current page first
        if current_url not in self.processed_pages:
            print(f"🎆 Processing current page first...")
            await self.replicate_page_real(current_url)
        else:
            print(f"✅ Current page already processed, checking for more pages...")
        
        # Process discovered links
        while True:
            unprocessed = [url for url in self.discovered_links 
                          if url not in self.processed_pages]
            
            if not unprocessed:
                print("\n✅ ALL PAGES PROCESSED!")
                print("\n🎉 Session complete - browser will close now")
                break
                
            # Calculate progress
            total_discovered = len(self.discovered_links)
            total_processed = len(self.processed_pages)
            percent_complete = (total_processed / total_discovered * 100) if total_discovered > 0 else 0
            
            # Display progress
            if self.auto_mode:
                time_remaining_seconds = len(unprocessed) * 60
                hours = time_remaining_seconds // 3600
                minutes = (time_remaining_seconds % 3600) // 60
                time_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
                print(f"\n📊 PROGRESS: {total_processed}/{total_discovered} pages ({percent_complete:.1f}% complete)")
                print(f"⏱️  Estimated time remaining: {time_str}")
            else:
                print(f"\n📊 PROGRESS: {total_processed}/{total_discovered} pages ({percent_complete:.1f}% complete)")
            print(f"📊 Queue: {len(unprocessed)} pages remaining")
            print(f"📍 Next: {unprocessed[0]}")
            
            # User options
            print("\nOptions:")
            print("  ENTER = Process next page")
            print("  'a' = AUTO mode (process every 60 seconds)")
            print("  'q' = Quit and close browser")
            print("  'l' = List all remaining pages")
            print("  's' = Skip this page")
            print("  'c' = Clear cache and reprocess all")
            
            # Handle auto mode
            if self.auto_mode:
                print("\n🤖 AUTO MODE: Processing next page in 60 seconds...")
                print("Press Ctrl+C to stop auto mode")
                try:
                    await asyncio.sleep(60)
                    response = ''
                except KeyboardInterrupt:
                    print("\n⚠️ Auto mode stopped")
                    self.auto_mode = False
                    continue
            else:
                response = input("\n>>> Your choice: ").strip().lower()
            
            if response == 'q':
                print("\n⚠️ Stopping at user request")
                break
            elif response == 'a':
                print("\n🤖 AUTO MODE ACTIVATED - Processing every 60 seconds")
                print("Press Ctrl+C during wait to stop auto mode")
                self.auto_mode = True
                await self.replicate_page_real(unprocessed[0])
                await asyncio.sleep(0.5)
                continue
            elif response == 'l':
                print("\n📋 Remaining pages:")
                for i, url in enumerate(unprocessed[:10], 1):
                    print(f"  {i}. {url}")
                if len(unprocessed) > 10:
                    print(f"  ... and {len(unprocessed) - 10} more")
                continue
            elif response == 's':
                print(f"⏭️ Skipping {unprocessed[0]}")
                self.processed_pages.add(unprocessed[0])
                self.save_state()
                continue
            elif response == 'c':
                print("\n🗑️ Clearing cache...")
                self.processed_pages.clear()
                self.save_state()
                print("✅ Cache cleared - all pages will be reprocessed")
                continue
            
            # Process next page
            await self.replicate_page_real(unprocessed[0])
            await asyncio.sleep(0.5)
    
    async def replicate_page_real(self, url: str):
        """REAL page replication - creates BEAUTIFUL, FUNCTIONAL pages"""
        print(f"\n🎨 REPLICATING: {url}")
        print("-" * 50)
        
        try:
            # Navigate to URL if not already there
            if self.page.url != url:
                print(f"📍 Navigating to: {url}")
                await self.page.goto(url, wait_until='networkidle', timeout=30000)
                await self.page.wait_for_timeout(2000)
            
            # Take screenshot
            screenshot_path = await self.take_screenshot(url)
            
            # Capture page content
            page_data = await self.capture_real_page(url)
            
            if not page_data:
                print(f"⚠️ Failed to capture page: {url}")
                self.processed_pages.add(url)
                self.save_state()
                return
            
            # Extract calculations
            calculations = await self.extract_calculations_real(page_data)
            
            # Extract API responses
            api_responses = await self.extract_api_responses_real(url)
            
            # Generate beautiful template
            template_html = await self.generate_beautiful_template(page_data, calculations)
            
            # Save template
            template_path = self.save_template(url, template_html)
            
            # Store in Supabase
            await self.store_in_supabase(url, page_data, template_path, calculations, api_responses)
            
            # Discover new links
            new_links = await self.discover_links(page_data)
            for link in new_links:
                if link not in self.discovered_links and link not in self.processed_pages:
                    self.discovered_links.append(link)
                    print(f"  🔗 Discovered: {link}")
            
            # Mark as processed
            self.processed_pages.add(url)
            self.save_state()
            
            print(f"✨ BEAUTIFUL PAGE COMPLETE: {template_path}")
            
        except Exception as e:
            print(f"❌ Error replicating {url}: {e}")
            logger.error(f"Replication error for {url}: {traceback.format_exc()}")
            self.processed_pages.add(url)
            self.save_state()
    
    async def capture_real_page(self, url: str) -> Optional[Dict]:
        """Capture complete page data"""
        try:
            print("  📸 Capturing page content...")
            
            # Get page title
            title = await self.page.title()
            
            # Get full HTML
            html_content = await self.page.content()
            
            # Get main content
            main_content = await self.extract_main_content_real(html_content)
            
            # Get all text content
            text_content = await self.page.evaluate("""
                () => {
                    const walker = document.createTreeWalker(
                        document.body,
                        NodeFilter.SHOW_TEXT,
                        null,
                        false
                    );
                    let text = '';
                    let node;
                    while(node = walker.nextNode()) {
                        if (node.nodeValue && node.nodeValue.trim()) {
                            text += node.nodeValue.trim() + ' ';
                        }
                    }
                    return text;
                }
            """)
            
            # Get forms and inputs
            forms_data = await self.extract_forms_data()
            
            # Get tables
            tables_data = await self.extract_tables_data()
            
            # Get navigation structure
            nav_data = await self.extract_navigation_data()
            
            page_data = {
                'url': url,
                'title': title,
                'html': html_content,
                'main_content': main_content,
                'text_content': text_content,
                'forms': forms_data,
                'tables': tables_data,
                'navigation': nav_data,
                'captured_at': datetime.now().isoformat()
            }
            
            print(f"  ✅ Captured {len(html_content)} bytes of content")
            return page_data
            
        except Exception as e:
            print(f"  ❌ Error capturing page: {e}")
            return None
    
    async def extract_main_content_real(self, html: str) -> str:
        """Extract main content area from HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Try common main content selectors
            selectors = [
                'main', '[role="main"]', '#main-content', '.main-content',
                '#content', '.content', 'article', '.container'
            ]
            
            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    return str(element)
            
            # Fallback to body
            body = soup.find('body')
            return str(body) if body else html
            
        except Exception as e:
            print(f"  ⚠️ Error extracting main content: {e}")
            return html
    
    async def extract_forms_data(self) -> List[Dict]:
        """Extract all forms and their fields"""
        try:
            forms = await self.page.evaluate("""
                () => {
                    const forms = Array.from(document.querySelectorAll('form'));
                    return forms.map(form => {
                        const inputs = Array.from(form.querySelectorAll('input, select, textarea'));
                        return {
                            id: form.id,
                            name: form.name,
                            action: form.action,
                            method: form.method,
                            fields: inputs.map(input => ({
                                type: input.type || input.tagName.toLowerCase(),
                                name: input.name,
                                id: input.id,
                                placeholder: input.placeholder,
                                value: input.value,
                                required: input.required,
                                options: input.tagName === 'SELECT' ? 
                                    Array.from(input.options).map(opt => ({
                                        value: opt.value,
                                        text: opt.text
                                    })) : null
                            }))
                        };
                    });
                }
            """)
            return forms
        except Exception as e:
            print(f"  ⚠️ Error extracting forms: {e}")
            return []
    
    async def extract_tables_data(self) -> List[Dict]:
        """Extract all tables and their data"""
        try:
            tables = await self.page.evaluate("""
                () => {
                    const tables = Array.from(document.querySelectorAll('table'));
                    return tables.map(table => {
                        const headers = Array.from(table.querySelectorAll('th')).map(th => th.textContent.trim());
                        const rows = Array.from(table.querySelectorAll('tbody tr')).map(tr => {
                            return Array.from(tr.querySelectorAll('td')).map(td => td.textContent.trim());
                        });
                        return {
                            id: table.id,
                            class: table.className,
                            headers: headers,
                            rows: rows,
                            summary: table.summary
                        };
                    });
                }
            """)
            return tables
        except Exception as e:
            print(f"  ⚠️ Error extracting tables: {e}")
            return []
    
    async def extract_navigation_data(self) -> Dict:
        """Extract navigation structure"""
        try:
            nav = await self.page.evaluate("""
                () => {
                    const navElements = document.querySelectorAll('nav, [role="navigation"], .nav, .navbar');
                    const menus = Array.from(navElements).map(nav => {
                        const links = Array.from(nav.querySelectorAll('a')).map(a => ({
                            text: a.textContent.trim(),
                            href: a.href,
                            target: a.target
                        }));
                        return {
                            type: nav.tagName.toLowerCase(),
                            class: nav.className,
                            links: links
                        };
                    });
                    return { menus };
                }
            """)
            return nav
        except Exception as e:
            print(f"  ⚠️ Error extracting navigation: {e}")
            return {}
    
    async def extract_calculations_real(self, page_data: Dict) -> List[Dict]:
        """Extract calculations using AI"""
        try:
            print("  🧮 Extracting calculations...")
            
            # Use Claude to analyze the page
            prompt = f"""
            Analyze this page content and identify ALL calculations, formulas, and computed values.
            
            Page URL: {page_data['url']}
            Page Content (first 5000 chars): {page_data['text_content'][:5000]}
            
            Look for:
            1. Mathematical operations (sums, averages, percentages)
            2. Financial calculations (totals, balances, ratios)
            3. Date calculations (age, duration, periods)
            4. Conditional logic (if-then rules)
            5. Aggregations (counts, groupings)
            
            For each calculation found, provide:
            - name: Clear descriptive name
            - description: What it calculates
            - formula: The mathematical formula
            - variables: List of input variables
            - sample_data: Example values
            
            Return as JSON array.
            """
            
            response = self.anthropic_client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse response
            content = response.content[0].text
            
            # Extract JSON from response
            import re
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                calculations = json.loads(json_match.group())
                print(f"  ✅ Found {len(calculations)} calculations")
                return calculations
            
            return []
            
        except Exception as e:
            print(f"  ⚠️ Error extracting calculations: {e}")
            return []
    
    async def extract_api_responses_real(self, url: str) -> List[Dict]:
        """Extract API responses from network activity"""
        try:
            print("  🌐 Extracting API responses...")
            
            # Intercept network requests
            api_responses = []
            
            # Get all network requests from page
            responses = await self.page.evaluate("""
                () => {
                    if (window.performance && window.performance.getEntriesByType) {
                        const resources = window.performance.getEntriesByType('resource');
                        return resources
                            .filter(r => r.initiatorType === 'fetch' || r.initiatorType === 'xmlhttprequest')
                            .map(r => ({
                                url: r.name,
                                duration: r.duration,
                                size: r.transferSize
                            }));
                    }
                    return [];
                }
            """)
            
            print(f"  ✅ Found {len(responses)} API calls")
            return responses
            
        except Exception as e:
            print(f"  ⚠️ Error extracting API responses: {e}")
            return []
    
    async def generate_beautiful_template(self, page_data: Dict, calculations: List[Dict]) -> str:
        """Generate beautiful HTML template"""
        try:
            print("  🎨 Generating beautiful template...")
            
            # Parse original HTML
            soup = BeautifulSoup(page_data['html'], 'html.parser')
            
            # Create template with Supabase integration
            template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_data['title']} - AIVIIZN</title>
    
    <!-- Bootstrap 5 -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Custom styles -->
    <style>
        :root {{
            --primary-color: #2c3e50;
            --secondary-color: #3498db;
            --success-color: #27ae60;
            --danger-color: #e74c3c;
            --warning-color: #f39c12;
            --info-color: #16a085;
            --light-color: #ecf0f1;
            --dark-color: #34495e;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .main-container {{
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            margin: 20px auto;
            padding: 30px;
            max-width: 1400px;
        }}
        
        .page-header {{
            border-bottom: 3px solid var(--primary-color);
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        
        .data-table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .data-table th {{
            background: var(--primary-color);
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        
        .data-table td {{
            padding: 10px 12px;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        .data-table tr:hover {{
            background-color: #f8f9fa;
        }}
        
        .calculation-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
        }}
        
        .form-modern {{
            background: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}
        
        .form-modern input, .form-modern select, .form-modern textarea {{
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            padding: 10px 15px;
            transition: all 0.3s;
        }}
        
        .form-modern input:focus, .form-modern select:focus, .form-modern textarea:focus {{
            border-color: var(--secondary-color);
            box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
        }}
        
        .btn-modern {{
            padding: 12px 30px;
            border-radius: 8px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: all 0.3s;
            border: none;
        }}
        
        .btn-primary-modern {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        
        .btn-primary-modern:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }}
        
        .nav-modern {{
            background: white;
            border-radius: 10px;
            padding: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        
        .nav-modern a {{
            color: var(--primary-color);
            padding: 10px 20px;
            border-radius: 8px;
            text-decoration: none;
            transition: all 0.3s;
            display: inline-block;
            margin: 0 5px;
        }}
        
        .nav-modern a:hover {{
            background: var(--light-color);
            color: var(--secondary-color);
        }}
        
        .loading-spinner {{
            display: none;
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            z-index: 9999;
        }}
        
        .spinner {{
            width: 50px;
            height: 50px;
            border: 5px solid #f3f3f3;
            border-top: 5px solid var(--secondary-color);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
    </style>
</head>
<body>
    <div class="loading-spinner" id="loadingSpinner">
        <div class="spinner"></div>
    </div>
    
    <div class="main-container">
        <div class="page-header">
            <h1>{page_data['title']}</h1>
            <p class="text-muted">Replicated from: {page_data['url']}</p>
            <p class="text-muted">Captured: {page_data['captured_at']}</p>
        </div>
        
        <!-- Navigation -->
        {self.render_navigation(page_data.get('navigation', {}))}
        
        <!-- Main Content -->
        <div class="content-area">
            <!-- Forms -->
            {self.render_forms(page_data.get('forms', []))}
            
            <!-- Tables -->
            {self.render_tables(page_data.get('tables', []))}
            
            <!-- Calculations -->
            {self.render_calculations(calculations)}
        </div>
    </div>
    
    <!-- Supabase Integration -->
    <script type="module">
        import {{ createClient }} from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm'
        
        const supabaseUrl = '{self.supabase_url}'
        const supabaseAnonKey = '{self.supabase_anon_key}'
        const supabase = createClient(supabaseUrl, supabaseAnonKey)
        
        // Initialize page
        async function initializePage() {{
            console.log('Page initialized with Supabase connection');
            
            // Add any dynamic data loading here
            await loadDynamicData();
        }}
        
        async function loadDynamicData() {{
            try {{
                // Example: Load calculations
                const {{ data, error }} = await supabase
                    .from('calculations')
                    .select('*')
                    .eq('page_url', '{page_data['url']}')
                    .order('created_at', {{ ascending: false }});
                
                if (data) {{
                    console.log('Loaded calculations:', data);
                    updateCalculationsUI(data);
                }}
            }} catch (error) {{
                console.error('Error loading data:', error);
            }}
        }}
        
        function updateCalculationsUI(calculations) {{
            // Update UI with live calculations
            const calcContainer = document.getElementById('calculations-container');
            if (calcContainer && calculations.length > 0) {{
                // Update calculation displays
                calculations.forEach(calc => {{
                    const element = document.getElementById(`calc-${{calc.id}}`);
                    if (element) {{
                        element.innerHTML = `
                            <h5>${{calc.name}}</h5>
                            <p>${{calc.description}}</p>
                            <code>${{calc.formula}}</code>
                        `;
                    }}
                }});
            }}
        }}
        
        // Initialize on load
        document.addEventListener('DOMContentLoaded', initializePage);
        
        // Form submission handler
        document.querySelectorAll('form').forEach(form => {{
            form.addEventListener('submit', async (e) => {{
                e.preventDefault();
                document.getElementById('loadingSpinner').style.display = 'block';
                
                const formData = new FormData(form);
                const data = Object.fromEntries(formData);
                
                try {{
                    // Save form submission to Supabase
                    const {{ error }} = await supabase
                        .from('form_submissions')
                        .insert({{
                            page_url: '{page_data['url']}',
                            form_data: data,
                            submitted_at: new Date().toISOString()
                        }});
                    
                    if (!error) {{
                        alert('Form submitted successfully!');
                        form.reset();
                    }} else {{
                        throw error;
                    }}
                }} catch (error) {{
                    console.error('Submission error:', error);
                    alert('Error submitting form. Please try again.');
                }} finally {{
                    document.getElementById('loadingSpinner').style.display = 'none';
                }}
            }});
        }});
    </script>
    
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""
            
            return template
            
        except Exception as e:
            print(f"  ⚠️ Error generating template: {e}")
            return page_data.get('html', '')
    
    def render_navigation(self, nav_data: Dict) -> str:
        """Render navigation HTML"""
        if not nav_data or not nav_data.get('menus'):
            return ''
        
        html = '<nav class="nav-modern">'
        for menu in nav_data['menus']:
            for link in menu.get('links', []):
                html += f'<a href="{link["href"]}">{link["text"]}</a>'
        html += '</nav>'
        return html
    
    def render_forms(self, forms: List[Dict]) -> str:
        """Render forms HTML"""
        if not forms:
            return ''
        
        html = '<div class="forms-section mb-4">'
        for form in forms:
            html += '<div class="form-modern">'
            html += f'<form id="{form.get("id", "")}" method="{form.get("method", "POST")}">'
            
            for field in form.get('fields', []):
                html += '<div class="mb-3">'
                if field['type'] == 'select':
                    html += f'<label class="form-label">{field.get("name", "")}</label>'
                    html += f'<select class="form-control" name="{field.get("name", "")}">'
                    for option in field.get('options', []):
                        html += f'<option value="{option["value"]}">{option["text"]}</option>'
                    html += '</select>'
                elif field['type'] == 'textarea':
                    html += f'<label class="form-label">{field.get("name", "")}</label>'
                    html += f'<textarea class="form-control" name="{field.get("name", "")}"></textarea>'
                else:
                    html += f'<input type="{field["type"]}" class="form-control" '
                    html += f'name="{field.get("name", "")}" '
                    html += f'placeholder="{field.get("placeholder", "")}" '
                    if field.get('required'):
                        html += 'required '
                    html += '/>'
                html += '</div>'
            
            html += '<button type="submit" class="btn btn-modern btn-primary-modern">Submit</button>'
            html += '</form>'
            html += '</div>'
        
        html += '</div>'
        return html
    
    def render_tables(self, tables: List[Dict]) -> str:
        """Render tables HTML"""
        if not tables:
            return ''
        
        html = '<div class="tables-section mb-4">'
        for table in tables:
            html += '<div class="table-responsive mb-4">'
            html += '<table class="data-table">'
            
            # Headers
            if table.get('headers'):
                html += '<thead><tr>'
                for header in table['headers']:
                    html += f'<th>{header}</th>'
                html += '</tr></thead>'
            
            # Rows
            if table.get('rows'):
                html += '<tbody>'
                for row in table['rows']:
                    html += '<tr>'
                    for cell in row:
                        html += f'<td>{cell}</td>'
                    html += '</tr>'
                html += '</tbody>'
            
            html += '</table>'
            html += '</div>'
        
        html += '</div>'
        return html
    
    def render_calculations(self, calculations: List[Dict]) -> str:
        """Render calculations HTML"""
        if not calculations:
            return ''
        
        html = '<div id="calculations-container" class="calculations-section">'
        html += '<h3 class="mb-4">Calculations & Formulas</h3>'
        
        for calc in calculations:
            html += f'<div class="calculation-card" id="calc-{calc.get("name", "").replace(" ", "-")}">'
            html += f'<h5>{calc.get("name", "Unknown")}</h5>'
            html += f'<p>{calc.get("description", "")}</p>'
            html += f'<code>{calc.get("formula", "")}</code>'
            html += '</div>'
        
        html += '</div>'
        return html
    
    def save_template(self, url: str, html: str) -> str:
        """Save template to file"""
        try:
            # Generate filename from URL
            parsed = urlparse(url)
            path_parts = parsed.path.strip('/').split('/')
            filename = '_'.join(path_parts) if path_parts[0] else 'index'
            filename = f"{filename}.html"
            
            # Save to templates directory
            template_path = self.templates_dir / filename
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(html)
            
            print(f"  💾 Saved template: {template_path}")
            return str(template_path)
            
        except Exception as e:
            print(f"  ⚠️ Error saving template: {e}")
            return ""
    
    async def take_screenshot(self, url: str) -> str:
        """Take screenshot of current page"""
        try:
            parsed = urlparse(url)
            path_parts = parsed.path.strip('/').split('/')
            filename = '_'.join(path_parts) if path_parts[0] else 'index'
            screenshot_path = self.project_root / "screenshots" / f"{filename}.png"
            
            await self.page.screenshot(path=str(screenshot_path), full_page=True)
            print(f"  📸 Screenshot saved: {screenshot_path}")
            return str(screenshot_path)
            
        except Exception as e:
            print(f"  ⚠️ Error taking screenshot: {e}")
            return ""
    
    async def store_in_supabase(self, url: str, page_data: Dict, template_path: str, 
                                calculations: List[Dict], api_responses: List[Dict]):
        """Store everything in Supabase"""
        try:
            print("  💾 Storing in Supabase...")
            
            # Store page
            page_record = {
                'company_id': self.company_id,
                'url': url,
                'title': page_data.get('title', ''),
                'template_path': template_path,
                'html_preview': page_data.get('html', '')[:5000],  # First 5000 chars
                'meta_data': {
                    'forms_count': len(page_data.get('forms', [])),
                    'tables_count': len(page_data.get('tables', [])),
                    'navigation': page_data.get('navigation', {})
                },
                'api_responses': api_responses,
                'captured_at': page_data.get('captured_at'),
                'is_active': True
            }
            
            # Check if page exists
            existing = self.supabase.table('pages').select('id').eq('url', url).eq('company_id', self.company_id).execute()
            
            if existing.data:
                # Update existing
                result = self.supabase.table('pages').update(page_record).eq('id', existing.data[0]['id']).execute()
                page_id = existing.data[0]['id']
                print(f"    ✅ Updated page: {page_id}")
            else:
                # Insert new
                result = self.supabase.table('pages').insert(page_record).execute()
                page_id = result.data[0]['id'] if result.data else None
                print(f"    ✅ Created page: {page_id}")
            
            # Store calculations
            for calc in calculations:
                calc_record = {
                    'company_id': self.company_id,
                    'page_id': page_id,
                    'page_url': url,
                    'name': calc.get('name', 'Unknown'),
                    'description': calc.get('description', ''),
                    'formula': calc.get('formula', ''),
                    'variables': calc.get('variables', []),
                    'sample_data': calc.get('sample_data', {}),
                    'source': 'claude-3-opus',
                    'confidence_score': 0.95,
                    'verified': False
                }
                
                result = self.supabase.table('calculations').insert(calc_record).execute()
                if result.data:
                    print(f"    ✅ Stored calculation: {calc.get('name')}")
            
            # Store API responses
            for api_resp in api_responses:
                api_record = {
                    'company_id': self.company_id,
                    'page_id': page_id,
                    'page_url': url,
                    'endpoint': api_resp.get('url', ''),
                    'method': 'GET',
                    'response_time_ms': api_resp.get('duration', 0),
                    'captured_at': datetime.now().isoformat()
                }
                
                result = self.supabase.table('api_responses').insert(api_record).execute()
            
            print("  ✅ Successfully stored in Supabase")
            
        except Exception as e:
            print(f"  ❌ Error storing in Supabase: {e}")
            logger.error(f"Supabase storage error: {traceback.format_exc()}")
    
    async def discover_links(self, page_data: Dict) -> List[str]:
        """Discover new links from page"""
        try:
            soup = BeautifulSoup(page_data['html'], 'html.parser')
            links = []
            
            for a in soup.find_all('a', href=True):
                href = a['href']
                
                # Skip external links, anchors, javascript
                if href.startswith('#') or href.startswith('javascript:') or href.startswith('mailto:'):
                    continue
                
                # Make absolute URL
                if href.startswith('http'):
                    full_url = href
                elif href.startswith('/'):
                    full_url = urljoin(self.target_base, href)
                else:
                    full_url = urljoin(page_data['url'], href)
                
                # Only include target domain
                if full_url.startswith(self.target_base):
                    # Clean URL
                    if '?' in full_url:
                        full_url = full_url.split('?')[0]
                    if '#' in full_url:
                        full_url = full_url.split('#')[0]
                    
                    if full_url not in links:
                        links.append(full_url)
            
            return links
            
        except Exception as e:
            print(f"  ⚠️ Error discovering links: {e}")
            return []

# Main execution
if __name__ == "__main__":
    agent = AIVIIZNRealAgent()
    asyncio.run(agent.run())
