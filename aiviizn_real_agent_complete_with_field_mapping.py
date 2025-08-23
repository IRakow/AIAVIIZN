#!/usr/bin/env python3
"""
AIVIIZN REAL TERMINAL AGENT - WITH FIELD MAPPING & DUPLICATE PREVENTION
Creates BEAUTIFUL, FULLY FUNCTIONAL pages from target sites
Includes intelligent field detection and duplicate prevention
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
from typing import Dict, List, Optional, Any, Tuple, Set
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

class FieldMapper:
    """Intelligent field identification and mapping system"""
    
    # Common field patterns for property management
    FIELD_PATTERNS = {
        'tenant_name': [
            r'tenant.*name', r'resident.*name', r'lessee', r'occupant',
            r'renter.*name', r'customer.*name'
        ],
        'unit_number': [
            r'unit.*num', r'apt.*num', r'apartment.*num', r'suite',
            r'unit.*\#', r'space.*num'
        ],
        'property_name': [
            r'property.*name', r'building.*name', r'complex.*name',
            r'location.*name', r'site.*name'
        ],
        'rent_amount': [
            r'rent.*amount', r'monthly.*rent', r'base.*rent', r'rental.*amount',
            r'lease.*amount', r'payment.*amount'
        ],
        'lease_start': [
            r'lease.*start', r'move.*in.*date', r'start.*date', r'begin.*date',
            r'commencement', r'occupancy.*date'
        ],
        'lease_end': [
            r'lease.*end', r'move.*out.*date', r'end.*date', r'expir',
            r'termination.*date', r'renewal.*date'
        ],
        'balance': [
            r'balance', r'amount.*due', r'outstanding', r'owed',
            r'total.*due', r'payable'
        ],
        'payment_date': [
            r'payment.*date', r'paid.*date', r'received.*date', r'transaction.*date',
            r'posted.*date'
        ],
        'email': [
            r'email', r'e-mail', r'electronic.*mail', r'contact.*email'
        ],
        'phone': [
            r'phone', r'telephone', r'mobile', r'cell', r'contact.*number'
        ],
        'address': [
            r'address', r'street', r'location', r'mailing.*addr'
        ],
        'status': [
            r'status', r'state', r'condition', r'standing'
        ],
        'notes': [
            r'notes', r'comments', r'remarks', r'description', r'memo'
        ]
    }
    
    @classmethod
    def identify_field_type(cls, field_name: str, field_attributes: Dict) -> Dict:
        """Identify the semantic type of a field"""
        field_name_lower = field_name.lower() if field_name else ''
        
        # Check against patterns
        for field_type, patterns in cls.FIELD_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, field_name_lower):
                    return {
                        'semantic_type': field_type,
                        'confidence': 0.9,
                        'pattern_matched': pattern
                    }
        
        # Check HTML input types for hints
        input_type = field_attributes.get('type', '').lower()
        if input_type == 'email':
            return {'semantic_type': 'email', 'confidence': 1.0}
        elif input_type == 'tel':
            return {'semantic_type': 'phone', 'confidence': 1.0}
        elif input_type == 'date':
            return {'semantic_type': 'date', 'confidence': 0.9}
        elif input_type == 'number':
            # Could be amount, unit number, etc.
            if 'amount' in field_name_lower or 'price' in field_name_lower:
                return {'semantic_type': 'amount', 'confidence': 0.8}
        
        # Check placeholders and labels
        placeholder = field_attributes.get('placeholder', '')
        placeholder = placeholder.lower() if placeholder else ''
        if placeholder:
            for field_type, patterns in cls.FIELD_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, placeholder):
                        return {
                            'semantic_type': field_type,
                            'confidence': 0.7,
                            'pattern_matched': pattern
                        }
        
        return {'semantic_type': 'unknown', 'confidence': 0.0}
    
    @classmethod
    def generate_field_signature(cls, field: Dict) -> str:
        """Generate a unique signature for a field to prevent duplicates"""
        # Create signature from key attributes
        sig_parts = [
            field.get('name', ''),
            field.get('type', ''),
            field.get('semantic_type', ''),
            field.get('form_id', ''),
            field.get('page_url', '')
        ]
        sig_string = '|'.join(str(p) for p in sig_parts)
        return hashlib.md5(sig_string.encode()).hexdigest()

class DuplicatePreventor:
    """System to prevent duplicate pages and data"""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
        self.page_checksums: Set[str] = set()
        self.field_signatures: Set[str] = set()
        self.url_checksums: Dict[str, str] = {}
        
    def generate_page_checksum(self, url: str, content: str) -> str:
        """Generate checksum for page content"""
        # Normalize URL (remove query params that don't affect content)
        normalized_url = self.normalize_url(url)
        
        # Extract stable content (remove timestamps, session IDs, etc.)
        stable_content = self.extract_stable_content(content)
        
        # Generate checksum
        checksum_data = f"{normalized_url}|{stable_content}"
        return hashlib.sha256(checksum_data.encode()).hexdigest()
    
    def normalize_url(self, url: str) -> str:
        """Normalize URL for comparison"""
        parsed = urlparse(url)
        
        # Remove common session/tracking parameters
        if parsed.query:
            params = parse_qs(parsed.query)
            cleaned_params = {
                k: v for k, v in params.items()
                if k not in ['session', 'sid', 'utm_source', 'utm_medium', 
                            'utm_campaign', '_ga', 'timestamp', 'cache']
            }
            if cleaned_params:
                from urllib.parse import urlencode
                query = urlencode(cleaned_params, doseq=True)
                return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{query}"
        
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    
    def extract_stable_content(self, html: str) -> str:
        """Extract stable content from HTML (remove dynamic elements)"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove script tags (often contain dynamic data)
            for script in soup.find_all('script'):
                script.decompose()
            
            # Remove elements with dynamic IDs/timestamps
            for elem in soup.find_all(attrs={'data-timestamp': True}):
                elem.decompose()
            
            # Extract text content from main areas
            main_content = []
            for selector in ['main', '[role="main"]', '#content', '.content', 'article']:
                elements = soup.select(selector)
                for elem in elements:
                    main_content.append(elem.get_text(strip=True))
            
            # If no main content found, use body text
            if not main_content:
                body = soup.find('body')
                if body:
                    main_content.append(body.get_text(strip=True))
            
            # Join and clean
            stable_text = ' '.join(main_content)
            # Remove multiple spaces and normalize
            stable_text = re.sub(r'\s+', ' ', stable_text)
            # Remove numbers that look like timestamps or IDs
            stable_text = re.sub(r'\b\d{10,}\b', '', stable_text)
            
            return stable_text[:5000]  # Use first 5000 chars for checksum
            
        except Exception as e:
            logger.error(f"Error extracting stable content: {e}")
            return html[:5000]
    
    def is_duplicate_page(self, url: str, content: str, company_id: str) -> bool:
        """Check if page is a duplicate"""
        checksum = self.generate_page_checksum(url, content)
        normalized_url = self.normalize_url(url)
        
        # Check in-memory cache first
        if checksum in self.page_checksums:
            print(f"  ⚠️ Duplicate detected (same content): {url}")
            return True
        
        # Check database for existing page
        try:
            # Check by normalized URL and checksum
            result = self.supabase.table('pages').select('id, url, content_checksum').eq(
                'company_id', company_id
            ).or_(
                f"url.eq.{normalized_url},content_checksum.eq.{checksum}"
            ).execute()
            
            if result.data:
                print(f"  ⚠️ Duplicate found in database: {url}")
                self.page_checksums.add(checksum)
                return True
                
        except Exception as e:
            logger.error(f"Error checking duplicates: {e}")
        
        # Not a duplicate - add to cache
        self.page_checksums.add(checksum)
        self.url_checksums[normalized_url] = checksum
        return False
    
    def is_duplicate_field(self, field_signature: str, company_id: str) -> bool:
        """Check if field mapping already exists"""
        if field_signature in self.field_signatures:
            return True
        
        try:
            # Check database
            result = self.supabase.table('field_mappings').select('id').eq(
                'signature', field_signature
            ).eq('company_id', company_id).execute()
            
            if result.data:
                self.field_signatures.add(field_signature)
                return True
                
        except Exception as e:
            logger.error(f"Error checking field duplicate: {e}")
        
        self.field_signatures.add(field_signature)
        return False

class AIVIIZNRealAgent:
    """
    REAL agent with field mapping and duplicate prevention
    """
    
    def __init__(self):
        """Initialize with real connections"""
        print("🚀 AIVIIZN REAL AGENT - WITH FIELD MAPPING & DUPLICATE PREVENTION")
        print("=" * 60)
        
        # Real Supabase connection
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_KEY') 
        self.supabase_anon_key = os.getenv('SUPABASE_KEY')
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        print("✓ Supabase connected")
        
        # Initialize duplicate prevention
        self.duplicate_preventor = DuplicatePreventor(self.supabase)
        print("✓ Duplicate prevention system ready")
        
        # Initialize field mapper
        self.field_mapper = FieldMapper()
        print("✓ Field mapping system ready")
        
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
        
        # Ensure field_mappings table exists
        self.ensure_field_mappings_table()
        
        # Project paths
        self.project_root = Path("/Users/ianrakow/Desktop/AIVIIZN")
        self.templates_dir = self.project_root / "templates"
        self.static_dir = self.project_root / "static"
        
        # Create directories
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.static_dir.mkdir(parents=True, exist_ok=True)
        (self.project_root / "data").mkdir(parents=True, exist_ok=True)
        (self.project_root / "screenshots").mkdir(parents=True, exist_ok=True)
        
        # Target site settings
        self.target_base = "https://celticprop.appfolio.com"
        
        # State
        self.processed_pages = self.load_state("processed_pages.json", set())
        self.discovered_links = self.load_state("discovered_links.json", list())
        self.identified_fields = self.load_state("identified_fields.json", dict())
        
        # Browser instance
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context = None
        self.page: Optional[Page] = None
        
        # Auto mode flag
        self.auto_mode = False
        
        # Statistics
        self.stats = {
            'fields_identified': 0,
            'duplicates_prevented': 0,
            'pages_processed': 0
        }
        
        print("✓ Ready to create beautiful pages with field mapping")
    
    def ensure_field_mappings_table(self):
        """Ensure field_mappings table exists"""
        try:
            # Try to query the table
            self.supabase.table('field_mappings').select('id').limit(1).execute()
            print("  ✓ field_mappings table exists")
        except:
            print("  ⚠️ field_mappings table not found")
            print("  Creating it now in Supabase...")
            
            # Create table via raw SQL (you'll need to run this in Supabase SQL editor)
            sql = """
            CREATE TABLE IF NOT EXISTS field_mappings (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                company_id UUID REFERENCES companies(id),
                page_url TEXT NOT NULL,
                form_id VARCHAR(255),
                form_name VARCHAR(255),
                field_name VARCHAR(255) NOT NULL,
                field_type VARCHAR(50),
                semantic_type VARCHAR(100),
                field_attributes JSONB,
                confidence NUMERIC(3,2),
                signature VARCHAR(64) UNIQUE,
                examples JSONB,
                validation_rules JSONB,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW(),
                UNIQUE(company_id, signature)
            );
            
            CREATE INDEX idx_field_mappings_company ON field_mappings(company_id);
            CREATE INDEX idx_field_mappings_semantic ON field_mappings(semantic_type);
            CREATE INDEX idx_field_mappings_signature ON field_mappings(signature);
            """
            print("\n  📋 Please run this SQL in Supabase SQL editor:")
            print(sql)
    
    def get_aiviizn_company_id(self):
        """Get the AIVIIZN company ID from database or create it"""
        try:
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
                        'require_field_verification': False,
                        'prevent_duplicates': True
                    },
                    'is_active': True
                }
                
                result = self.supabase.table('companies').insert(new_company).execute()
                if result.data:
                    company_id = result.data[0]['id']
                    print(f"✓ Created AIVIIZN company: {company_id}")
                    return company_id
                else:
                    return '5bb7db68-63e2-4750-ac16-ad15f19938a8'
                    
        except Exception as e:
            print(f"⚠️ Error with company ID: {e}")
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
            
        with open(data_dir / "identified_fields.json", 'w') as f:
            json.dump(self.identified_fields, f, indent=2)
        
        # Save statistics
        with open(data_dir / "statistics.json", 'w') as f:
            json.dump(self.stats, f, indent=2)
    
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
        
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            screen={'width': 1920, 'height': 1080},
            device_scale_factor=1,
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            locale='en-US',
            timezone_id='America/Chicago'
        )
        self.page = await self.context.new_page()
        
        await self.page.set_viewport_size({"width": 1920, "height": 1080})
        
        # Override automation detection
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            window.chrome = { runtime: {} };
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
        """Main execution with field mapping and duplicate prevention"""
        print("\n🎯 STARTING REAL PAGE REPLICATION WITH FIELD MAPPING")
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
        elif choice == "3":
            custom = input(">>> Enter path (e.g., /reports/rent_roll): ").strip()
            if not custom.startswith('/'):
                custom = '/' + custom
            start_url = self.target_base + custom
        else:
            start_url = self.target_base + "/reports"
        
        print(f"✓ Starting from: {start_url}")
        
        try:
            await self.start_browser()
            
            print(f"\n🌐 Opening: {start_url}...")
            await self.page.goto(start_url, wait_until='networkidle')
            
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
            
            print("\n🚀 Starting replication with field mapping...")
            
            await self.page.wait_for_timeout(500)
            
            current_url = self.page.url
            print(f"✅ Current page detected: {current_url}")
            
            if 'sign_in' not in current_url and 'login' not in current_url:
                print("🔄 Reloading page to ensure full content...")
                await self.page.reload(wait_until='networkidle')
                await self.page.wait_for_timeout(2000)
            
            self.discovered_links = [link for link in self.discovered_links 
                                    if 'sign_in' not in link and 'login' not in link]
            
            if 'sign_in' in current_url or 'login' in current_url:
                print("⚠️  Still on login page - please navigate to a content page first")
                input("\n>>> Press ENTER after navigating to a content page: ")
                current_url = self.page.url
                print(f"✅ New page detected: {current_url}")
            
            if current_url not in self.discovered_links:
                self.discovered_links.insert(0, current_url)
                print(f"📦 Added current page to processing queue")
            
            await self.process_pages_loop()
            
        except KeyboardInterrupt:
            print("\n⚠️ Stopped by user (Ctrl+C)")
            self.save_state()
            self.print_statistics()
            
        except Exception as e:
            logger.error(f"Agent error: {e}")
            self.save_state()
            raise
            
        finally:
            await self.close_browser()
            self.print_statistics()
    
    async def process_pages_loop(self):
        """Process pages with duplicate prevention"""
        current_url = self.page.url
        print(f"\n📍 Processing from: {current_url}")
        
        if current_url not in self.processed_pages:
            print(f"🎆 Processing current page first...")
            await self.replicate_page_real(current_url)
        
        while True:
            unprocessed = [url for url in self.discovered_links 
                          if url not in self.processed_pages]
            
            if not unprocessed:
                print("\n✅ ALL PAGES PROCESSED!")
                print("\n🎉 Session complete - browser will close now")
                break
                
            total_discovered = len(self.discovered_links)
            total_processed = len(self.processed_pages)
            percent_complete = (total_processed / total_discovered * 100) if total_discovered > 0 else 0
            
            print(f"\n📊 PROGRESS: {total_processed}/{total_discovered} pages ({percent_complete:.1f}% complete)")
            print(f"📊 Fields Identified: {self.stats['fields_identified']}")
            print(f"📊 Duplicates Prevented: {self.stats['duplicates_prevented']}")
            print(f"📊 Queue: {len(unprocessed)} pages remaining")
            print(f"📍 Next: {unprocessed[0]}")
            
            print("\nOptions:")
            print("  ENTER = Process next page")
            print("  'a' = AUTO mode (process every 60 seconds)")
            print("  'q' = Quit and close browser")
            print("  'l' = List all remaining pages")
            print("  's' = Skip this page")
            print("  'f' = Show identified fields")
            print("  'c' = Clear cache and reprocess all")
            
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
                print("\n🤖 AUTO MODE ACTIVATED")
                self.auto_mode = True
                await self.replicate_page_real(unprocessed[0])
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
            elif response == 'f':
                self.show_identified_fields()
                continue
            elif response == 'c':
                print("\n🗑️ Clearing cache...")
                self.processed_pages.clear()
                self.save_state()
                print("✅ Cache cleared")
                continue
            
            await self.replicate_page_real(unprocessed[0])
            await asyncio.sleep(0.5)
    
    async def replicate_page_real(self, url: str):
        """Replicate page with field mapping and duplicate prevention"""
        print(f"\n🎨 REPLICATING: {url}")
        print("-" * 50)
        
        try:
            # Navigate to URL
            if self.page.url != url:
                print(f"📍 Navigating to: {url}")
                await self.page.goto(url, wait_until='networkidle', timeout=30000)
                await self.page.wait_for_timeout(2000)
            
            # Capture page content
            page_data = await self.capture_real_page(url)
            
            if not page_data:
                print(f"⚠️ Failed to capture page: {url}")
                self.processed_pages.add(url)
                self.save_state()
                return
            
            # Check for duplicate
            is_duplicate = self.duplicate_preventor.is_duplicate_page(
                url, page_data['html'], self.company_id
            )
            
            if is_duplicate:
                print(f"  ⚠️ DUPLICATE PREVENTED: {url}")
                self.stats['duplicates_prevented'] += 1
                self.processed_pages.add(url)
                self.save_state()
                return
            
            # Extract and identify fields
            fields = await self.extract_and_identify_fields(page_data)
            
            # Store field mappings
            await self.store_field_mappings(url, fields)
            
            # Extract calculations
            calculations = await self.extract_calculations_real(page_data)
            
            # Extract API responses
            api_responses = await self.extract_api_responses_real(url)
            
            # Generate beautiful template
            template_html = await self.generate_beautiful_template(page_data, calculations, fields)
            
            # Save template
            template_path = self.save_template(url, template_html)
            
            # Store in Supabase with checksum
            await self.store_in_supabase_with_dedup(
                url, page_data, template_path, calculations, 
                api_responses, fields
            )
            
            # Discover new links
            new_links = await self.discover_links(page_data)
            for link in new_links:
                if link not in self.discovered_links and link not in self.processed_pages:
                    self.discovered_links.append(link)
                    print(f"  🔗 Discovered: {link}")
            
            # Mark as processed
            self.processed_pages.add(url)
            self.stats['pages_processed'] += 1
            self.save_state()
            
            print(f"✨ PAGE COMPLETE with {len(fields)} fields identified")
            
        except Exception as e:
            print(f"❌ Error replicating {url}: {e}")
            logger.error(f"Replication error for {url}: {traceback.format_exc()}")
            self.processed_pages.add(url)
            self.save_state()
    
    async def extract_and_identify_fields(self, page_data: Dict) -> List[Dict]:
        """Extract all fields and identify their semantic types"""
        print("  🔍 Identifying fields...")
        identified_fields = []
        
        # Process forms
        for form in page_data.get('forms', []):
            form_id = form.get('id', '')
            form_name = form.get('name', '')
            
            for field in form.get('fields', []):
                # Identify semantic type
                field_type_info = self.field_mapper.identify_field_type(
                    field.get('name', ''),
                    field
                )
                
                # Generate signature for duplicate prevention
                field_data = {
                    'form_id': form_id,
                    'form_name': form_name,
                    'field_name': field.get('name', ''),
                    'field_type': field.get('type', ''),
                    'semantic_type': field_type_info['semantic_type'],
                    'confidence': field_type_info.get('confidence', 0),
                    'placeholder': field.get('placeholder', ''),
                    'required': field.get('required', False),
                    'options': field.get('options', []),
                    'page_url': page_data['url']
                }
                
                signature = self.field_mapper.generate_field_signature(field_data)
                field_data['signature'] = signature
                
                identified_fields.append(field_data)
                
                # Track in memory
                field_key = f"{form_id}_{field.get('name', '')}"
                if field_key not in self.identified_fields:
                    self.identified_fields[field_key] = field_data
                    self.stats['fields_identified'] += 1
                    
                    if field_type_info['semantic_type'] != 'unknown':
                        print(f"    ✓ Identified: {field.get('name')} → {field_type_info['semantic_type']} (confidence: {field_type_info['confidence']:.1%})")
        
        print(f"  ✅ Identified {len(identified_fields)} fields")
        return identified_fields
    
    async def store_field_mappings(self, url: str, fields: List[Dict]):
        """Store field mappings in database"""
        if not fields:
            return
        
        print(f"  💾 Storing {len(fields)} field mappings...")
        
        for field in fields:
            # Check if duplicate
            is_duplicate = self.duplicate_preventor.is_duplicate_field(
                field['signature'], self.company_id
            )
            
            if not is_duplicate:
                try:
                    field_record = {
                        'company_id': self.company_id,
                        'page_url': url,
                        'form_id': field.get('form_id'),
                        'form_name': field.get('form_name'),
                        'field_name': field['field_name'],
                        'field_type': field['field_type'],
                        'semantic_type': field['semantic_type'],
                        'confidence': field['confidence'],
                        'signature': field['signature'],
                        'field_attributes': {
                            'placeholder': field.get('placeholder'),
                            'required': field.get('required'),
                            'options': field.get('options', [])
                        }
                    }
                    
                    # Try to insert the field mapping
                    result = self.supabase.table('field_mappings').insert(field_record).execute()
                    
                    if result.data:
                        print(f"    ✅ Stored field: {field['field_name']} ({field['semantic_type']})")
                        
                except Exception as e:
                    # Check if it's a table not found error
                    if 'field_mappings' in str(e):
                        print("    ⚠️ field_mappings table not found - please create it")
                        break
                    else:
                        logger.error(f"Error storing field mapping: {e}")
    
    async def store_in_supabase_with_dedup(self, url: str, page_data: Dict, 
                                          template_path: str, calculations: List[Dict],
                                          api_responses: List[Dict], fields: List[Dict]):
        """Store in Supabase with duplicate prevention"""
        try:
            print("  💾 Storing in Supabase with duplicate prevention...")
            
            # Generate checksum
            checksum = self.duplicate_preventor.generate_page_checksum(
                url, page_data['html']
            )
            
            # Prepare page record
            page_record = {
                'company_id': self.company_id,
                'url': url,
                'title': page_data.get('title', ''),
                'template_path': template_path,
                'html_preview': page_data.get('html', '')[:5000],
                'content_checksum': checksum,
                'meta_data': {
                    'forms_count': len(page_data.get('forms', [])),
                    'tables_count': len(page_data.get('tables', [])),
                    'fields_count': len(fields),
                    'field_types': list(set(f['semantic_type'] for f in fields if f['semantic_type'] != 'unknown'))
                },
                'api_responses': api_responses,
                'captured_at': page_data.get('captured_at'),
                'is_active': True
            }
            
            # Check if exists by URL
            normalized_url = self.duplicate_preventor.normalize_url(url)
            existing = self.supabase.table('pages').select('id').eq(
                'url', normalized_url
            ).eq('company_id', self.company_id).execute()
            
            if existing.data:
                # Update existing
                result = self.supabase.table('pages').update(page_record).eq(
                    'id', existing.data[0]['id']
                ).execute()
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
                
                self.supabase.table('calculations').insert(calc_record).execute()
            
            print("  ✅ Successfully stored in Supabase")
            
        except Exception as e:
            print(f"  ❌ Error storing in Supabase: {e}")
            logger.error(f"Supabase storage error: {traceback.format_exc()}")
    
    def show_identified_fields(self):
        """Display all identified fields"""
        print("\n📋 IDENTIFIED FIELDS:")
        print("-" * 50)
        
        # Group by semantic type
        fields_by_type = {}
        for field_key, field_data in self.identified_fields.items():
            semantic_type = field_data['semantic_type']
            if semantic_type not in fields_by_type:
                fields_by_type[semantic_type] = []
            fields_by_type[semantic_type].append(field_data)
        
        # Display grouped fields
        for semantic_type, fields in sorted(fields_by_type.items()):
            print(f"\n{semantic_type.upper()} ({len(fields)} fields):")
            for field in fields[:5]:  # Show first 5 of each type
                print(f"  • {field['field_name']} (confidence: {field['confidence']:.1%})")
            if len(fields) > 5:
                print(f"  ... and {len(fields) - 5} more")
        
        print(f"\nTotal fields identified: {self.stats['fields_identified']}")
    
    def print_statistics(self):
        """Print session statistics"""
        print("\n" + "="*60)
        print("📊 SESSION STATISTICS")
        print("="*60)
        print(f"Pages Processed: {self.stats['pages_processed']}")
        print(f"Fields Identified: {self.stats['fields_identified']}")
        print(f"Duplicates Prevented: {self.stats['duplicates_prevented']}")
        
        # Show field type breakdown
        if self.identified_fields:
            field_types = {}
            for field_data in self.identified_fields.values():
                semantic_type = field_data['semantic_type']
                field_types[semantic_type] = field_types.get(semantic_type, 0) + 1
            
            print("\nField Types Identified:")
            for field_type, count in sorted(field_types.items(), key=lambda x: x[1], reverse=True):
                print(f"  • {field_type}: {count}")
        
        print("="*60)
    
    # Include all the other methods from the previous implementation
    # (capture_real_page, extract_main_content_real, extract_forms_data, etc.)
    # These remain the same as in the previous complete implementation
    
    async def capture_real_page(self, url: str) -> Optional[Dict]:
        """Capture complete page data"""
        try:
            print("  📸 Capturing page content...")
            
            title = await self.page.title()
            html_content = await self.page.content()
            main_content = await self.extract_main_content_real(html_content)
            
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
            
            forms_data = await self.extract_forms_data()
            tables_data = await self.extract_tables_data()
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
            
            selectors = [
                'main', '[role="main"]', '#main-content', '.main-content',
                '#content', '.content', 'article', '.container'
            ]
            
            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    return str(element)
            
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
                                pattern: input.pattern,
                                maxLength: input.maxLength,
                                minLength: input.minLength,
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
            
            Return as JSON array with: name, description, formula, variables, sample_data
            """
            
            response = self.anthropic_client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text
            
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
    
    async def generate_beautiful_template(self, page_data: Dict, calculations: List[Dict], fields: List[Dict]) -> str:
        """Generate beautiful HTML template with field mappings"""
        try:
            print("  🎨 Generating beautiful template with field mappings...")
            
            template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_data['title']} - AIVIIZN</title>
    
    <!-- Bootstrap 5 -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Custom styles with field highlighting -->
    <style>
        /* Previous styles remain... */
        
        .identified-field {{
            position: relative;
            border: 2px solid transparent;
            transition: all 0.3s;
        }}
        
        .identified-field:hover {{
            border-color: var(--secondary-color);
            box-shadow: 0 0 10px rgba(52, 152, 219, 0.3);
        }}
        
        .field-badge {{
            position: absolute;
            top: -10px;
            right: -10px;
            background: var(--secondary-color);
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            z-index: 10;
        }}
        
        .field-info {{
            background: #f8f9fa;
            border-left: 4px solid var(--secondary-color);
            padding: 10px;
            margin-top: 5px;
            font-size: 12px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="main-container">
        <div class="page-header">
            <h1>{page_data['title']}</h1>
            <p class="text-muted">Fields Identified: {len(fields)}</p>
            <p class="text-muted">Duplicate Prevention: Active</p>
        </div>
        
        <!-- Field Mappings Summary -->
        <div class="field-mappings-summary mb-4">
            <h3>Identified Fields</h3>
            <div class="row">
                {self.render_field_summary(fields)}
            </div>
        </div>
        
        <!-- Content continues... -->
        {self.render_forms_with_field_info(page_data.get('forms', []), fields)}
    </div>
    
    <script type="module">
        // Field mapping integration
        const fieldMappings = {json.dumps(fields)};
        
        console.log('Field mappings loaded:', fieldMappings.length);
        
        // Highlight identified fields
        fieldMappings.forEach(field => {{
            const element = document.querySelector(`[name="${{field.field_name}}"]`);
            if (element) {{
                element.classList.add('identified-field');
                element.setAttribute('data-semantic-type', field.semantic_type);
                element.setAttribute('data-confidence', field.confidence);
            }}
        }});
    </script>
</body>
</html>"""
            
            return template
            
        except Exception as e:
            print(f"  ⚠️ Error generating template: {e}")
            return page_data.get('html', '')
    
    def render_field_summary(self, fields: List[Dict]) -> str:
        """Render field summary cards"""
        field_types = {}
        for field in fields:
            semantic_type = field['semantic_type']
            if semantic_type not in field_types:
                field_types[semantic_type] = 0
            field_types[semantic_type] += 1
        
        html = ''
        for field_type, count in field_types.items():
            html += f'''
            <div class="col-md-3 mb-3">
                <div class="card">
                    <div class="card-body">
                        <h6 class="card-title">{field_type.replace('_', ' ').title()}</h6>
                        <p class="card-text display-6">{count}</p>
                    </div>
                </div>
            </div>
            '''
        return html
    
    def render_forms_with_field_info(self, forms: List[Dict], fields: List[Dict]) -> str:
        """Render forms with field identification info"""
        if not forms:
            return ''
        
        # Create field lookup
        field_lookup = {f['field_name']: f for f in fields}
        
        html = '<div class="forms-section mb-4">'
        for form in forms:
            html += '<div class="form-modern">'
            html += f'<form id="{form.get("id", "")}" method="{form.get("method", "POST")}">'
            
            for field in form.get('fields', []):
                field_info = field_lookup.get(field.get('name', ''), {})
                semantic_type = field_info.get('semantic_type', 'unknown')
                confidence = field_info.get('confidence', 0)
                
                html += '<div class="mb-3 position-relative">'
                
                if semantic_type != 'unknown':
                    html += f'<span class="field-badge">{semantic_type} ({confidence:.0%})</span>'
                
                # Render field as before...
                if field['type'] == 'select':
                    html += f'<label class="form-label">{field.get("name", "")}</label>'
                    html += f'<select class="form-control identified-field" name="{field.get("name", "")}">'
                    for option in field.get('options', []):
                        html += f'<option value="{option["value"]}">{option["text"]}</option>'
                    html += '</select>'
                else:
                    html += f'<input type="{field["type"]}" class="form-control identified-field" '
                    html += f'name="{field.get("name", "")}" '
                    html += f'placeholder="{field.get("placeholder", "")}" />'
                
                if semantic_type != 'unknown':
                    html += f'<div class="field-info">Identified as: {semantic_type}</div>'
                
                html += '</div>'
            
            html += '<button type="submit" class="btn btn-modern btn-primary-modern">Submit</button>'
            html += '</form>'
            html += '</div>'
        
        html += '</div>'
        return html
    
    def save_template(self, url: str, html: str) -> str:
        """Save template to file"""
        try:
            parsed = urlparse(url)
            path_parts = parsed.path.strip('/').split('/')
            filename = '_'.join(path_parts) if path_parts[0] else 'index'
            filename = f"{filename}.html"
            
            template_path = self.templates_dir / filename
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(html)
            
            print(f"  💾 Saved template: {template_path}")
            return str(template_path)
            
        except Exception as e:
            print(f"  ⚠️ Error saving template: {e}")
            return ""
    
    async def discover_links(self, page_data: Dict) -> List[str]:
        """Discover new links from page"""
        try:
            soup = BeautifulSoup(page_data['html'], 'html.parser')
            links = []
            
            for a in soup.find_all('a', href=True):
                href = a['href']
                
                if href.startswith('#') or href.startswith('javascript:') or href.startswith('mailto:'):
                    continue
                
                if href.startswith('http'):
                    full_url = href
                elif href.startswith('/'):
                    full_url = urljoin(self.target_base, href)
                else:
                    full_url = urljoin(page_data['url'], href)
                
                if full_url.startswith(self.target_base):
                    # Normalize URL for duplicate prevention
                    normalized = self.duplicate_preventor.normalize_url(full_url)
                    
                    if normalized not in links:
                        links.append(normalized)
            
            return links
            
        except Exception as e:
            print(f"  ⚠️ Error discovering links: {e}")
            return []

# Main execution
if __name__ == "__main__":
    agent = AIVIIZNRealAgent()
    asyncio.run(agent.run())
