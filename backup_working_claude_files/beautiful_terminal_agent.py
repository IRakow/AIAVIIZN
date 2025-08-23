#!/usr/bin/env python3
"""
ENHANCED AIVIIZN Terminal Agent - Beautiful AppFolio Replication
Creates pixel-perfect AIVIIZN templates with exact AppFolio styling and functionality
"""

import os
import sys
import json
import time
import asyncio
import logging
import signal
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, urljoin
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Set

# Import required libraries
from playwright.async_api import async_playwright, Browser, Page
import openai
import anthropic
import google.generativeai as genai
import requests
from supabase import create_client, Client
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

@dataclass
class PageData:
    url: str
    title: str
    html_content: str
    screenshot_path: str
    calculations: List[Dict]
    links_discovered: List[str]
    page_type: str
    ai_analysis: Dict
    timestamp: str

class PersistentBrowserManager:
    """Browser manager that NEVER closes - stays open entire session"""
    
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.is_running = True
        self._initialized = False
        
        # Setup graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown gracefully"""
        print("\n🛑 Graceful shutdown initiated...")
        self.is_running = False
        asyncio.create_task(self.cleanup())
    
    async def initialize_browser(self):
        """Initialize browser once - stays open forever"""
        if self._initialized:
            return True
            
        try:
            print("🚀 Initializing persistent browser session...")
            self.playwright = await async_playwright().start()
            
            self.browser = await self.playwright.chromium.launch(
                headless=False,  # Always visible
                args=[
                    '--start-maximized',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--no-first-run'
                ]
            )
            
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            
            self.page = await self.context.new_page()
            self._initialized = True
            print("🌐 Browser session established - WILL REMAIN OPEN")
            return True
            
        except Exception as e:
            logging.error(f"Failed to initialize browser: {e}")
            return False
    
    async def navigate_and_process(self, url):
        """Navigate to URL and return page for processing"""
        try:
            if not self._initialized:
                await self.initialize_browser()
            
            print(f"🔗 Navigating to: {url}")
            
            response = await self.page.goto(url, wait_until='networkidle', timeout=30000)
            await self.page.wait_for_load_state('domcontentloaded')
            await asyncio.sleep(2)  # Let dynamic content load
            
            print(f"✅ Successfully navigated to: {url}")
            return self.page
            
        except Exception as e:
            logging.error(f"Error navigating to {url}: {e}")
            return None
    
    async def wait_for_login(self):
        """Pause for manual login"""
        print("🔐 Please log in manually in the browser window (if needed)")
        print("Press Enter when you're logged in and ready to start processing...")
        input()
        print("▶️ Starting processing...")
    
    async def cleanup(self):
        """Clean up only on shutdown"""
        try:
            print("🧹 Cleaning up browser session...")
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            print("✅ Browser cleaned up")
        except Exception as e:
            logging.error(f"Error during cleanup: {e}")

class AIViizNTerminalAgent:
    """Enhanced terminal agent for beautiful AppFolio replication"""
    
    def __init__(self):
        self.setup_logging()
        self.load_environment()
        self.setup_ai_clients()
        self.setup_supabase()
        
        self.browser_manager = PersistentBrowserManager()
        self.processed_urls = set()
        self.pending_urls = []
        self.session_start = datetime.now()
        
        # File paths
        self.links_file = "discovered_links.json"
        self.session_file = f"session_data/session_{self.session_start.strftime('%Y%m%d_%H%M%S')}.json"
        
        # Load existing data
        self.load_session_data()
    
    def setup_logging(self):
        """Configure logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('terminal_agent.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_environment(self):
        """Load API keys from environment"""
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        self.gemini_key = os.getenv('GEMINI_API_KEY')
        self.wolfram_key = os.getenv('WOLFRAM_APP_ID')
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
        
        if not all([self.openai_key, self.anthropic_key, self.gemini_key, self.supabase_url, self.supabase_key]):
            print("⚠️ Missing API keys in .env file")
    
    def setup_ai_clients(self):
        """Initialize AI service clients"""
        try:
            self.openai_client = openai.OpenAI(api_key=self.openai_key)
            self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_key)
            genai.configure(api_key=self.gemini_key)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
            print("🤖 AI clients initialized")
        except Exception as e:
            print(f"⚠️ Error setting up AI clients: {e}")
    
    def setup_supabase(self):
        """Initialize Supabase client"""
        try:
            self.supabase = create_client(self.supabase_url, self.supabase_key)
            print("🗄️ Supabase connected")
        except Exception as e:
            print(f"⚠️ Error connecting to Supabase: {e}")
    
    def load_session_data(self):
        """Load existing links and session data"""
        try:
            if os.path.exists(self.links_file):
                with open(self.links_file, 'r') as f:
                    data = json.load(f)
                    self.processed_urls = set(data.get('processed', []))
                    self.pending_urls = data.get('pending', [])
                    print(f"📊 Loaded {len(self.processed_urls)} processed, {len(self.pending_urls)} pending URLs")
        except Exception as e:
            print(f"⚠️ Error loading session data: {e}")
    
    def save_session_data(self):
        """Save current session state"""
        try:
            data = {
                'processed': list(self.processed_urls),
                'pending': self.pending_urls,
                'session_start': self.session_start.isoformat(),
                'last_update': datetime.now().isoformat()
            }
            
            with open(self.links_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            with open(self.session_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"⚠️ Error saving session data: {e}")
    
    async def start_processing(self, start_url=None):
        """Start the main processing loop"""
        
        # Initialize browser
        await self.browser_manager.initialize_browser()
        
        # Set starting URL
        if not start_url:
            start_url = "https://celticprop.appfolio.com/reports"
        
        if start_url not in self.pending_urls and start_url not in self.processed_urls:
            self.pending_urls.append(start_url)
        
        print(f"\n🎯 AIVIIZN Terminal Agent Started")
        print(f"📍 Starting URL: {start_url}")
        print(f"🔄 Browser will stay open - use Ctrl+C to exit")
        print(f"📊 Current status: {len(self.processed_urls)} processed, {len(self.pending_urls)} pending")
        
        # Always wait for manual confirmation before processing
        await self.browser_manager.navigate_and_process(start_url)
        await self.browser_manager.wait_for_login()
        
        try:
            while self.browser_manager.is_running and self.pending_urls and len(self.processed_urls) < 30:
                current_url = self.pending_urls.pop(0)
                
                if current_url not in self.processed_urls:
                    await self.process_page(current_url)
                    self.processed_urls.add(current_url)
                    self.save_session_data()
                    
                    # Brief pause
                    await asyncio.sleep(2)
                
                print(f"📊 Progress: {len(self.processed_urls)} processed, {len(self.pending_urls)} pending")
            
            if not self.pending_urls:
                print("\n✅ All pages processed!")
                print("🌐 Browser staying open for manual inspection")
                print("Press Enter to continue or Ctrl+C to exit...")
                input()
        
        except Exception as e:
            self.logger.error(f"Error in processing loop: {e}")
        finally:
            await self.browser_manager.cleanup()
    
    async def process_page(self, url):
        """Process individual page"""
        try:
            print(f"\n🔍 Processing: {url}")
            
            page = await self.browser_manager.navigate_and_process(url)
            if not page:
                return
            
            # Analyze page
            page_data = await self.analyze_page(page, url)
            
            # Generate beautiful AIVIIZN template
            await self.generate_beautiful_template(page_data)
            
            # Store in database
            await self.store_page_data(page_data)
            
            print(f"✅ Completed: {url}")
            
        except Exception as e:
            self.logger.error(f"Error processing {url}: {e}")
    
    async def analyze_page(self, page, url):
        """Analyze page content with AI"""
        try:
            # Get basic page info
            title = await page.title()
            content = await page.content()
            
            # Take screenshot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"screenshots/{title.replace(' ', '_').replace('/', '_')}_{timestamp}.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            
            # Extract links
            links = await page.eval_on_selector_all(
                'a[href]', 
                'elements => elements.map(el => el.href)'
            )
            
            # Filter AppFolio links
            new_links = []
            for link in links:
                if ('appfolio.com' in link and 
                    link not in self.processed_urls and 
                    link not in self.pending_urls):
                    new_links.append(link)
                    self.pending_urls.append(link)
            
            # Extract calculations and interactive elements
            calculations = await self.extract_calculations(page)
            
            # AI analysis
            ai_analysis = await self.get_ai_analysis(content, title, url)
            
            # Determine page type
            page_type = self.determine_page_type(url, title)
            
            page_data = PageData(
                url=url,
                title=title,
                html_content=content,
                screenshot_path=screenshot_path,
                calculations=calculations,
                links_discovered=new_links,
                page_type=page_type,
                ai_analysis=ai_analysis,
                timestamp=timestamp
            )
            
            print(f"📊 Analyzed: {title} - Found {len(new_links)} new links, {len(calculations)} calculations")
            
            return page_data
            
        except Exception as e:
            self.logger.error(f"Error analyzing page: {e}")
            return None
    
    def extract_main_content(self, soup):
        """Extract the main content area from AppFolio page"""
        # Look for main content containers
        main_selectors = [
            'main', '.main-container', '.page-content', '.content-wrapper',
            '#content', '.buffered-report', '.report-content', '[role="main"]'
        ]
        
        for selector in main_selectors:
            main_element = soup.select_one(selector)
            if main_element:
                # Clean up the content for AIVIIZN
                return self.clean_appfolio_content(main_element)
        
        # Fallback: get body content
        body = soup.find('body')
        if body:
            return self.clean_appfolio_content(body)
        
        return "<div><!-- Main content could not be extracted --></div>"
    
    def clean_appfolio_content(self, element):
        """Clean AppFolio content and prepare for AIVIIZN"""
        # Remove script tags and unwanted elements
        for script in element.find_all(['script', 'noscript']):
            script.decompose()
        
        # Replace AppFolio branding with AIVIIZN
        html_str = str(element)
        replacements = {
            'AppFolio': 'AIVIIZN',
            'appfolio': 'aiviizn',
            'Celtic Property': 'AIVIIZN',
            'celticprop': 'aiviizn'
        }
        
        for old, new in replacements.items():
            html_str = html_str.replace(old, new)
        
        return html_str
    
    def convert_appfolio_to_aiviizn(self, content):
        """Convert AppFolio styling to AIVIIZN"""
        # Add AIVIIZN classes and styling
        content = content.replace('class="', 'class="aiviizn-')
        
        # Convert AppFolio specific classes to AIVIIZN equivalents
        class_mappings = {
            'btn-primary': 'btn-appfolio',
            'table-striped': 'data-grid',
            'form-control': 'aiviizn-input',
            'card': 'aiviizn-card'
        }
        
        for old_class, new_class in class_mappings.items():
            content = content.replace(old_class, new_class)
        
        return content
    
    def extract_and_convert_forms(self, soup):
        """Extract and convert forms to AIVIIZN format"""
        forms = soup.find_all('form')
        forms_html = ""
        
        for form in forms:
            # Convert form to AIVIIZN format
            form_html = str(form)
            
            # Add AIVIIZN form styling
            form_html = form_html.replace('<form', '<form class="aiviizn-form"')
            form_html = form_html.replace('action="/', 'action="/aiviizn/')
            
            forms_html += form_html + "\n"
        
        return forms_html
    
    def extract_calculations_js(self, calculations):
        """Generate JavaScript for calculations"""
        js_code = "// Extracted calculations from AppFolio\n"
        
        for calc in calculations:
            if 'text' in calc:
                # Parse calculation and create JS function
                calc_text = calc['text']
                if '$' in calc_text or '%' in calc_text:
                    js_code += f"// Calculation: {calc_text}\n"
                    js_code += f"// Context: {calc.get('context', '')}\n\n"
        
        return js_code
    
    def generate_database_models(self, soup, page_type):
        """Generate database models based on page content"""
        models = []
        
        # Look for data tables
        tables = soup.find_all('table')
        for table in tables:
            headers = [th.get_text().strip() for th in table.find_all('th')]
            if headers:
                model_name = f"{page_type}_data"
                model = {
                    'name': model_name,
                    'fields': headers,
                    'table_html': str(table)[:500]  # Truncate for storage
                }
                models.append(model)
        
        return models
    
    def generate_appfolio_css(self):
        """Generate AppFolio-inspired CSS for AIVIIZN"""
        return """
/* AppFolio-inspired color scheme */
:root {
    --appfolio-blue: #0066CC;
    --appfolio-dark-blue: #0052A3;
    --appfolio-light-blue: #4A90E2;
    --appfolio-gray: #F8F9FA;
    --appfolio-border: #E0E6ED;
}

/* AppFolio-style navigation */
.aiviizn-nav {
    background: var(--appfolio-blue);
    border-bottom: 2px solid var(--appfolio-dark-blue);
}

/* AppFolio-style content areas */
.aiviizn-content {
    background: white;
    border: 1px solid var(--appfolio-border);
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
}

/* AppFolio-style data tables */
.aiviizn-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    border: 1px solid var(--appfolio-border);
    border-radius: 6px;
    overflow: hidden;
}

.aiviizn-table th {
    background: var(--appfolio-gray);
    font-weight: 600;
    padding: 12px 15px;
    text-align: left;
    border-bottom: 2px solid var(--appfolio-border);
}

.aiviizn-table td {
    padding: 10px 15px;
    border-bottom: 1px solid #f0f0f0;
}

.aiviizn-table tr:hover {
    background: #f8f9fa;
}
"""
    
    def extract_page_specific_css(self, soup):
        """Extract page-specific CSS from AppFolio"""
        css = ""
        
        # Look for style tags
        style_tags = soup.find_all('style')
        for style in style_tags:
            css_content = style.get_text()
            # Filter and adapt CSS for AIVIIZN
            css += f"/* Adapted from AppFolio */\n{css_content}\n"
        
        return css
    
    def get_primary_table(self, page_type):
        """Get primary database table for page type"""
        table_map = {
            'reports': 'financial_reports',
            'properties': 'properties',
            'accounting': 'accounting_entries',
            'maintenance': 'maintenance_requests',
            'leasing': 'lease_agreements'
        }
        return table_map.get(page_type, 'general_data')
    
    def generate_calculation_functions(self, calculations):
        """Generate JavaScript calculation functions"""
        js_code = ""
        
        for calc in calculations:
            if 'text' in calc:
                # Create a calculation function
                func_name = f"calculate_{hash(calc['text']) % 1000}"
                js_code += f"""
function {func_name}() {{
    // Original calculation: {calc['text']}
    // Context: {calc.get('context', '')}
    // TODO: Implement calculation logic
    return 0;
}}
"""
        
        return js_code
    
    def generate_total_calculations(self, calculations):
        """Generate total calculation JavaScript"""
        return """
// Calculate grand totals for financial data
function calculateGrandTotal() {
    let total = 0;
    const values = document.querySelectorAll('.currency-value');
    values.forEach(value => {
        const amount = parseFloat(value.textContent.replace(/[$,]/g, ''));
        if (!isNaN(amount)) {
            total += amount;
        }
    });
    
    const totalElement = document.querySelector('.grand-total');
    if (totalElement) {
        totalElement.textContent = formatCurrency(total);
    }
}

// Format currency values
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}
"""
    
    async def generate_database_migration(self, models, page_type):
        """Generate database migration file"""
        migration_content = f"""-- AIVIIZN Database Migration for {page_type}
-- Generated from AppFolio page analysis
-- Timestamp: {datetime.now().isoformat()}

"""
        
        for model in models:
            table_name = model['name']
            fields = model['fields']
            
            migration_content += f"""
-- Table: {table_name}
CREATE TABLE IF NOT EXISTS {table_name} (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
"""
            
            for field in fields:
                # Convert field names to database columns
                col_name = field.lower().replace(' ', '_').replace('(', '').replace(')', '')
                col_type = "TEXT"  # Default type
                
                # Determine appropriate column type
                if any(word in field.lower() for word in ['amount', 'balance', 'total', 'cost', 'price']):
                    col_type = "DECIMAL(12,2)"
                elif any(word in field.lower() for word in ['date', 'time']):
                    col_type = "DATE"
                elif any(word in field.lower() for word in ['id', 'number', 'count']):
                    col_type = "INTEGER"
                
                migration_content += f"    {col_name} {col_type},\n"
            
            migration_content += ");\n\n"
        
        # Save migration file
        migration_file = f"migrations/{page_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
        os.makedirs('migrations', exist_ok=True)
        
        with open(migration_file, 'w') as f:
            f.write(migration_content)
        
        print(f"📊 Database migration created: {migration_file}")
    
    async def generate_beautiful_template(self, page_data):
        """Generate pixel-perfect AIVIIZN template from AppFolio page data"""
        try:
            # Create template directory
            template_dir = f"templates/{page_data.page_type}"
            os.makedirs(template_dir, exist_ok=True)
            
            # Generate template filename
            safe_title = re.sub(r'[^\w\s-]', '', page_data.title).strip()
            safe_title = re.sub(r'[-\s]+', '_', safe_title).lower()
            template_path = f"{template_dir}/{safe_title}.html"
            
            # Parse the HTML to extract the main content
            soup = BeautifulSoup(page_data.html_content, 'html.parser')
            
            # Extract AppFolio's main content area
            main_content = self.extract_main_content(soup)
            
            # Convert AppFolio styling to AIVIIZN
            converted_content = self.convert_appfolio_to_aiviizn(main_content)
            
            # Extract and convert forms/interactive elements
            forms_html = self.extract_and_convert_forms(soup)
            
            # Extract calculations and data tables
            calculations_js = self.extract_calculations_js(page_data.calculations)
            
            # Generate database models for this page
            database_models = self.generate_database_models(soup, page_data.page_type)
            
            # Create the complete beautiful template
            template_content = f"""<!-- AIVIIZN Template: {page_data.title} -->
<!-- Generated from: {page_data.url} -->
<!-- Timestamp: {page_data.timestamp} -->
<!-- Beautiful AppFolio-inspired design -->

{{% extends "base.html" %}}

{{% block title %}}{page_data.title} - AIVIIZN Property Manager{{% endblock %}}

{{% block styles %}}
<style>
/* AppFolio-inspired styling converted for AIVIIZN */
{self.generate_appfolio_css()}

/* Page-specific styling */
{self.extract_page_specific_css(soup)}

/* AIVIIZN Beautiful Enhancements */
.aiviizn-page {{
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    min-height: 100vh;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}}

.content-wrapper {{
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    margin: 20px;
    padding: 30px;
    backdrop-filter: blur(10px);
}}

.aiviizn-header {{
    background: linear-gradient(135deg, var(--primary-blue) 0%, var(--dark-blue) 100%);
    color: white;
    padding: 25px 30px;
    border-radius: 8px 8px 0 0;
    margin: -30px -30px 30px -30px;
    position: relative;
    overflow: hidden;
}}

.aiviizn-header::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="75" cy="75" r="1" fill="rgba(255,255,255,0.1)"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
    opacity: 0.3;
}}

.aiviizn-header h1 {{
    margin: 0;
    font-weight: 600;
    font-size: 1.8rem;
    position: relative;
    z-index: 1;
}}

.aiviizn-header p {{
    margin: 8px 0 0 0;
    opacity: 0.9;
    position: relative;
    z-index: 1;
}}

/* Beautiful AppFolio-style buttons */
.btn-appfolio {{
    background: linear-gradient(135deg, #0066CC 0%, #0052A3 100%);
    border: none;
    color: white;
    padding: 10px 20px;
    border-radius: 6px;
    font-weight: 500;
    font-size: 14px;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(0, 102, 204, 0.3);
    position: relative;
    overflow: hidden;
}}

.btn-appfolio:hover {{
    background: linear-gradient(135deg, #0052A3 0%, #004182 100%);
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(0, 102, 204, 0.4);
}}

.btn-appfolio:active {{
    transform: translateY(0);
}}

/* Beautiful data grid styling */
.data-grid {{
    border: 1px solid #e0e6ed;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    background: white;
}}

.data-grid th {{
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border-bottom: 2px solid #dee2e6;
    font-weight: 600;
    padding: 15px 12px;
    text-align: left;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #495057;
}}

.data-grid td {{
    padding: 12px;
    border-bottom: 1px solid #f8f9fa;
    vertical-align: middle;
    font-size: 14px;
}}

.data-grid tr:hover {{
    background: linear-gradient(135deg, #f8f9fa 0%, #f1f3f4 100%);
    transition: all 0.2s ease;
}}

.data-grid tr:last-child td {{
    border-bottom: none;
}}

/* Beautiful currency formatting */
.currency {{
    font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace;
    font-weight: 600;
    text-align: right;
    font-size: 14px;
}}

.currency.positive {{
    color: #28a745;
    background: rgba(40, 167, 69, 0.1);
    padding: 2px 6px;
    border-radius: 4px;
}}

.currency.negative {{
    color: #dc3545;
    background: rgba(220, 53, 69, 0.1);
    padding: 2px 6px;
    border-radius: 4px;
}}

/* Beautiful form styling */
.aiviizn-form {{
    background: #f8f9fa;
    padding: 25px;
    border-radius: 8px;
    border: 1px solid #e9ecef;
    margin: 20px 0;
}}

.aiviizn-input {{
    border: 2px solid #e9ecef;
    border-radius: 6px;
    padding: 10px 12px;
    font-size: 14px;
    transition: all 0.2s ease;
}}

.aiviizn-input:focus {{
    border-color: var(--primary-blue);
    box-shadow: 0 0 0 3px rgba(11, 83, 148, 0.1);
    outline: none;
}}

/* Loading states */
.loading {{
    opacity: 0.6;
    pointer-events: none;
    position: relative;
}}

.loading::after {{
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 20px;
    height: 20px;
    margin: -10px 0 0 -10px;
    border: 2px solid #f3f3f3;
    border-top: 2px solid var(--primary-blue);
    border-radius: 50%;
    animation: spin 1s linear infinite;
}}

@keyframes spin {{
    0% {{ transform: rotate(0deg); }}
    100% {{ transform: rotate(360deg); }}
}}

/* Responsive design */
@media (max-width: 768px) {{
    .content-wrapper {{
        margin: 10px;
        padding: 20px;
    }}
    
    .aiviizn-header {{
        padding: 20px;
        margin: -20px -20px 20px -20px;
    }}
    
    .data-grid {{
        font-size: 12px;
    }}
    
    .data-grid th,
    .data-grid td {{
        padding: 8px;
    }}
}}
</style>
{{% endblock %}}

{{% block content %}}
<div class="aiviizn-page {page_data.page_type}">
    <div class="content-wrapper">
        <div class="aiviizn-header">
            <h1><i class="fas fa-chart-line me-3"></i>{page_data.title}</h1>
            <p class="mb-0">Professional property management reporting with beautiful design</p>
        </div>
        
        <!-- AppFolio Content Converted to Beautiful AIVIIZN Design -->
        <div class="aiviizn-content-area">
            {converted_content}
        </div>
        
        <!-- Interactive Forms with Beautiful Styling -->
        <div class="aiviizn-forms-section">
            {forms_html}
        </div>
        
        <!-- Data Visualization Section -->
        <div class="mt-4" id="data-visualization">
            <h3 class="mb-3"><i class="fas fa-chart-bar me-2"></i>Data Insights</h3>
            <div class="row">
                <div class="col-md-8">
                    <canvas id="main-chart" style="max-height: 400px;"></canvas>
                </div>
                <div class="col-md-4">
                    <div class="card border-0 shadow-sm">
                        <div class="card-body">
                            <h5 class="card-title">Quick Stats</h5>
                            <div id="quick-stats">
                                <!-- Stats will be populated by JavaScript -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Export and Action Buttons -->
        <div class="mt-4 d-flex justify-content-between align-items-center">
            <div class="btn-group" role="group">
                <button type="button" class="btn btn-appfolio" onclick="exportToPDF()">
                    <i class="fas fa-file-pdf me-2"></i>Export PDF
                </button>
                <button type="button" class="btn btn-outline-primary" onclick="exportToExcel()">
                    <i class="fas fa-file-excel me-2"></i>Export Excel
                </button>
                <button type="button" class="btn btn-outline-secondary" onclick="refreshData()">
                    <i class="fas fa-sync-alt me-2"></i>Refresh
                </button>
            </div>
            <small class="text-muted">
                Last updated: <span id="last-updated">{{ page_data.timestamp }}</span>
            </small>
        </div>
    </div>
</div>
{{% endblock %}}

{{% block scripts %}}
<!-- Chart.js for beautiful visualizations -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<script>
// AIVIIZN JavaScript - Beautiful AppFolio functionality
console.log('🚀 AIVIIZN {page_data.title} - Loading...');

// Supabase connection
const supabaseUrl = '{{{{ supabase_url }}}}';
const supabaseAnonKey = '{{{{ supabase_anon_key }}}}';
const supabase = window.supabase.createClient(supabaseUrl, supabaseAnonKey);

// Page-specific calculations converted from AppFolio
{calculations_js}

// Beautiful AIVIIZN Database Class
class AIVIIZNDatabase {{
    constructor() {{
        this.tableName = '{self.get_primary_table(page_data.page_type)}';
        this.cache = new Map();
    }}
    
    // Load data for this beautiful page
    async loadPageData() {{
        try {{
            console.log('📊 Loading data for {page_data.title}...');
            const {{ data, error }} = await supabase
                .from(this.tableName)
                .select('*')
                .order('created_at', {{ ascending: false }});
            
            if (error) throw error;
            
            this.cache.set('pageData', data);
            this.renderBeautifulData(data);
            this.updateCalculations(data);
            this.createVisualization(data);
            
            console.log('✅ Data loaded successfully!');
        }} catch (error) {{
            console.error('❌ Error loading data:', error);
            this.showErrorMessage('Failed to load data. Please try again.');
        }}
    }}
    
    // Render data in beautiful AppFolio-style tables
    renderBeautifulData(data) {{
        const tableContainer = document.querySelector('.data-grid');
        if (!tableContainer || !data.length) return;
        
        // Create beautiful table HTML
        let tableHTML = '<table class="table table-hover data-grid">';
        
        // Beautiful header
        tableHTML += '<thead><tr>';
        Object.keys(data[0]).forEach(key => {{
            if (key !== 'id' && key !== 'created_at' && key !== 'updated_at') {{
                tableHTML += `<th>${{this.formatColumnName(key)}}</th>`;
            }}
        }});
        tableHTML += '</tr></thead>';
        
        // Beautiful body
        tableHTML += '<tbody>';
        data.forEach(row => {{
            tableHTML += '<tr>';
            Object.entries(row).forEach(([key, value]) => {{
                if (key !== 'id' && key !== 'created_at' && key !== 'updated_at') {{
                    const formattedValue = this.formatCellValue(key, value);
                    tableHTML += `<td>${{formattedValue}}</td>`;
                }}
            }});
            tableHTML += '</tr>';
        }});
        tableHTML += '</tbody></table>';
        
        tableContainer.innerHTML = tableHTML;
    }}
    
    // Format column names beautifully
    formatColumnName(name) {{
        return name.replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase());
    }}
    
    // Format cell values beautifully
    formatCellValue(key, value) {{
        if (value === null || value === undefined) return '<em class="text-muted">—</em>';
        
        // Currency formatting
        if (key.includes('amount') || key.includes('balance') || key.includes('total')) {{
            const numValue = parseFloat(value);
            if (!isNaN(numValue)) {{
                const formatted = this.formatCurrency(numValue);
                const cssClass = numValue >= 0 ? 'positive' : 'negative';
                return `<span class="currency ${{cssClass}}">${{formatted}}</span>`;
            }}
        }}
        
        // Date formatting
        if (key.includes('date') || key.includes('time')) {{
            return new Date(value).toLocaleDateString();
        }}
        
        // Percentage formatting
        if (key.includes('percent') || key.includes('rate')) {{
            const numValue = parseFloat(value);
            if (!isNaN(numValue)) {{
                return `<span class="badge bg-info">${{numValue}}%</span>`;
            }}
        }}
        
        return value;
    }}
    
    // Beautiful currency formatting
    formatCurrency(amount) {{
        return new Intl.NumberFormat('en-US', {{
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2
        }}).format(amount);
    }}
    
    // Update calculations with beautiful animations
    updateCalculations(data) {{
        console.log('🧮 Updating calculations...');
        
        // Calculate totals
        const totals = this.calculateTotals(data);
        
        // Update UI with beautiful animations
        Object.entries(totals).forEach(([key, value]) => {{
            const element = document.querySelector(`[data-calculation="${{key}}"]`);
            if (element) {{
                this.animateValueChange(element, value);
            }}
        }});
        
        {self.generate_total_calculations(page_data.calculations)}
    }}
    
    // Create beautiful data visualization
    createVisualization(data) {{
        const ctx = document.getElementById('main-chart');
        if (!ctx || !data.length) return;
        
        // Prepare data for Chart.js
        const chartData = this.prepareChartData(data);
        
        new Chart(ctx, {{
            type: 'line',
            data: chartData,
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: '{page_data.title} Trends',
                        font: {{
                            family: 'Inter',
                            size: 16,
                            weight: '600'
                        }}
                    }},
                    legend: {{
                        position: 'bottom'
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        grid: {{
                            color: 'rgba(0,0,0,0.05)'
                        }}
                    }},
                    x: {{
                        grid: {{
                            color: 'rgba(0,0,0,0.05)'
                        }}
                    }}
                }},
                elements: {{
                    line: {{
                        tension: 0.4
                    }},
                    point: {{
                        radius: 4,
                        hoverRadius: 6
                    }}
                }}
            }}
        }});
    }}
    
    // Prepare chart data from database
    prepareChartData(data) {{
        // This would be customized based on the specific page type
        return {{
            labels: data.map((_, index) => `Period ${{index + 1}}`),
            datasets: [{{
                label: 'Values',
                data: data.map(row => Object.values(row)[1]), // First numeric column
                borderColor: 'rgb(11, 83, 148)',
                backgroundColor: 'rgba(11, 83, 148, 0.1)',
                fill: true
            }}]
        }};
    }}
    
    // Calculate totals and summaries
    calculateTotals(data) {{
        const totals = {{}};
        
        if (!data.length) return totals;
        
        // Calculate sums for numeric columns
        Object.keys(data[0]).forEach(key => {{
            if (key.includes('amount') || key.includes('balance') || key.includes('total')) {{
                totals[key] = data.reduce((sum, row) => {{
                    const value = parseFloat(row[key]) || 0;
                    return sum + value;
                }}, 0);
            }}
        }});
        
        return totals;
    }}
    
    // Animate value changes
    animateValueChange(element, newValue) {{
        const currentValue = parseFloat(element.textContent.replace(/[^\\d.-]/g, '')) || 0;
        const duration = 1000;
        const startTime = performance.now();
        
        const animate = (currentTime) => {{
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            
            const interpolatedValue = currentValue + (newValue - currentValue) * easeOutQuart;
            
            if (element.classList.contains('currency')) {{
                element.textContent = this.formatCurrency(interpolatedValue);
            }} else {{
                element.textContent = Math.round(interpolatedValue).toLocaleString();
            }}
            
            if (progress < 1) {{
                requestAnimationFrame(animate);
            }}
        }};
        
        requestAnimationFrame(animate);
    }}
    
    // Show beautiful error messages
    showErrorMessage(message) {{
        const alertHTML = `
            <div class="alert alert-danger alert-dismissible fade show" role="alert">
                <i class="fas fa-exclamation-triangle me-2"></i>
                ${{message}}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        const container = document.querySelector('.content-wrapper');
        container.insertAdjacentHTML('afterbegin', alertHTML);
    }}
}}

// Initialize beautiful page functionality
document.addEventListener('DOMContentLoaded', function() {{
    console.log('🎨 Initializing beautiful AIVIIZN page...');
    
    const db = new AIVIIZNDatabase();
    db.loadPageData();
    
    // Initialize all beautiful interactions
    initializeFilters();
    initializeDatePickers();
    initializeDataTables();
    initializeCalculations();
    initializeAnimations();
    
    console.log('✨ Beautiful AIVIIZN page ready!');
}});

// Beautiful filter functionality
function initializeFilters() {{
    const filters = document.querySelectorAll('.filter-control');
    filters.forEach(filter => {{
        filter.addEventListener('change', function() {{
            const loading = document.querySelector('.content-wrapper');
            loading.classList.add('loading');
            
            setTimeout(() => {{
                updateDataDisplay();
                loading.classList.remove('loading');
            }}, 500);
        }});
    }});
}}

// Beautiful date picker initialization
function initializeDatePickers() {{
    const datePickers = document.querySelectorAll('.date-picker');
    datePickers.forEach(picker => {{
        picker.addEventListener('change', function() {{
            refreshReportData();
        }});
    }});
}}

// Beautiful data table functionality
function initializeDataTables() {{
    const tables = document.querySelectorAll('.data-grid');
    tables.forEach(table => {{
        addTableSorting(table);
        addTableFiltering(table);
        addTableAnimations(table);
    }});
}}

// Beautiful real-time calculations
function initializeCalculations() {{
    const calculationFields = document.querySelectorAll('.calculation-field');
    calculationFields.forEach(field => {{
        field.addEventListener('input', function() {{
            recalculateAllTotals();
        }});
    }});
}}

// Beautiful animations
function initializeAnimations() {{
    // Intersection Observer for scroll animations
    const observer = new IntersectionObserver((entries) => {{
        entries.forEach(entry => {{
            if (entry.isIntersecting) {{
                entry.target.style.animation = 'fadeInUp 0.6s ease forwards';
            }}
        }});
    }});
    
    document.querySelectorAll('.data-grid, .aiviizn-form, .card').forEach(el => {{
        observer.observe(el);
    }});
}}

// Export functions
function exportToPDF() {{
    console.log('📄 Exporting to beautiful PDF...');
    // Implementation would go here
    alert('PDF export functionality would be implemented here');
}}

function exportToExcel() {{
    console.log('📊 Exporting to Excel...');
    // Implementation would go here
    alert('Excel export functionality would be implemented here');
}}

function refreshData() {{
    console.log('🔄 Refreshing data...');
    const db = new AIVIIZNDatabase();
    db.loadPageData();
    
    // Update timestamp
    document.getElementById('last-updated').textContent = new Date().toLocaleString();
}}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
@keyframes fadeInUp {{
    from {{
        opacity: 0;
        transform: translateY(30px);
    }}
    to {{
        opacity: 1;
        transform: translateY(0);
    }}
}}
`;
document.head.appendChild(style);

</script>
{{% endblock %}}
"""
            
            # Write the beautiful template file
            with open(template_path, 'w') as f:
                f.write(template_content)
            
            # Generate database migration file
            await self.generate_database_migration(database_models, page_data.page_type)
            
            print(f"🎨 Beautiful AIVIIZN template created: {template_path}")
            print(f"📊 Database models generated: {len(database_models)} tables")
            print(f"✨ AppFolio styling converted to beautiful AIVIIZN design")
            
        except Exception as e:
            self.logger.error(f"Error generating beautiful template: {e}")
    
    async def extract_calculations(self, page):
        """Extract calculations and formulas from page"""
        calculations = []
        
        try:
            # Look for number patterns and formulas
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # Find elements with numbers
            for element in soup.find_all(text=re.compile(r'\$[\d,]+\.?\d*|\d+%|[\d,]+\.?\d*')):
                parent = element.parent
                calculations.append({
                    'text': element.strip(),
                    'context': parent.get_text().strip()[:100],
                    'tag': parent.name if parent else 'text'
                })
            
            # Look for JavaScript calculations
            scripts = await page.eval_on_selector_all(
                'script',
                'elements => elements.map(el => el.textContent)'
            )
            
            for script in scripts:
                if any(term in script for term in ['calculate', 'sum', 'total', 'Math.']):
                    calculations.append({
                        'type': 'javascript',
                        'content': script[:500]  # First 500 chars
                    })
            
        except Exception as e:
            self.logger.error(f"Error extracting calculations: {e}")
        
        return calculations
    
    async def get_ai_analysis(self, content, title, url):
        """Get AI analysis of page functionality"""
        analysis = {}
        
        try:
            # OpenAI analysis
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{
                    "role": "user",
                    "content": f"Analyze this AppFolio page and describe its functionality, calculations, and key features. Focus on what business logic needs to be replicated.\n\nTitle: {title}\nURL: {url}\n\nContent: {content[:2000]}"
                }],
                max_tokens=500
            )
            analysis['openai'] = response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Error in AI analysis: {e}")
            analysis['error'] = str(e)
        
        return analysis
    
    def determine_page_type(self, url, title):
        """Determine the type of page for template organization"""
        if '/reports' in url or '/buffered_reports' in url:
            return 'reports'
        elif '/properties' in url:
            return 'properties'
        elif '/accounting' in url:
            return 'accounting'
        elif '/maintenance' in url:
            return 'maintenance'
        elif '/leasing' in url:
            return 'leasing'
        else:
            return 'general'
    
    async def store_page_data(self, page_data):
        """Store page data in Supabase"""
        try:
            # Store in appfolio_pages table
            data = {
                'url': page_data.url,
                'title': page_data.title,
                'page_type': page_data.page_type,
                'screenshot_path': page_data.screenshot_path,
                'calculations_count': len(page_data.calculations),
                'links_discovered_count': len(page_data.links_discovered),
                'ai_analysis': page_data.ai_analysis,
                'processed_at': page_data.timestamp
            }
            
            result = self.supabase.table('appfolio_pages').insert(data).execute()
            print(f"💾 Stored beautiful page data in database")
            
        except Exception as e:
            self.logger.error(f"Error storing page data: {e}")

async def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced AIVIIZN Terminal Agent')
    parser.add_argument('--url', help='Starting URL to process')
    parser.add_argument('--start-reports', action='store_true', help='Start with reports page')
    args = parser.parse_args()
    
    # Determine starting URL
    start_url = None
    if args.url:
        start_url = args.url
    elif args.start_reports:
        start_url = "https://celticprop.appfolio.com/reports"
    
    # Create and run enhanced agent
    agent = AIViizNTerminalAgent()
    
    try:
        print("🎨 Enhanced AIVIIZN Terminal Agent - Beautiful AppFolio Replication")
        print("=" * 70)
        await agent.start_processing(start_url)
    except KeyboardInterrupt:
        print("\n🛑 Shutdown requested by user")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        print("👋 Beautiful AIVIIZN Terminal Agent shutdown complete")

if __name__ == "__main__":
    asyncio.run(main())
