#!/usr/bin/env python3
"""
AIVIIZN Terminal Agent - AppFolio to AIVIIZN Replicator
Keeps browser open, processes pages systematically, extracts functionality
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
        print("🔐 Please log in manually in the browser window")
        print("Press Enter when login is complete...")
        input()
        print("▶️ Continuing with processing...")
    
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
    """Main terminal agent for AppFolio replication"""
    
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
        
        # Check if login is needed
        await self.browser_manager.navigate_and_process(start_url)
        
        if "login" in self.browser_manager.page.url.lower():
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
            
            # Generate AIVIIZN template
            await self.generate_template(page_data)
            
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
        if '/reports' in url:
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
    
    async def generate_template(self, page_data):
        """Generate AIVIIZN template from page data"""
        try:
            # Create template directory
            template_dir = f"templates/{page_data.page_type}"
            os.makedirs(template_dir, exist_ok=True)
            
            # Generate template filename
            safe_title = re.sub(r'[^\w\s-]', '', page_data.title).strip()
            safe_title = re.sub(r'[-\s]+', '_', safe_title).lower()
            template_path = f"{template_dir}/{safe_title}.html"
            
            # Create basic template structure
            template_content = f"""<!-- AIVIIZN Template: {page_data.title} -->
<!-- Generated from: {page_data.url} -->
<!-- Timestamp: {page_data.timestamp} -->

{{% extends "base.html" %}}

{{% block title %}}{page_data.title} - AIVIIZN{{% endblock %}}

{{% block content %}}
<div class="aiviizn-page {page_data.page_type}">
    <h1>{page_data.title}</h1>
    
    <!-- TODO: Implement functionality from {page_data.url} -->
    <!-- Calculations found: {len(page_data.calculations)} -->
    <!-- Links discovered: {len(page_data.links_discovered)} -->
    
    <!-- AI Analysis: -->
    <!-- {page_data.ai_analysis.get('openai', 'No analysis available')} -->
    
</div>
{{% endblock %}}

{{% block scripts %}}
<script>
// TODO: Implement JavaScript functionality
// Original page calculations: {len(page_data.calculations)}
</script>
{{% endblock %}}
"""
            
            with open(template_path, 'w') as f:
                f.write(template_content)
            
            print(f"📄 Template created: {template_path}")
            
        except Exception as e:
            self.logger.error(f"Error generating template: {e}")
    
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
            print(f"💾 Stored page data in database")
            
        except Exception as e:
            self.logger.error(f"Error storing page data: {e}")

async def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AIVIIZN Terminal Agent')
    parser.add_argument('--url', help='Starting URL to process')
    parser.add_argument('--start-reports', action='store_true', help='Start with reports page')
    args = parser.parse_args()
    
    # Determine starting URL
    start_url = None
    if args.url:
        start_url = args.url
    elif args.start_reports:
        start_url = "https://celticprop.appfolio.com/reports"
    
    # Create and run agent
    agent = AIViizNTerminalAgent()
    
    try:
        print("🚀 AIVIIZN Terminal Agent - AppFolio Replicator")
        print("=" * 50)
        await agent.start_processing(start_url)
    except KeyboardInterrupt:
        print("\n🛑 Shutdown requested by user")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        print("👋 AIVIIZN Terminal Agent shutdown complete")

if __name__ == "__main__":
    asyncio.run(main())
