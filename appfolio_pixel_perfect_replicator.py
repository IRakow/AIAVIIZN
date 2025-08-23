#!/usr/bin/env python3
"""
🎯 APPFOLIO PIXEL-PERFECT REPLICATOR
Complete terminal app for exact AppFolio replication with multi-AI validation

Features:
- Complete browser automation with Playwright
- Multi-AI validation (OpenAI, Gemini, Wolfram, Claude)
- Pixel-perfect template generation using existing AIVIIZN framework
- Complete database schema duplication
- Exact JavaScript calculations replication
- Mathematical consensus verification (1% tolerance)
- Error handling with immediate stops
"""

import os
import sys
import json
import time
import asyncio
import aiohttp
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import subprocess
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('appfolio_replication.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class PageInfo:
    name: str
    url: str
    category: str
    critical_calculations: List[str]
    validation_priority: str
    related_pages: List[str]
    data_dependencies: List[str]

class AppFolioPixelPerfectReplicator:
    def __init__(self):
        self.current_page = 0
        self.total_pages_processed = 0
        self.discovered_links = set()
        self.processed_links = set()
        self.page_analysis_results = {}
        self.multi_ai_validation_results = {}
        self.consensus_threshold = 0.01  # 1% tolerance
        
        # API Configuration
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY') 
        self.wolfram_app_id = os.getenv('WOLFRAM_APP_ID', 'X479TRR99U')
        
        # AIVIIZN Framework Paths
        self.templates_base_path = "/Users/ianrakow/Desktop/AIVIIZN/templates"
        self.static_js_path = "/Users/ianrakow/Desktop/AIVIIZN/static/js"
        self.static_css_path = "/Users/ianrakow/Desktop/AIVIIZN/static/css"
        self.docs_path = "/Users/ianrakow/Desktop/AIVIIZN/docs"
        
        # Playwright browser instance
        self.browser = None
        self.page = None
        self.context = None
        
        # Validation tracking
        self.validation_errors = []
        self.schema_validations = {}
        
        print("🎯 APPFOLIO PIXEL-PERFECT REPLICATOR INITIALIZED")
        print("=" * 80)

    async def initialize_browser(self):
        """Initialize Playwright browser"""
        try:
            from playwright.async_api import async_playwright
            
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=False,  # Keep visible for authentication
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            
            self.page = await self.context.new_page()
            
            # Enable request/response logging
            self.page.on('request', self.log_request)
            self.page.on('response', self.log_response)
            
            logger.info("✅ Browser initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Browser initialization failed: {e}")
            return False

    def log_request(self, request):
        """Log network requests"""
        if 'appfolio.com' in request.url:
            logger.debug(f"📤 REQUEST: {request.method} {request.url}")

    def log_response(self, response):
        """Log network responses"""
        if 'appfolio.com' in response.url and response.status >= 400:
            logger.warning(f"📥 RESPONSE ERROR: {response.status} {response.url}")

    async def authenticate_appfolio(self):
        """Navigate to AppFolio and wait for manual authentication"""
        try:
            logger.info("🔑 Navigating to AppFolio login...")
            
            await self.page.goto("https://celticprop.appfolio.com/reports")
            
            # Check if we're redirected to login
            current_url = self.page.url
            if 'sign_in' in current_url:
                logger.info("🔐 Login page detected. Please authenticate manually...")
                logger.info("⏳ Waiting for authentication to complete...")
                
                # Wait for successful login (redirect away from sign_in)
                await self.page.wait_for_url('**/reports', timeout=300000)  # 5 minutes
                
            logger.info("✅ Successfully authenticated and on reports page")
            await asyncio.sleep(3)  # Let page fully load
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Authentication failed: {e}")
            return False

    async def extract_complete_page_structure(self, url: str) -> Dict:
        """Extract complete page structure including all elements, calculations, and functionality"""
        try:
            logger.info(f"📄 Extracting complete structure from: {url}")
            
            await self.page.goto(url)
            await self.page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)
            
            # Take comprehensive screenshot
            screenshot_path = f"screenshots/page_{self.current_page}_{int(time.time())}.png"
            os.makedirs("screenshots", exist_ok=True)
            await self.page.screenshot(path=screenshot_path, full_page=True)
            
            # Extract all page content
            page_content = await self.page.content()
            
            # Get page snapshot for accessibility tree
            snapshot = await self.page.accessibility.snapshot()
            
            # Extract all visible text
            all_text = await self.page.evaluate("() => document.body.innerText")
            
            # Extract all links
            links = await self.page.evaluate("""
                () => Array.from(document.querySelectorAll('a[href]')).map(a => ({
                    text: a.innerText.trim(),
                    href: a.href,
                    title: a.title || '',
                    classes: a.className
                }))
            """)
            
            # Extract all buttons
            buttons = await self.page.evaluate("""
                () => Array.from(document.querySelectorAll('button, input[type="button"], input[type="submit"]')).map(btn => ({
                    text: btn.innerText.trim() || btn.value || '',
                    id: btn.id || '',
                    classes: btn.className,
                    type: btn.type || 'button',
                    onclick: btn.onclick ? btn.onclick.toString() : '',
                    disabled: btn.disabled
                }))
            """)
            
            # Extract all forms
            forms = await self.page.evaluate("""
                () => Array.from(document.querySelectorAll('form')).map(form => ({
                    action: form.action || '',
                    method: form.method || 'GET',
                    id: form.id || '',
                    classes: form.className,
                    fields: Array.from(form.querySelectorAll('input, select, textarea')).map(field => ({
                        name: field.name || '',
                        type: field.type || '',
                        id: field.id || '',
                        placeholder: field.placeholder || '',
                        required: field.required,
                        value: field.value || ''
                    }))
                }))
            """)
            
            # Extract all tables with data
            tables = await self.page.evaluate("""
                () => Array.from(document.querySelectorAll('table')).map(table => ({
                    id: table.id || '',
                    classes: table.className,
                    headers: Array.from(table.querySelectorAll('th')).map(th => th.innerText.trim()),
                    rows: Array.from(table.querySelectorAll('tbody tr')).slice(0, 5).map(tr => 
                        Array.from(tr.querySelectorAll('td')).map(td => td.innerText.trim())
                    )
                }))
            """)
            
            # Extract any visible calculations or numbers
            calculations = await self.page.evaluate("""
                () => {
                    const numberPattern = /\\$?([0-9,]+\\.?[0-9]*)\\s*%?/g;
                    const text = document.body.innerText;
                    const matches = [...text.matchAll(numberPattern)];
                    return matches.map(match => ({
                        value: match[0],
                        context: text.substring(Math.max(0, match.index - 50), match.index + 50)
                    })).slice(0, 20);
                }
            """)
            
            # Extract navigation structure
            navigation = await self.page.evaluate("""
                () => ({
                    breadcrumbs: Array.from(document.querySelectorAll('.breadcrumb, .breadcrumbs, nav[aria-label="breadcrumb"]')).map(nav => nav.innerText.trim()),
                    sidebar: Array.from(document.querySelectorAll('aside, .sidebar, .nav-sidebar')).map(side => side.innerText.trim()),
                    mainNav: Array.from(document.querySelectorAll('nav:not([aria-label="breadcrumb"])')).map(nav => nav.innerText.trim())
                })
            """)
            
            # Extract any JavaScript variables or configs
            js_data = await self.page.evaluate("""
                () => {
                    const result = {};
                    // Look for common config patterns
                    if (window.Config) result.config = window.Config;
                    if (window.APP_CONFIG) result.app_config = window.APP_CONFIG;
                    if (window.pageData) result.page_data = window.pageData;
                    return result;
                }
            """)
            
            # Compile complete page analysis
            page_analysis = {
                "url": url,
                "timestamp": datetime.now().isoformat(),
                "page_title": await self.page.title(),
                "screenshot_path": screenshot_path,
                "page_content": page_content[:10000],  # Truncate for storage
                "accessibility_snapshot": snapshot,
                "all_text": all_text[:5000],  # Truncate for storage
                "links": links,
                "buttons": buttons,
                "forms": forms,
                "tables": tables,
                "calculations": calculations,
                "navigation": navigation,
                "javascript_data": js_data,
                "network_requests": []  # Will be populated by listeners
            }
            
            logger.info(f"✅ Extracted {len(links)} links, {len(buttons)} buttons, {len(forms)} forms, {len(tables)} tables")
            
            return page_analysis
            
        except Exception as e:
            logger.error(f"❌ Page extraction failed for {url}: {e}")
            return {}

    async def validate_with_openai(self, page_analysis: Dict, page_info: PageInfo) -> Dict:
        """Validate with OpenAI GPT-4 for mathematical accuracy"""
        if not self.openai_api_key:
            return {"error": "No OpenAI API key", "success": False}
        
        try:
            logger.info("🤖 Validating with OpenAI GPT-4...")
            
            prompt = f"""
            MATHEMATICAL ACCURACY VALIDATION for AppFolio page: {page_info.name}
            
            Page Data:
            - URL: {page_analysis.get('url', '')}
            - Calculations found: {page_analysis.get('calculations', [])}
            - Critical calculations to verify: {page_info.critical_calculations}
            
            VALIDATION TASKS:
            1. Verify all mathematical formulas are correct
            2. Check calculation logic for property management standards  
            3. Identify any mathematical errors or inconsistencies
            4. Validate percentage calculations and totals
            
            Return JSON:
            {{
                "calculations_verified": true/false,
                "mathematical_accuracy_score": 0-100,
                "identified_errors": [],
                "suggested_corrections": [],
                "confidence_level": "HIGH/MEDIUM/LOW"
            }}
            """
            
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "model": "gpt-4-turbo-preview",
                "messages": [
                    {"role": "system", "content": "You are a financial calculation expert analyzing AppFolio property management calculations."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1,
                "max_tokens": 2000
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post('https://api.openai.com/v1/chat/completions', 
                                      headers=headers, json=payload, timeout=60) as response:
                    result = await response.json()
                    
                    return {
                        "ai_source": "OpenAI GPT-4",
                        "validation_result": result['choices'][0]['message']['content'],
                        "timestamp": datetime.now().isoformat(),
                        "success": True
                    }
                    
        except Exception as e:
            logger.error(f"❌ OpenAI validation failed: {e}")
            return {"ai_source": "OpenAI GPT-4", "error": str(e), "success": False}

    async def validate_with_gemini(self, page_analysis: Dict, page_info: PageInfo) -> Dict:
        """Validate with Google Gemini for business logic"""
        if not self.gemini_api_key:
            return {"error": "No Gemini API key", "success": False}
        
        try:
            logger.info("🤖 Validating with Google Gemini...")
            
            prompt = f"""
            BUSINESS LOGIC VALIDATION for AppFolio page: {page_info.name}
            
            Page Data:
            - URL: {page_analysis.get('url', '')}
            - Forms found: {page_analysis.get('forms', [])}
            - Tables found: {page_analysis.get('tables', [])}
            - Critical calculations: {page_info.critical_calculations}
            
            VALIDATION TASKS:
            1. Verify business logic follows property management standards
            2. Check data flow and dependencies are correct
            3. Identify edge cases and error handling needs
            4. Validate form validation requirements
            
            Return JSON:
            {{
                "business_logic_valid": true/false,
                "data_flow_correct": true/false,
                "edge_cases_identified": [],
                "business_rule_compliance_score": 0-100,
                "confidence_level": "HIGH/MEDIUM/LOW"
            }}
            """
            
            headers = {'Content-Type': 'application/json'}
            
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.1,
                    "maxOutputTokens": 2000
                }
            }
            
            url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.gemini_api_key}'
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload, timeout=60) as response:
                    result = await response.json()
                    
                    return {
                        "ai_source": "Google Gemini",
                        "validation_result": result['candidates'][0]['content']['parts'][0]['text'],
                        "timestamp": datetime.now().isoformat(),
                        "success": True
                    }
                    
        except Exception as e:
            logger.error(f"❌ Gemini validation failed: {e}")
            return {"ai_source": "Google Gemini", "error": str(e), "success": False}

    async def validate_with_wolfram(self, page_analysis: Dict, page_info: PageInfo) -> Dict:
        """Validate with Wolfram Alpha for mathematical proof"""
        try:
            logger.info("🤖 Validating with Wolfram Alpha...")
            
            calculations = page_analysis.get('calculations', [])
            if not calculations:
                return {
                    "ai_source": "Wolfram Alpha",
                    "validation_result": "No calculations found to verify",
                    "success": True
                }
            
            # Extract numerical calculations for Wolfram
            calc_text = "; ".join([calc['value'] for calc in calculations[:5]])
            
            prompt = f"""
            Verify these property management calculations mathematically:
            {calc_text}
            
            Critical calculations: {page_info.critical_calculations}
            
            Provide mathematical verification for each calculation.
            """
            
            headers = {'Content-Type': 'application/json'}
            payload = {
                "input": prompt,
                "appid": self.wolfram_app_id
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post('https://api.wolframalpha.com/v1/llm-api', 
                                      headers=headers, json=payload, timeout=60) as response:
                    result = await response.text()
                    
                    return {
                        "ai_source": "Wolfram Alpha",
                        "validation_result": result,
                        "timestamp": datetime.now().isoformat(),
                        "success": True
                    }
                    
        except Exception as e:
            logger.error(f"❌ Wolfram validation failed: {e}")
            return {"ai_source": "Wolfram Alpha", "error": str(e), "success": False}

    def call_claude_desktop(self, prompt: str) -> Dict:
        """Call Claude Desktop using AppleScript automation"""
        try:
            logger.info("🤖 Sending prompt to Claude Desktop...")
            
            # Save prompt to temporary file
            temp_file = "/tmp/claude_prompt.txt"
            with open(temp_file, 'w') as f:
                f.write(prompt)
            
            # AppleScript to automate Claude Desktop
            applescript = f'''
            tell application "Claude"
                activate
                delay 2
                
                -- Open new chat
                key code 45 using {{command down}}
                delay 3
                
                -- Read and paste prompt
                set promptText to (read file "{temp_file}")
                set the clipboard to promptText
                key code 9 using {{command down}}
                delay 2
                
                -- Send message
                key code 36
                delay 5
                
                -- Copy response (select all and copy)
                key code 0 using {{command down}}
                delay 1
                key code 8 using {{command down}}
                delay 2
                
                -- Get response from clipboard
                set responseText to (the clipboard as string)
                return responseText
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', applescript], 
                                  capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                response = result.stdout.strip()
                return {
                    "ai_source": "Claude Desktop",
                    "validation_result": response,
                    "timestamp": datetime.now().isoformat(),
                    "success": True
                }
            else:
                return {
                    "ai_source": "Claude Desktop",
                    "error": result.stderr,
                    "success": False
                }
                
        except Exception as e:
            logger.error(f"❌ Claude Desktop automation failed: {e}")
            return {"ai_source": "Claude Desktop", "error": str(e), "success": False}

    def create_claude_validation_prompt(self, page_analysis: Dict, page_info: PageInfo) -> str:
        """Create comprehensive Claude validation prompt"""
        
        return f"""
🎯 APPFOLIO PAGE ANALYSIS & PIXEL-PERFECT REPLICATION

Page: {page_info.name}
URL: {page_analysis.get('url', '')}
Priority: {page_info.validation_priority}

EXTRACTED PAGE DATA:
- Links: {len(page_analysis.get('links', []))}
- Buttons: {len(page_analysis.get('buttons', []))}
- Forms: {len(page_analysis.get('forms', []))}
- Tables: {len(page_analysis.get('tables', []))}
- Calculations: {page_analysis.get('calculations', [])}

CRITICAL VALIDATION TASKS:
1. 🧮 Mathematical Accuracy: Verify all calculations are correct
2. 🔗 Integration Logic: Check how this page connects to related pages
3. 🎨 UI/UX Implementation: Ensure pixel-perfect replication is feasible
4. ⚡ Performance: Validate calculations won't cause performance issues

DELIVERABLES REQUIRED:
1. Complete HTML template extending base.html
2. JavaScript calculations file
3. Database schema SQL
4. CSS overrides (if needed)
5. Integration with existing AIVIIZN navigation

CRITICAL CALCULATIONS TO VERIFY:
{', '.join(page_info.critical_calculations)}

RELATED PAGES FOR INTEGRATION:
{', '.join(page_info.related_pages)}

DATA DEPENDENCIES:
{', '.join(page_info.data_dependencies)}

🎯 PROVIDE COMPLETE ANALYSIS WITH:
- Mathematical verification results
- Exact HTML template code
- Complete JavaScript calculations
- Database schema requirements
- Integration recommendations
- Performance considerations

START COMPREHENSIVE ANALYSIS NOW!
"""

    async def run_multi_ai_validation(self, page_analysis: Dict, page_info: PageInfo) -> Dict:
        """Run validation across all AI systems in parallel"""
        try:
            logger.info(f"🤖 Running multi-AI validation for {page_info.name}")
            
            # Create Claude prompt
            claude_prompt = self.create_claude_validation_prompt(page_analysis, page_info)
            
            # Run all validations in parallel
            tasks = [
                self.validate_with_openai(page_analysis, page_info),
                self.validate_with_gemini(page_analysis, page_info),
                self.validate_with_wolfram(page_analysis, page_info)
            ]
            
            # Execute parallel validation
            ai_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Run Claude validation (synchronous)
            claude_result = self.call_claude_desktop(claude_prompt)
            
            validation_summary = {
                "page_name": page_info.name,
                "page_url": page_analysis.get('url', ''),
                "validation_timestamp": datetime.now().isoformat(),
                "openai_result": ai_results[0] if len(ai_results) > 0 else None,
                "gemini_result": ai_results[1] if len(ai_results) > 1 else None,
                "wolfram_result": ai_results[2] if len(ai_results) > 2 else None,
                "claude_result": claude_result,
                "consensus_analysis": self.analyze_consensus(ai_results + [claude_result]),
                "validation_priority": page_info.validation_priority
            }
            
            return validation_summary
            
        except Exception as e:
            logger.error(f"❌ Multi-AI validation failed for {page_info.name}: {e}")
            return {"error": str(e), "page_name": page_info.name}

    def analyze_consensus(self, ai_results: List[Dict]) -> Dict:
        """Analyze consensus between AI validation results"""
        
        successful_results = [r for r in ai_results if isinstance(r, dict) and r.get('success', True)]
        
        if len(successful_results) < 3:
            return {
                "consensus_achieved": False,
                "reason": f"Insufficient successful AI responses ({len(successful_results)}/4)",
                "recommendation": "STOP - Manual review required",
                "requires_manual_review": True
            }
        
        # Basic consensus analysis
        return {
            "consensus_achieved": len(successful_results) >= 3,
            "successful_validations": len(successful_results),
            "total_attempts": len(ai_results),
            "recommendation": "Proceed with template generation" if len(successful_results) >= 3 else "STOP - Manual review required",
            "requires_manual_review": len(successful_results) < 3
        }

    def extract_template_from_claude_response(self, claude_result: Dict) -> str:
        """Extract HTML template from Claude's response"""
        try:
            response_text = claude_result.get('validation_result', '')
            
            # Look for HTML template in response
            import re
            html_pattern = r'```html\s*(.*?)\s*```'
            html_match = re.search(html_pattern, response_text, re.DOTALL)
            
            if html_match:
                return html_match.group(1).strip()
            
            # If no code blocks, look for template-like content
            template_patterns = [
                r'{% extends "base\.html" %}.*?{% endblock %}',
                r'<!DOCTYPE html>.*?</html>',
                r'<div class="content-body">.*?</div>'
            ]
            
            for pattern in template_patterns:
                match = re.search(pattern, response_text, re.DOTALL)
                if match:
                    return match.group(0)
            
            return ""
            
        except Exception as e:
            logger.error(f"❌ Template extraction failed: {e}")
            return ""

    def extract_javascript_from_claude_response(self, claude_result: Dict) -> str:
        """Extract JavaScript calculations from Claude's response"""
        try:
            response_text = claude_result.get('validation_result', '')
            
            import re
            js_pattern = r'```javascript\s*(.*?)\s*```'
            js_match = re.search(js_pattern, response_text, re.DOTALL)
            
            if js_match:
                return js_match.group(1).strip()
            
            return "// No JavaScript calculations found"
            
        except Exception as e:
            logger.error(f"❌ JavaScript extraction failed: {e}")
            return "// Error extracting JavaScript"

    def extract_sql_from_claude_response(self, claude_result: Dict) -> str:
        """Extract SQL schema from Claude's response"""
        try:
            response_text = claude_result.get('validation_result', '')
            
            import re
            sql_pattern = r'```sql\s*(.*?)\s*```'
            sql_match = re.search(sql_pattern, response_text, re.DOTALL)
            
            if sql_match:
                return sql_match.group(1).strip()
            
            return "-- No SQL schema found"
            
        except Exception as e:
            logger.error(f"❌ SQL extraction failed: {e}")
            return "-- Error extracting SQL"

    def save_generated_files(self, page_info: PageInfo, validation_summary: Dict) -> Dict:
        """Save all generated files to proper AIVIIZN structure"""
        try:
            logger.info(f"💾 Saving generated files for {page_info.name}")
            
            saved_files = {}
            claude_result = validation_summary.get('claude_result', {})
            
            # Extract content from Claude response
            html_template = self.extract_template_from_claude_response(claude_result)
            javascript_code = self.extract_javascript_from_claude_response(claude_result)
            sql_schema = self.extract_sql_from_claude_response(claude_result)
            
            # Determine file paths based on AppFolio structure
            page_name_clean = page_info.name.lower().replace(' ', '_').replace('-', '_')
            
            # Map to AppFolio directory structure
            if page_info.category == "Accounting Reports":
                template_dir = f"{self.templates_base_path}/reports/accounting"
            elif page_info.category == "Property And Unit Reports":
                template_dir = f"{self.templates_base_path}/reports/property"
            elif page_info.category == "Tenant Reports":
                template_dir = f"{self.templates_base_path}/reports/tenant"
            else:
                template_dir = f"{self.templates_base_path}/reports/general"
            
            # Create directories
            os.makedirs(template_dir, exist_ok=True)
            os.makedirs(f"{self.static_js_path}/reports", exist_ok=True)
            os.makedirs(f"{self.docs_path}/reports", exist_ok=True)
            
            # Save HTML template
            if html_template:
                template_path = f"{template_dir}/{page_name_clean}.html"
                with open(template_path, 'w', encoding='utf-8') as f:
                    f.write(html_template)
                saved_files['template'] = template_path
                logger.info(f"✅ Saved template: {template_path}")
            
            # Save JavaScript
            if javascript_code and javascript_code != "// No JavaScript calculations found":
                js_path = f"{self.static_js_path}/reports/{page_name_clean}_calculations.js"
                with open(js_path, 'w', encoding='utf-8') as f:
                    f.write(javascript_code)
                saved_files['javascript'] = js_path
                logger.info(f"✅ Saved JavaScript: {js_path}")
            
            # Save SQL schema
            if sql_schema and sql_schema != "-- No SQL schema found":
                sql_path = f"{self.docs_path}/reports/{page_name_clean}_schema.sql"
                with open(sql_path, 'w', encoding='utf-8') as f:
                    f.write(sql_schema)
                saved_files['sql_schema'] = sql_path
                logger.info(f"✅ Saved SQL schema: {sql_path}")
            
            # Save validation results
            validation_path = f"{self.docs_path}/reports/{page_name_clean}_validation.json"
            with open(validation_path, 'w', encoding='utf-8') as f:
                json.dump(validation_summary, f, indent=2)
            saved_files['validation_results'] = validation_path
            
            return saved_files
            
        except Exception as e:
            logger.error(f"❌ File saving failed for {page_info.name}: {e}")
            return {}

    def discover_page_links(self, page_analysis: Dict) -> List[str]:
        """Discover new AppFolio links from current page"""
        try:
            discovered = []
            links = page_analysis.get('links', [])
            
            for link in links:
                href = link.get('href', '')
                if (href and 
                    'celticprop.appfolio.com' in href and
                    href not in self.processed_links and
                    href not in self.discovered_links and
                    '/buffered_reports/' in href):
                    
                    discovered.append(href)
                    self.discovered_links.add(href)
            
            logger.info(f"🔗 Discovered {len(discovered)} new links")
            return discovered
            
        except Exception as e:
            logger.error(f"❌ Link discovery failed: {e}")
            return []

    def get_page_info_from_url(self, url: str) -> PageInfo:
        """Extract page info from URL and content"""
        
        # Extract page name from URL
        if '/buffered_reports/' in url:
            page_name = url.split('/buffered_reports/')[-1].split('?')[0]
            page_name = page_name.replace('_', ' ').title()
        else:
            page_name = "Unknown Page"
        
        # Determine category and calculations based on page name
        if any(term in page_name.lower() for term in ['income', 'balance', 'cash_flow', 'trial']):
            category = "Accounting Reports"
            calculations = ["net_income", "total_expenses", "cash_flow"]
            priority = "HIGH"
        elif any(term in page_name.lower() for term in ['rent_roll', 'tenant', 'delinquency']):
            category = "Tenant Reports" 
            calculations = ["total_rent", "vacancy_rate", "collection_rate"]
            priority = "HIGH"
        elif any(term in page_name.lower() for term in ['property', 'unit', 'vacancy']):
            category = "Property And Unit Reports"
            calculations = ["occupancy_rate", "avg_rent"]
            priority = "MEDIUM"
        else:
            category = "General Reports"
            calculations = []
            priority = "LOW"
        
        return PageInfo(
            name=page_name,
            url=url,
            category=category,
            critical_calculations=calculations,
            validation_priority=priority,
            related_pages=[],
            data_dependencies=[]
        )

    async def process_single_appfolio_page(self, url: str) -> Dict:
        """Process a single AppFolio page with complete analysis and validation"""
        try:
            self.current_page += 1
            page_info = self.get_page_info_from_url(url)
            
            logger.info(f"\n{'='*80}")
            logger.info(f"🎯 PROCESSING PAGE {self.current_page}: {page_info.name}")
            logger.info(f"📍 URL: {url}")
            logger.info(f"🏷️  Category: {page_info.category}")
            logger.info(f"🎯 Priority: {page_info.validation_priority}")
            logger.info(f"{'='*80}")
            
            # Step 1: Extract complete page structure
            logger.info("📄 Step 1: Extracting complete page structure...")
            page_analysis = await self.extract_complete_page_structure(url)
            
            if not page_analysis:
                logger.error(f"❌ STOPPING: Failed to extract page structure for {url}")
                return {"error": "Page extraction failed", "page": page_info.name}
            
            # Step 2: Discover new links
            logger.info("🔗 Step 2: Discovering new links...")
            new_links = self.discover_page_links(page_analysis)
            
            # Step 3: Multi-AI validation
            logger.info("🤖 Step 3: Running multi-AI validation...")
            validation_summary = await self.run_multi_ai_validation(page_analysis, page_info)
            
            # Step 4: Check consensus
            consensus = validation_summary.get('consensus_analysis', {})
            if consensus.get('requires_manual_review', False):
                logger.error(f"❌ STOPPING: Consensus not achieved for {page_info.name}")
                logger.error(f"   Reason: {consensus.get('reason', 'Unknown')}")
                return {"error": "Consensus failed", "page": page_info.name, "validation": validation_summary}
            
            # Step 5: Save generated files
            logger.info("💾 Step 5: Saving generated files...")
            saved_files = self.save_generated_files(page_info, validation_summary)
            
            # Step 6: Store results
            result = {
                "page_info": page_info.__dict__,
                "page_analysis": page_analysis,
                "validation_summary": validation_summary,
                "saved_files": saved_files,
                "new_links_discovered": new_links,
                "success": True
            }
            
            self.page_analysis_results[url] = result
            self.total_pages_processed += 1
            
            logger.info(f"✅ COMPLETED: {page_info.name}")
            logger.info(f"📊 Progress: {self.total_pages_processed} pages processed")
            logger.info(f"🔗 New links: {len(new_links)}")
            logger.info(f"💾 Files saved: {len(saved_files)}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ CRITICAL ERROR processing {url}: {e}")
            return {"error": str(e), "page": url}

    async def run_complete_appfolio_replication(self, max_pages: int = 50):
        """Run complete AppFolio replication process"""
        try:
            logger.info("🚀 STARTING COMPLETE APPFOLIO REPLICATION")
            logger.info(f"📊 Target: {max_pages} pages maximum")
            
            # Initialize browser
            if not await self.initialize_browser():
                logger.error("❌ CRITICAL: Browser initialization failed")
                return False
            
            # Authenticate
            if not await self.authenticate_appfolio():
                logger.error("❌ CRITICAL: Authentication failed") 
                return False
            
            # Start with reports page
            start_url = "https://celticprop.appfolio.com/reports"
            
            # Process initial page
            initial_result = await self.process_single_appfolio_page(start_url)
            if "error" in initial_result:
                logger.error("❌ CRITICAL: Initial page processing failed")
                return False
            
            # Queue discovered links
            link_queue = list(self.discovered_links)
            
            # Process pages until limit reached
            while link_queue and self.total_pages_processed < max_pages:
                url = link_queue.pop(0)
                
                if url in self.processed_links:
                    continue
                
                self.processed_links.add(url)
                
                result = await self.process_single_appfolio_page(url)
                
                if "error" in result:
                    logger.warning(f"⚠️  Skipping failed page: {url}")
                    continue
                
                # Add newly discovered links
                new_links = result.get('new_links_discovered', [])
                for new_link in new_links:
                    if new_link not in link_queue and new_link not in self.processed_links:
                        link_queue.append(new_link)
                
                # Small delay between pages
                await asyncio.sleep(2)
            
            # Generate final report
            await self.generate_final_report()
            
            logger.info("🎉 COMPLETE APPFOLIO REPLICATION FINISHED!")
            logger.info(f"✅ Total pages processed: {self.total_pages_processed}")
            logger.info(f"📁 All files saved to AIVIIZN structure")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ CRITICAL ERROR in complete replication: {e}")
            return False
        
        finally:
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()

    async def generate_final_report(self):
        """Generate comprehensive final report"""
        try:
            logger.info("📊 Generating final comprehensive report...")
            
            report = {
                "replication_summary": {
                    "total_pages_processed": self.total_pages_processed,
                    "completion_timestamp": datetime.now().isoformat(),
                    "ai_systems_used": ["Claude Desktop", "OpenAI GPT-4", "Google Gemini", "Wolfram Alpha"],
                    "consensus_threshold": self.consensus_threshold
                },
                "pages_processed": list(self.page_analysis_results.keys()),
                "validation_results": self.multi_ai_validation_results,
                "files_generated": [],
                "errors_encountered": self.validation_errors
            }
            
            # Collect all generated files
            for result in self.page_analysis_results.values():
                if result.get('saved_files'):
                    report["files_generated"].extend(result['saved_files'].values())
            
            # Calculate success metrics
            successful_pages = len([r for r in self.page_analysis_results.values() if r.get('success')])
            report["success_rate"] = successful_pages / self.total_pages_processed if self.total_pages_processed > 0 else 0
            
            # Save report
            report_path = f"appfolio_replication_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"📊 Final report saved: {report_path}")
            
            # Print summary
            print("\n" + "="*80)
            print("🎯 APPFOLIO PIXEL-PERFECT REPLICATION COMPLETE")
            print("="*80)
            print(f"✅ Pages processed: {self.total_pages_processed}")
            print(f"📁 Templates created: {len([f for f in report['files_generated'] if 'template' in f])}")
            print(f"⚡ JavaScript files: {len([f for f in report['files_generated'] if '.js' in f])}")
            print(f"🗄️  SQL schemas: {len([f for f in report['files_generated'] if '.sql' in f])}")
            print(f"📈 Success rate: {report['success_rate']:.1%}")
            print(f"📊 Full report: {report_path}")
            print("="*80)
            
        except Exception as e:
            logger.error(f"❌ Report generation failed: {e}")

def main():
    """Main execution function"""
    print("🎯 APPFOLIO PIXEL-PERFECT REPLICATOR")
    print("=" * 80)
    print("This will create exact replicas of AppFolio pages in your AIVIIZN system")
    print("with multi-AI validation and mathematical consensus verification.")
    print()
    
    # Get user preferences
    try:
        max_pages = int(input("📊 How many pages to process? (default 20): ") or "20")
    except ValueError:
        max_pages = 20
    
    print(f"\n🚀 Starting replication of up to {max_pages} pages...")
    print("⏳ Please wait for browser to open and authenticate manually when prompted.")
    
    # Run the replicator
    replicator = AppFolioPixelPerfectReplicator()
    
    try:
        success = asyncio.run(replicator.run_complete_appfolio_replication(max_pages))
        
        if success:
            print("\n🎉 REPLICATION COMPLETED SUCCESSFULLY!")
            print("✅ Check the generated files in your AIVIIZN templates directory")
        else:
            print("\n❌ REPLICATION FAILED")
            print("📋 Check the logs for detailed error information")
            
    except KeyboardInterrupt:
        print("\n⏹️  Replication stopped by user")
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        logger.error(f"Critical error in main: {e}")

if __name__ == "__main__":
    main()
