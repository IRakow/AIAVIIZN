#!/usr/bin/env python3
"""
AIVIIZN REAL TERMINAL AGENT - WITH AI-POWERED FIELD INTELLIGENCE
Creates BEAUTIFUL, FULLY FUNCTIONAL pages from target sites
Now with advanced AI field naming and calculation mapping
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
import google.generativeai as genai

# Import the enhanced field intelligence
from enhanced_field_intelligence import (
    EnhancedFieldMapper,
    CalculationVariableMapper,
    FieldIntelligence
)

# Import dual model analyzer for Gemini + OpenAI reliability (Claude excluded here)
from dual_model_analyzer import DualModelFieldAnalyzer

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
    """Basic field identification using patterns - kept as fallback"""
    
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
        """Identify the semantic type of a field using patterns"""
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
        
        # Check placeholders and labels - handle None case
        placeholder = field_attributes.get('placeholder') or ''
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
    REAL agent with AI-powered field intelligence
    """
    
    def __init__(self):
        """Initialize with real connections and AI intelligence"""
        print("🚀 AIVIIZN REAL AGENT - WITH AI-POWERED FIELD INTELLIGENCE")
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
        
        # Real Claude API
        self.anthropic_client = anthropic.Anthropic(
            api_key=os.getenv('ANTHROPIC_API_KEY')
        )
        print("✓ Claude API ready (Sonnet 4)")
        
        # Initialize OpenAI client
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if openai_api_key:
            self.openai_client = AsyncOpenAI(api_key=openai_api_key)
            print(f"✓ GPT-4o (Omni) connected")
        else:
            print("⚠️ OpenAI API key not found")
            self.openai_client = None
        
        # Initialize Gemini Ultra with JSON output configuration
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)
            # Configure for JSON output - CRITICAL FIX
            self.gemini_model = genai.GenerativeModel(
                'gemini-1.5-pro-002',  # Latest version
                generation_config={
                    'temperature': 0.1,
                    'top_p': 0.95,
                    'top_k': 40,
                    'max_output_tokens': 2048,
                    'response_mime_type': 'application/json'  # Forces JSON output
                }
            )
            print("✓ Gemini Ultra connected with JSON output")
        else:
            print("⚠️ Gemini API key not found - falling back to Claude/GPT")
            self.gemini_model = None
        
        # Initialize BOTH field mappers
        # Basic pattern-based mapper for fallback
        self.field_mapper = FieldMapper()
        print("✓ Basic field mapping ready (fallback)")
        
        # Initialize dual model analyzer with Gemini and OpenAI only (Claude excluded for field analysis)
        self.dual_analyzer = DualModelFieldAnalyzer(
            self.gemini_model,
            self.openai_client
        )
        print("✓ Dual model analyzer ready (Gemini + OpenAI)")
        print("  Note: Claude remains available for other tasks but excluded from field analysis")
        
        # AI-powered enhanced mapper for intelligent analysis
        if self.gemini_model:
            # Pass Gemini as both primary and secondary AI
            self.enhanced_field_mapper = EnhancedFieldMapper(
                self.gemini_model,
                self.gemini_model
            )
            print("✓ AI-powered field intelligence ready (Gemini Ultra)")
        else:
            self.enhanced_field_mapper = EnhancedFieldMapper(
                self.anthropic_client,
                self.openai_client
            )
            print("✓ AI-powered field intelligence ready")
        
        # Calculation variable mapper
        if self.gemini_model:
            self.calculation_mapper = CalculationVariableMapper(
                self.gemini_model
            )
            print("✓ Calculation mapping system ready (Gemini Ultra)")
        else:
            self.calculation_mapper = CalculationVariableMapper(
                self.anthropic_client
            )
            print("✓ Calculation mapping system ready")
        
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
        
        # Target site settings - Use environment variable or default
        self.target_base = os.getenv('TARGET_BASE_URL', 'https://celticprop.appfolio.com')
        
        # State
        self.processed_pages = self.load_state("processed_pages.json", set())
        self.discovered_links = self.load_state("discovered_links.json", list())
        self.identified_fields = self.load_state("identified_fields.json", dict())
        self.ai_field_mappings = self.load_state("ai_field_mappings.json", dict())
        
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
            'fields_ai_named': 0,
            'calculations_mapped': 0,
            'duplicates_prevented': 0,
            'pages_processed': 0,
            'total_cost': 0.0,
            'claude_cost': 0.0,
            'gemini_cost': 0.0
        }
        
        print("✓ Ready to create beautiful pages with AI field intelligence")
    
    def get_aiviizn_company_id(self):
        """Get or create AIVIIZN company ID"""
        try:
            # Check for existing AIVIIZN company
            result = self.supabase.table('companies').select('id').eq('name', 'AIVIIZN').execute()
            
            if result.data and len(result.data) > 0:
                company_id = result.data[0]['id']
                print(f"  ✓ Using existing AIVIIZN company: {company_id}")
                return company_id
            else:
                # Create AIVIIZN company
                result = self.supabase.table('companies').insert({
                    'name': 'AIVIIZN',
                    'domain': 'aiviizn.com',
                    'industry': 'Property Management Technology',
                    'subscription_tier': 'enterprise'
                }).execute()
                
                if result.data:
                    company_id = result.data[0]['id']
                    print(f"  ✓ Created AIVIIZN company: {company_id}")
                    return company_id
                else:
                    raise Exception("Failed to create company")
        except Exception as e:
            print(f"  ⚠️ Error with company ID: {e}")
            print("  Using default company ID")
            return '00000000-0000-0000-0000-000000000000'
    
    async def safe_navigate(self, url: str = None, action: str = 'goto', element=None):
        """Safe navigation wrapper that handles timeouts gracefully"""
        try:
            if action == 'goto' and url:
                # Try different wait strategies
                try:
                    await self.page.goto(url, wait_until='networkidle', timeout=10000)
                except PlaywrightTimeout:
                    # If networkidle fails, just wait for DOM
                    await self.page.goto(url, wait_until='domcontentloaded', timeout=5000)
                    await self.page.wait_for_timeout(2000)  # Give JS time to run
                    
            elif action == 'reload':
                try:
                    await self.page.reload(wait_until='networkidle', timeout=5000)
                except PlaywrightTimeout:
                    await self.page.reload(wait_until='domcontentloaded', timeout=5000)
                    
            elif action == 'click' and element:
                # Click and handle navigation
                try:
                    await element.click(timeout=5000)
                    await self.page.wait_for_load_state('networkidle', timeout=5000)
                except PlaywrightTimeout:
                    # Page is probably loaded enough
                    await self.page.wait_for_timeout(1000)
                    
            elif action == 'wait':
                # Just wait for content to stabilize
                try:
                    await self.page.wait_for_load_state('networkidle', timeout=3000)
                except PlaywrightTimeout:
                    await self.page.wait_for_timeout(1000)
                    
        except Exception as e:
            print(f"⚠️ Navigation issue: {e} - continuing anyway")
            await self.page.wait_for_timeout(1000)
    
    def ensure_field_mappings_table(self):
        """Ensure field_mappings table exists with AI fields"""
        try:
            # Try to query the table
            self.supabase.table('field_mappings').select('id').limit(1).execute()
            print("  ✓ field_mappings table exists")
        except:
            print("  ⚠️ field_mappings table not found")
            print("  Creating it now in Supabase...")
            
            # Enhanced table structure with AI fields
            sql = """
            CREATE TABLE IF NOT EXISTS field_mappings (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                company_id UUID REFERENCES companies(id),
                page_url TEXT NOT NULL,
                form_id VARCHAR(255),
                form_name VARCHAR(255),
                field_name VARCHAR(255) NOT NULL,
                ai_generated_name VARCHAR(255),
                field_type VARCHAR(50),
                semantic_type VARCHAR(100),
                data_type VARCHAR(50),
                unit_of_measure VARCHAR(50),
                is_calculated BOOLEAN DEFAULT FALSE,
                calculation_formula TEXT,
                related_fields JSONB,
                field_attributes JSONB,
                confidence NUMERIC(3,2),
                signature VARCHAR(64) UNIQUE,
                examples JSONB,
                validation_rules JSONB,
                context_clues JSONB,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW(),
                UNIQUE(company_id, signature)
            );
            
            CREATE INDEX idx_field_mappings_company ON field_mappings(company_id);
            CREATE INDEX idx_field_mappings_semantic ON field_mappings(semantic_type);
            CREATE INDEX idx_field_mappings_signature ON field_mappings(signature);
            CREATE INDEX idx_field_mappings_calculated ON field_mappings(is_calculated);
            CREATE INDEX idx_field_mappings_ai_name ON field_mappings(ai_generated_name);
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
                        'use_ai_field_naming': True,
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
                
                # Clean up discovered_links to remove invalid URLs
                if filename == "discovered_links.json" and isinstance(data, list):
                    cleaned_links = [
                        link for link in data 
                        if link and link != "processed" and link.startswith(('http://', 'https://'))
                    ]
                    if len(cleaned_links) < len(data):
                        print(f"  ⚠️ Cleaned {len(data) - len(cleaned_links)} invalid URLs from discovered links")
                    return cleaned_links
                
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
        
        with open(data_dir / "ai_field_mappings.json", 'w') as f:
            json.dump(self.ai_field_mappings, f, indent=2)
        
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
    
    async def extract_and_identify_fields(self, page_data: Dict) -> List[Dict]:
        """Extract all fields using AI-powered intelligence"""
        print("  🧠 Identifying fields with AI intelligence...")
        identified_fields = []
        
        # Process forms
        for form in page_data.get('forms', []):
            form_id = form.get('id', '')
            form_name = form.get('name', '')
            
            # Get all field names for context
            surrounding_fields = [f.get('name', '') for f in form.get('fields', [])]
            
            for field in form.get('fields', []):
                field_name = field.get('name', '')
                
                # Skip if no field name
                if not field_name and not field.get('id'):
                    continue
                
                # Use fallback name if field name is empty
                if not field_name:
                    field_name = field.get('id', f"field_{len(identified_fields)}")
                
                consensus_result = None  # Initialize for use outside try block
                try:
                    # Use Gemini and OpenAI dual consensus (Claude excluded from field analysis)
                    print(f"    🔍 Analyzing field with Gemini + OpenAI: {field_name}")
                    
                    # Get consensus result from Gemini and OpenAI only
                    consensus_result = await self.dual_analyzer.analyze_with_dual_consensus(
                        field_name,
                        field,
                        page_data.get('text_content', ''),
                        surrounding_fields
                    )
                    
                    # Convert to FieldIntelligence object for compatibility
                    from enhanced_field_intelligence import FieldIntelligence
                    field_intelligence = FieldIntelligence(
                        original_name=field_name,  # Added missing required argument
                        ai_generated_name=consensus_result.get('ai_generated_name', field_name),
                        semantic_type=consensus_result.get('semantic_type', 'unknown'),
                        data_type=consensus_result.get('data_type', 'text'),
                        unit_of_measure=consensus_result.get('unit_of_measure'),
                        is_calculated=consensus_result.get('is_calculated', False),
                        calculation_formula=consensus_result.get('calculation_formula'),
                        related_fields=consensus_result.get('related_fields', []),
                        confidence=consensus_result.get('confidence', 0.5),
                        context_clues=consensus_result.get('context_clues', {}),
                        description=consensus_result.get('description', '')  # Added missing required argument
                    )
                    
                    # Build comprehensive field data
                    field_data = {
                        'form_id': form_id,
                        'form_name': form_name,
                        'field_name': field_name,
                        'ai_generated_name': field_intelligence.ai_generated_name,
                        'field_type': field.get('type', ''),
                        'semantic_type': field_intelligence.semantic_type,
                        'data_type': field_intelligence.data_type,
                        'unit_of_measure': field_intelligence.unit_of_measure,
                        'is_calculated': field_intelligence.is_calculated,
                        'calculation_formula': field_intelligence.calculation_formula,
                        'related_fields': field_intelligence.related_fields,
                        'confidence': field_intelligence.confidence,
                        'context_clues': field_intelligence.context_clues,
                        'placeholder': field.get('placeholder', ''),
                        'required': field.get('required', False),
                        'options': field.get('options', []),
                        'page_url': page_data['url']
                    }
                    
                    # Generate signature for duplicate prevention
                    signature = self.field_mapper.generate_field_signature(field_data)
                    field_data['signature'] = signature
                    
                    identified_fields.append(field_data)
                    
                    # Track in memory
                    field_key = f"{form_id}_{field_name}"
                    if field_key not in self.identified_fields:
                        self.identified_fields[field_key] = field_data
                        self.stats['fields_identified'] += 1
                        
                        if field_intelligence.ai_generated_name != field_name:
                            self.stats['fields_ai_named'] += 1
                            print(f"    ✨ AI Named: {field_name} → {field_intelligence.ai_generated_name}")
                        
                        if field_intelligence.semantic_type != 'unknown':
                            provider_info = consensus_result.get('provider', 'unknown')
                            agreement = consensus_result.get('agreement', '')
                            if agreement == 'full':
                                print(f"    ✓ Identified: {field_intelligence.ai_generated_name} → {field_intelligence.semantic_type} ({field_intelligence.confidence:.1%}) [Gemini & OpenAI agreed]")
                            else:
                                print(f"    ✓ Identified: {field_intelligence.ai_generated_name} → {field_intelligence.semantic_type} ({field_intelligence.confidence:.1%}) [{provider_info}]")
                    
                    # Store AI mapping
                    self.ai_field_mappings[field_key] = {
                        'original': field_name,
                        'ai_name': field_intelligence.ai_generated_name,
                        'semantic_type': field_intelligence.semantic_type,
                        'data_type': field_intelligence.data_type,
                        'is_calculated': field_intelligence.is_calculated
                    }
                    
                except Exception as e:
                    print(f"    ⚠️ Dual model analysis failed for {field_name}: {e}")
                    # Fallback to basic pattern matching
                    field_type_info = self.field_mapper.identify_field_type(
                        field_name,
                        field
                    )
                    
                    field_data = {
                        'form_id': form_id,
                        'form_name': form_name,
                        'field_name': field_name,
                        'ai_generated_name': field_name,  # Use original name
                        'field_type': field.get('type', ''),
                        'semantic_type': field_type_info['semantic_type'],
                        'data_type': 'text',  # Default
                        'confidence': field_type_info.get('confidence', 0),
                        'placeholder': field.get('placeholder', ''),
                        'required': field.get('required', False),
                        'options': field.get('options', []),
                        'page_url': page_data['url']
                    }
                    
                    signature = self.field_mapper.generate_field_signature(field_data)
                    field_data['signature'] = signature
                    identified_fields.append(field_data)
                    
                    if field_type_info['semantic_type'] != 'unknown':
                        print(f"    ✓ Pattern Match: {field_name} → {field_type_info['semantic_type']} ({field_type_info['confidence']:.1%})")
        
        print(f"  ✅ Identified {len(identified_fields)} fields ({self.stats['fields_ai_named']} with AI naming)")
        return identified_fields
    
    async def extract_api_responses_real(self, url: str) -> List[Dict]:
        """Extract API responses from the page"""
        try:
            print("  🌐 Extracting API responses...")
            
            # Validate URL first
            if not url or url == "processed" or not url.startswith(('http://', 'https://')):
                print(f"  ⚠️ Invalid URL for API extraction: {url}")
                return []
            
            # Extract network requests
            api_responses = await self.page.evaluate("""
                () => {
                    // Get all XHR and Fetch requests from performance API
                    const entries = performance.getEntriesByType('resource')
                        .filter(entry => 
                            entry.initiatorType === 'xmlhttprequest' || 
                            entry.initiatorType === 'fetch'
                        );
                    
                    return entries.map(entry => ({
                        url: entry.name,
                        duration: entry.duration,
                        size: entry.transferSize,
                        type: entry.initiatorType
                    }));
                }
            """)
            
            print(f"  ✅ Found {len(api_responses)} API responses")
            return api_responses
            
        except Exception as e:
            print(f"  ⚠️ Error extracting API responses: {e}")
            return []
    
    async def extract_calculations_real(self, page_data: Dict) -> List[Dict]:
        """Extract calculations from the page"""
        try:
            print("  🧮 Extracting calculations...")
            calculations = []
            
            # Look for calculation patterns in scripts
            for script in page_data.get('scripts', []):
                content = script.get('content', '')
                
                # Find calculation patterns
                calc_patterns = [
                    r'(\w+)\s*=\s*([\w\.]+)\s*[\+\-\*\/]\s*([\w\.]+)',
                    r'total\w*\s*=',
                    r'sum\w*\s*=',
                    r'calculate\w*\(',
                    r'\w+\.toFixed\(',
                ]
                
                for pattern in calc_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        for match in matches[:5]:  # Limit to first 5 matches
                            calculations.append({
                                'name': f'Calculation {len(calculations) + 1}',
                                'formula': str(match) if isinstance(match, str) else ' '.join(match),
                                'type': 'javascript',
                                'source': 'inline_script'
                            })
            
            # Look for Excel-style formulas in tables
            for table in page_data.get('tables', []):
                for row in table.get('rows', []):
                    for cell in row:
                        if isinstance(cell, str) and cell.startswith('='):
                            calculations.append({
                                'name': f'Excel Formula {len(calculations) + 1}',
                                'formula': cell,
                                'type': 'excel',
                                'source': 'table_cell'
                            })
            
            print(f"  ✅ Found {len(calculations)} calculations")
            return calculations
            
        except Exception as e:
            print(f"  ⚠️ Error extracting calculations: {e}")
            return []
    
    async def extract_calculations_with_mapping(self, page_data: Dict, fields: List[Dict]) -> List[Dict]:
        """Extract calculations and map their variables to fields"""
        try:
            print("  🧮 Extracting calculations with variable mapping...")
            
            # First extract calculations using Claude
            calculations = await self.extract_calculations_real(page_data)
            
            # Now map variables for each calculation
            enhanced_calculations = []
            # Create field list in exact format the mapper expects
            fields_for_mapper = []
            for field in fields:
                # DEBUG: Check what field actually is
                if not isinstance(field, dict):
                    print(f"    WARNING: field is not a dict: {type(field)} - {field}")
                    continue
                    
                fields_for_mapper.append({
                    'field_name': field.get('field_name', ''),
                    'semantic_type': field.get('semantic_type', 'unknown'),
                    'data_type': field.get('data_type', 'text')
                })
            
            print(f"    DEBUG: Created {len(fields_for_mapper)} fields for mapper from {len(fields)} total fields")
            
            for i, calc in enumerate(calculations):
                formula = calc.get('formula', '')
                if formula:
                    try:
                        # Map variables to fields
                        variable_mappings = await self.calculation_mapper.map_calculation_variables(
                            formula,
                            fields_for_mapper,
                            page_data.get('text_content', '')
                        )
                        
                        calc['variable_mappings'] = variable_mappings
                        calc['formula_type'] = self.calculation_mapper.identify_formula_type(
                            formula,
                            [v['variable_name'] for v in variable_mappings] if variable_mappings else []
                        )
                        
                        if variable_mappings:
                            self.stats['calculations_mapped'] += 1
                            print(f"    ✓ Mapped calculation: {calc.get('name')} with {len(variable_mappings)} variables")
                    except Exception as map_error:
                        print(f"    ERROR mapping calc {i+1}: {map_error}")
                        print(f"    Formula was: {formula[:100]}...")
                        import traceback
                        print(f"    Traceback: {traceback.format_exc()}")
                        calc['variable_mappings'] = []
                        calc['formula_type'] = 'unknown'
                
                enhanced_calculations.append(calc)
            
            return enhanced_calculations
            
        except Exception as e:
            print(f"  ⚠️ Error in calculation mapping: {e}")
            import traceback
            print(f"  Full traceback:\n{traceback.format_exc()}")
            return []
    
    async def store_field_mappings(self, url: str, fields: List[Dict]):
        """Store field mappings with AI enhancements in database"""
        if not fields:
            return
        
        print(f"  💾 Storing {len(fields)} AI-enhanced field mappings...")
        
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
                        'ai_generated_name': field.get('ai_generated_name', field['field_name']),
                        'field_type': field['field_type'],
                        'semantic_type': field['semantic_type'],
                        'data_type': field.get('data_type', 'text'),
                        'unit_of_measure': field.get('unit_of_measure'),
                        'is_calculated': field.get('is_calculated', False),
                        'calculation_formula': field.get('calculation_formula'),
                        'related_fields': field.get('related_fields', []),
                        'confidence': field['confidence'],
                        'signature': field['signature'],
                        'field_attributes': {
                            'placeholder': field.get('placeholder'),
                            'required': field.get('required'),
                            'options': field.get('options', [])
                        },
                        'context_clues': field.get('context_clues', {})
                    }
                    
                    # Try to insert the field mapping
                    result = self.supabase.table('field_mappings').insert(field_record).execute()
                    
                    if result.data:
                        if field.get('ai_generated_name') != field['field_name']:
                            print(f"    ✨ Stored AI field: {field['field_name']} → {field['ai_generated_name']} ({field['semantic_type']})")
                        else:
                            print(f"    ✅ Stored field: {field['field_name']} ({field['semantic_type']})")
                        
                except Exception as e:
                    # Check if it's a table not found error
                    if 'field_mappings' in str(e):
                        print("    ⚠️ field_mappings table not found - please create it")
                        break
                    else:
                        logger.error(f"Error storing field mapping: {e}")
    
    async def replicate_page_real(self, url: str):
        """Replicate page with AI-powered field intelligence"""
        print(f"\n🎨 REPLICATING WITH AI INTELLIGENCE: {url}")
        print("-" * 50)
        
        # Validate URL first
        if not url or url == "processed" or not url.startswith(('http://', 'https://')):
            print(f"  ⚠️ INVALID URL SKIPPED: {url}")
            self.processed_pages.add(url)  # Mark as processed to skip it
            self.save_state()
            return
        
        try:
            # Navigate to URL
            if self.page.url != url:
                print(f"📍 Navigating to: {url}")
                await self.safe_navigate(url, action='goto')
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
            
            # Extract and identify fields with AI
            fields = await self.extract_and_identify_fields(page_data)
            
            # Store field mappings
            await self.store_field_mappings(url, fields)
            
            # Extract calculations with variable mapping
            calculations = await self.extract_calculations_with_mapping(page_data, fields)
            
            # Extract API responses
            api_responses = await self.extract_api_responses_real(url)
            
            # Generate beautiful template with AI-enhanced fields
            template_html = await self.generate_beautiful_template_with_ai(page_data, calculations, fields)
            
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
            
            print(f"✨ PAGE COMPLETE with {len(fields)} AI-analyzed fields")
            
            # Update interlinking in all templates after each new page
            self.update_template_links()
            
        except Exception as e:
            print(f"❌ Error replicating {url}: {e}")
            logger.error(f"Replication error for {url}: {traceback.format_exc()}")
            self.processed_pages.add(url)
            self.save_state()
    
    def update_template_links(self):
        """Update all template links to use Flask routes instead of external URLs"""
        try:
            print("  🔗 Updating interlinks in templates...")
            
            # Process each template file
            for template_file in self.templates_dir.rglob('*.html'):
                with open(template_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Replace target site links with Flask routes
                soup = BeautifulSoup(content, 'html.parser')
                updated = False
                
                # Update all links
                for tag in soup.find_all(['a', 'form']):
                    attr = 'href' if tag.name == 'a' else 'action'
                    url = tag.get(attr)
                    
                    if url and self.target_base in url:
                        # Convert to Flask route
                        flask_route = url.replace(self.target_base, '')
                        if not flask_route.startswith('/'):
                            flask_route = '/' + flask_route
                        
                        tag[attr] = flask_route
                        updated = True
                    elif url and url.startswith('/templates/'):
                        # Already a template link, convert to Flask route
                        flask_route = url.replace('/templates/', '/')
                        tag[attr] = flask_route
                        updated = True
                
                # Save updated template if changed
                if updated:
                    with open(template_file, 'w', encoding='utf-8') as f:
                        f.write(str(soup))
                    print(f"    ✓ Updated links in {template_file.name}")
                    
        except Exception as e:
            print(f"  ⚠️ Error updating template links: {e}")
    
    def create_base_template(self) -> str:
        """Create base.html template if it doesn't exist"""
        base_template_path = self.templates_dir / 'base.html'
        if not base_template_path.exists():
            base_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}AIVIIZN{% endblock %}</title>
    {% block styles %}{% endblock %}
</head>
<body>
    {% block content %}{% endblock %}
    {% block scripts %}{% endblock %}
</body>
</html>'''
            with open(base_template_path, 'w') as f:
                f.write(base_template)
        return str(base_template_path)
    
    def rewrite_links(self, html: str, current_url: str) -> str:
        """Rewrite internal links to point to Flask routes"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Rewrite all internal links
        for tag in soup.find_all(['a', 'form']):
            attr = 'href' if tag.name == 'a' else 'action'
            url = tag.get(attr)
            
            if url:
                # Convert to absolute URL
                absolute_url = urljoin(current_url, url)
                
                # If it's an internal link, rewrite it to Flask route
                if absolute_url.startswith(self.target_base):
                    # Generate Flask route from URL
                    flask_route = absolute_url.replace(self.target_base, '')
                    if not flask_route.startswith('/'):
                        flask_route = '/' + flask_route
                    
                    # Update the link to use Flask route
                    tag[attr] = flask_route
        
        # Rewrite asset links
        for tag in soup.find_all(['img', 'script', 'link']):
            if tag.name == 'img':
                attr = 'src'
            elif tag.name == 'script':
                attr = 'src'
            else:  # link
                attr = 'href'
            
            url = tag.get(attr)
            if url and not url.startswith(('data:', 'blob:', '#', 'http://', 'https://')):
                # Use Flask static URL
                if not url.startswith('/static/'):
                    tag[attr] = f"{{{{ url_for('static', filename='{url.lstrip('/')}') }}}}"
            elif url and url.startswith(('http://', 'https://')):
                # External URLs - leave as is unless from target site
                if self.target_base in url:
                    # Convert to local static asset
                    parsed = urlparse(url)
                    local_file = parsed.path.lstrip('/')
                    tag[attr] = f"{{{{ url_for('static', filename='{local_file}') }}}}"
        
        return str(soup)
    
    def generate_flask_app(self):
        """Generate complete Flask application with all routes"""
        print("\n🚀 GENERATING FLASK APPLICATION")
        print("="*60)
        
        flask_app_content = '''#!/usr/bin/env python3
"""
AIVIIZN Flask Application - Auto-generated from replicated pages
Serves all captured pages with proper interlinking
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
from functools import wraps
from datetime import datetime, timedelta
import os
import json
from pathlib import Path

app = Flask(__name__)
app.secret_key = 'aiviizn-secret-key-2025-change-in-production'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Template and static paths
app.template_folder = 'templates'
app.static_folder = 'static'

# Load page metadata
PAGE_METADATA = {}
data_dir = Path('data')
if (data_dir / 'processed_pages.json').exists():
    with open(data_dir / 'processed_pages.json', 'r') as f:
        processed_pages = json.load(f)
        for page_url in processed_pages:
            # Generate route name from URL
            route_name = page_url.replace('{target_base}', '').strip('/').replace('/', '_') or 'index'
            PAGE_METADATA[route_name] = {{
                'url': page_url,
                'title': route_name.replace('_', ' ').title()
            }}

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Base routes
@app.route('/')
def index():
    """Main landing page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Demo login
        if email == "admin@aiviizn.com" and password == "demo123":
            session.permanent = True
            session['user_id'] = 'demo-user-id'
            session['email'] = email
            flash('Welcome to AIVIIZN!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials. Use admin@aiviizn.com / demo123', 'danger')
    
    return render_template('auth/login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    return render_template('dashboard.html', pages=PAGE_METADATA)

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))
'''
        
        # Add dynamic routes for each captured page
        for page_url in self.processed_pages:
            route_path = page_url.replace(self.target_base, '').strip('/')
            if not route_path:
                route_path = 'index'
            
            # Generate function name from route
            func_name = route_path.replace('/', '_').replace('-', '_')
            if func_name[0].isdigit():
                func_name = 'page_' + func_name
            
            # Template path
            template_path = self.get_template_path_for_url(page_url)
            
            # Add route to Flask app
            route_code = f'''

@app.route('/{route_path}')
@login_required
def {func_name}():
    """Auto-generated route for {page_url}"""
    # Load any field mappings for this page
    field_mappings = {{}}
    
    # Load AI field mappings if available
    if (data_dir / 'ai_field_mappings.json').exists():
        with open(data_dir / 'ai_field_mappings.json', 'r') as f:
            all_mappings = json.load(f)
            # Filter mappings for this page
            page_mappings = {{k: v for k, v in all_mappings.items() if '{page_url}' in k}}
            field_mappings.update(page_mappings)
    
    return render_template('{template_path}', 
                         field_mappings=field_mappings,
                         current_page='{route_path}')
'''
            flask_app_content += route_code
        
        # Add API routes for field data
        flask_app_content += '''

# API Routes
@app.route('/api/fields/<page_id>')
@login_required
def api_get_fields(page_id):
    """Get field mappings for a specific page"""
    if (data_dir / 'identified_fields.json').exists():
        with open(data_dir / 'identified_fields.json', 'r') as f:
            fields = json.load(f)
            page_fields = [f for f in fields.values() if page_id in f.get('page_url', '')]
            return jsonify(page_fields)
    return jsonify([])

@app.route('/api/calculations/<page_id>')
@login_required
def api_get_calculations(page_id):
    """Get calculations for a specific page"""
    # Would load from database in production
    return jsonify([])

@app.route('/api/ai-mappings')
@login_required
def api_get_ai_mappings():
    """Get all AI field mappings"""
    if (data_dir / 'ai_field_mappings.json').exists():
        with open(data_dir / 'ai_field_mappings.json', 'r') as f:
            return jsonify(json.load(f))
    return jsonify({})

if __name__ == '__main__':
    app.run(debug=True, port=8080)
'''
        
        # Save Flask app
        flask_app_path = self.project_root / 'app_generated.py'
        with open(flask_app_path, 'w') as f:
            f.write(flask_app_content.replace('{target_base}', self.target_base))
        
        print(f"✅ Flask app generated: {flask_app_path}")
        print(f"   • {len(self.processed_pages)} routes created")
        print(f"   • AI field mappings integrated")
        print(f"   • Authentication enabled")
        print(f"\n📌 To run: python {flask_app_path}")
        
        return flask_app_path
    
    def get_template_path_for_url(self, url: str) -> str:
        """Get template path for a given URL"""
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')
        
        if len(path_parts) > 1:
            template_path = '/'.join(path_parts[:-1]) + '/' + path_parts[-1] + '.html'
        else:
            template_path = (path_parts[0] + '.html') if path_parts[0] else 'index.html'
        
        return template_path
    
    async def generate_beautiful_template_with_ai(self, page_data: Dict, calculations: List[Dict], fields: List[Dict]) -> str:
        """Generate beautiful template using Claude Sonnet 4"""
        try:
            print("  🎨 Creating beautiful template with Claude Sonnet 4...")
            
            # Prepare the prompt for Claude with original instructions
            prompt = f"""
            Create a beautiful, modern HTML template for this page:
            
            Page Title: {page_data.get('title', 'AIVIIZN')}
            Page URL: {page_data.get('url', '')}
            
            MAIN CONTENT HTML TO PRESERVE: {page_data.get('main_content', page_data.get('html', ''))[:15000]}
            
            Forms Data: {json.dumps(page_data.get('forms', [])[:2], indent=2)}
            Tables Data: {json.dumps(page_data.get('tables', [])[:2], indent=2)}
            
            AI-Identified Fields: {json.dumps([{
                'name': f['field_name'],
                'ai_name': f.get('ai_generated_name'),
                'type': f.get('semantic_type'),
                'data_type': f.get('data_type')
            } for f in fields[:20]], indent=2)}
            
            Calculations Found: {json.dumps(calculations[:5], indent=2)}
            
            Requirements:
            1. Extend 'base.html' using Jinja2 template syntax {{% extends 'base.html' %}}
            2. Use Bootstrap 5 and modern CSS that matches AIVIIZN design
            3. Add smooth animations and transitions
            4. Use a professional color scheme matching AIVIIZN brand
            5. Include all forms with proper validation
            6. Make tables sortable and searchable
            7. Add loading states and error handling
            8. Include Supabase integration for data
            9. Make everything actually WORK - no placeholders
            10. Highlight AI-enhanced fields with special styling
            11. Convert all links from {self.target_base} to Flask routes
            
            Create a complete, production-ready template that extends base.html.
            The template should be beautiful enough to impress clients and functional enough to use in production.
            
            IMPORTANT: Output ONLY the template code, no explanations.
            """
            
            # Use Claude Opus to generate the template
            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=20000
            )
            
            # Track costs (Sonnet 4 estimated: $30/M output, $6/M input) - increased to 20k tokens
            input_tokens = len(prompt) / 4  # Rough estimate: 4 chars per token
            output_tokens = len(response.content[0].text) / 4
            cost = (input_tokens * 0.000006) + (output_tokens * 0.00003)
            self.stats['claude_cost'] += cost
            self.stats['total_cost'] += cost
            
            template = response.content[0].text
            
            # Extract HTML from response if wrapped in code blocks
            if '```html' in template:
                template = template.split('```html')[1].split('```')[0]
            elif '```jinja2' in template:
                template = template.split('```jinja2')[1].split('```')[0]
            elif '```' in template:
                template = template.split('```')[1].split('```')[0]
            
            print("  ✅ Beautiful template generated by Claude Sonnet 4")
            return template
            
        except Exception as e:
            print(f"  ❌ CLAUDE SONNET 4 FAILED: {e}")
            print("  🛑 STOPPING - Claude Sonnet 4 is required for template generation")
            raise Exception("Claude Sonnet 4 failed - cannot continue")
    
    async def extract_exact_main_content(self, page_data: Dict) -> str:
        """Extract the exact main content area from target site, preserving structure"""
        try:
            print("  📐 Extracting exact target main structure...")
            
            # Use Gemini Ultra to identify main content if available
            if self.gemini_model:
                prompt = f"""
                Analyze this HTML and identify the CSS selector for the MAIN CONTENT area only.
                Exclude navigation, headers, footers, sidebars.
                
                HTML (first 10000 chars): {page_data.get('html', '')[:10000]}
                
                Return ONLY a CSS selector string like '#main-content' or '.content-area'.
                """
                
                try:
                    response = self.gemini_model.generate_content(prompt)
                    main_selector = response.text.strip().strip('"').strip("'").strip()
                    print(f"    ✨ Gemini identified selector: {main_selector}")
                    
                    # Extract using Gemini-identified selector
                    main_content = await self.page.evaluate(f"""
                        () => {{
                            const elem = document.querySelector('{main_selector}');
                            if (elem) {{
                                const clone = elem.cloneNode(true);
                                clone.querySelectorAll('nav, .sidebar, .navigation, header, footer').forEach(el => el.remove());
                                return clone.outerHTML;
                            }}
                            return null;
                        }}
                    """)
                    
                    if main_content:
                        return main_content
                except Exception as e:
                    print(f"    ❌ GEMINI FAILED: {e}")
                    print("    🛑 STOPPING - Gemini is required for extraction")
                    raise Exception("Gemini failed - cannot continue")
            
            # Fallback to original method
            main_content = await self.page.evaluate("""
                () => {
                    // Find the main content area using multiple strategies
                    let mainElement = null;
                    
                    // Strategy 1: Look for specific target site containers
                    const selectors = [
                        '#main-content',
                        '.main-content',
                        '[role="main"]',
                        'main',
                        '#content',
                        '.content-wrapper',
                        '.page-content',
                        '.reports-content',
                        '.report-container',
                        '.page-body',
                        '#page-content'
                    ];
                    
                    for (const selector of selectors) {
                        const elem = document.querySelector(selector);
                        if (elem && elem.innerHTML.length > 100) {
                            mainElement = elem;
                            break;
                        }
                    }
                    
                    // Strategy 2: If no main found, get the largest content div
                    if (!mainElement) {
                        const divs = document.querySelectorAll('div');
                        let largestDiv = null;
                        let largestSize = 0;
                        
                        divs.forEach(div => {
                            // Skip navigation, headers, footers
                            if (div.closest('nav, header, footer, .sidebar, .navigation')) return;
                            
                            const size = div.innerHTML.length;
                            if (size > largestSize && size > 500) {
                                largestSize = size;
                                largestDiv = div;
                            }
                        });
                        
                        mainElement = largestDiv;
                    }
                    
                    if (!mainElement) {
                        // Fallback: get body minus navigation
                        mainElement = document.body;
                    }
                    
                    // Clone the element to preserve it
                    const clone = mainElement.cloneNode(true);
                    
                    // Remove navigation elements from the clone
                    clone.querySelectorAll('nav, .sidebar, .navigation, header, footer').forEach(el => el.remove());
                    
                    // Preserve data attributes and form structures
                    clone.querySelectorAll('form, input, select, textarea').forEach(el => {
                        // Keep all attributes
                        Array.from(el.attributes).forEach(attr => {
                            el.setAttribute(attr.name, attr.value);
                        });
                    });
                    
                    return clone.outerHTML;
                }
            """)
            
            return main_content
            
        except Exception as e:
            print(f"  ⚠️ Error extracting exact main content: {e}")
            # Fallback to BeautifulSoup extraction
            return self.extract_main_content_beautifulsoup(page_data.get('html', ''))
    
    def extract_main_content_beautifulsoup(self, html: str) -> str:
        """Fallback extraction using BeautifulSoup"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove navigation elements
        for elem in soup.select('nav, header, footer, .sidebar, .navigation'):
            elem.decompose()
        
        # Find main content
        main_selectors = [
            'main', '[role="main"]', '#main-content', '.main-content',
            '#content', '.content', '.page-content', '.report-container'
        ]
        
        for selector in main_selectors:
            element = soup.select_one(selector)
            if element:
                return str(element)
        
        # If no main found, return body content
        body = soup.find('body')
        return str(body) if body else html
    
    def transform_to_aiviizn_styles(self, html_content: str, page_data: Dict) -> str:
        """Transform target HTML to use AIVIIZN CSS classes while preserving structure"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        print("  🎨 Applying AIVIIZN styles to target structure...")
        
        # CSS class mappings from target to AIVIIZN
        class_mappings = {
            # Tables
            'table': 'table table-hover',
            'data-table': 'table table-hover',
            'report-table': 'table table-hover',
            
            # Forms
            'form-control': 'form-control',
            'form-group': 'form-group mb-3',
            'form-label': 'form-label',
            
            # Buttons
            'btn': 'btn',
            'btn-primary': 'btn btn-primary',
            'btn-secondary': 'btn btn-secondary',
            'btn-success': 'btn btn-success',
            'btn-danger': 'btn btn-danger',
            
            # Cards/Panels
            'panel': 'card',
            'panel-heading': 'card-header',
            'panel-body': 'card-body',
            'panel-footer': 'card-footer',
            
            # Grid
            'row': 'row',
            'col': 'col',
            'container': 'container-fluid',
            
            # Alerts
            'alert': 'alert',
            'alert-success': 'alert alert-success',
            'alert-danger': 'alert alert-danger',
            'alert-warning': 'alert alert-warning',
            'alert-info': 'alert alert-info'
        }
        
        # Apply class mappings
        for element in soup.find_all(True):  # Find all elements
            if element.get('class'):
                original_classes = element.get('class')
                new_classes = []
                
                for cls in original_classes:
                    # Check if we have a mapping for this class
                    if cls in class_mappings:
                        new_classes.append(class_mappings[cls])
                    else:
                        # Keep original class for now (we can style it in our CSS)
                        new_classes.append(cls)
                
                element['class'] = ' '.join(new_classes) if new_classes else ''
        
        # Ensure all tables have proper structure
        for table in soup.find_all('table'):
            if 'table' not in (table.get('class') or ''):
                table['class'] = f"table table-hover {table.get('class', '')}"
            
            # Ensure thead/tbody structure
            if not table.find('thead'):
                # Try to identify header rows and wrap them
                first_row = table.find('tr')
                if first_row and first_row.find('th'):
                    thead = soup.new_tag('thead')
                    first_row.wrap(thead)
            
            if not table.find('tbody'):
                # Wrap all non-header rows in tbody
                rows = table.find_all('tr')
                if rows:
                    tbody = soup.new_tag('tbody')
                    for row in rows:
                        if not row.find_parent('thead'):
                            row.wrap(tbody)
        
        # Ensure all forms have proper Bootstrap structure
        for form in soup.find_all('form'):
            # Add form class if missing
            if not form.get('class'):
                form['class'] = 'form'
            
            # Wrap form controls in form-group if not already
            for input_elem in form.find_all(['input', 'select', 'textarea']):
                if input_elem.get('type') not in ['hidden', 'submit', 'button']:
                    parent = input_elem.parent
                    
                    # Add form-control class
                    input_classes = input_elem.get('class', '')
                    if 'form-control' not in input_classes:
                        input_elem['class'] = f"form-control {input_classes}".strip()
                    
                    # Ensure it's in a form-group
                    if not parent or 'form-group' not in (parent.get('class') or ''):
                        wrapper = soup.new_tag('div', **{'class': 'form-group mb-3'})
                        
                        # Find associated label
                        label = None
                        if input_elem.get('id'):
                            label = form.find('label', {'for': input_elem.get('id')})
                        
                        if label:
                            label['class'] = 'form-label'
                            label.extract()
                            wrapper.append(label)
                        
                        input_elem.wrap(wrapper)
        
        # Add wrapper divs for better layout
        content_wrapper = soup.new_tag('div', **{'class': 'content-header'})
        title_elem = soup.new_tag('h2')
        title_elem.string = page_data.get('title', 'Report')
        content_wrapper.append(title_elem)
        
        body_wrapper = soup.new_tag('div', **{'class': 'content-body'})
        
        # Move all content into body wrapper
        all_content = str(soup)
        body_soup = BeautifulSoup(all_content, 'html.parser')
        
        # Create final structure
        final_soup = BeautifulSoup('<div></div>', 'html.parser')
        final_div = final_soup.div
        final_div.append(content_wrapper)
        body_wrapper.append(body_soup)
        final_div.append(body_wrapper)
        
        return str(final_div)
    
    def enhance_fields_preserve_structure(self, html: str, fields: List[Dict]) -> str:
        """Enhance form fields with AI intelligence while preserving exact structure"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Create field lookup
        field_lookup = {f['field_name']: f for f in fields}
        
        # Find and enhance all form fields
        for tag in soup.find_all(['input', 'select', 'textarea']):
            field_name = tag.get('name')
            if field_name and field_name in field_lookup:
                field_info = field_lookup[field_name]
                
                # Add data attributes for AI intelligence (non-visible)
                tag['data-ai-name'] = field_info.get('ai_generated_name', field_name)
                tag['data-semantic-type'] = field_info.get('semantic_type', 'unknown')
                tag['data-data-type'] = field_info.get('data_type', 'text')
                tag['data-confidence'] = str(field_info.get('confidence', 0))
                
                if field_info.get('is_calculated'):
                    tag['data-calculated'] = 'true'
                    if field_info.get('calculation_formula'):
                        tag['data-formula'] = field_info['calculation_formula']
                
                # Add subtle CSS classes for styling
                existing_classes = tag.get('class', '')
                if isinstance(existing_classes, list):
                    existing_classes = ' '.join(existing_classes)
                
                # Add AI classes without disrupting original classes
                if field_info.get('is_calculated'):
                    tag['class'] = f"{existing_classes} ai-calculated-field".strip()
                elif field_info.get('ai_generated_name') != field_name:
                    tag['class'] = f"{existing_classes} ai-enhanced-field".strip()
                
                # Add informative title for tooltip
                confidence_pct = field_info.get('confidence', 0) * 100
                tag['title'] = f"AI: {field_info.get('ai_generated_name')} ({field_info.get('semantic_type')}) - {confidence_pct:.0f}% confidence"
        
        return str(soup)
    
    def extract_essential_scripts(self, page_data: Dict) -> str:
        """Extract only essential scripts for functionality, not styling"""
        essential_scripts = []
        
        # Use Gemini to identify essential scripts if available
        if self.gemini_model and page_data.get('scripts'):
            scripts_preview = []
            for i, script in enumerate(page_data.get('scripts', [])[:5]):
                if script['type'] == 'inline':
                    scripts_preview.append({
                        'index': i,
                        'preview': script.get('content', '')[:500]
                    })
            
            if scripts_preview:
                prompt = f"""
                Analyze these scripts and identify which are ESSENTIAL for calculations and form functionality.
                
                Scripts: {json.dumps(scripts_preview)}
                
                Return ONLY the index numbers of scripts that:
                1. Perform calculations
                2. Validate forms
                3. Update dynamic values
                4. Handle user interactions
                
                Skip scripts for: analytics, tracking, styling, ads, fonts
                
                Return as JSON array of index numbers like [0, 2, 3]
                """
                
                try:
                    response = self.gemini_model.generate_content(prompt)
                    response_text = response.text.strip()
                    
                    # Debug output to see what Gemini returned
                    if len(response_text) > 200:
                        print(f"    📝 Gemini response preview: {response_text[:200]}...")
                    else:
                        print(f"    📝 Gemini response: {response_text}")
                    
                    # Try multiple extraction methods
                    essential_indices = []
                    
                    # Method 1: Direct parse
                    try:
                        essential_indices = json.loads(response_text)
                        if isinstance(essential_indices, list):
                            print(f"    ✓ Parsed directly: {essential_indices}")
                    except json.JSONDecodeError as e:
                        print(f"    ⚠️ Direct parse failed: {e}")
                    
                    # Method 2: Extract from markdown
                    if not essential_indices and '```' in response_text:
                        if '```json' in response_text:
                            extracted = response_text.split('```json')[1].split('```')[0].strip()
                        else:
                            extracted = response_text.split('```')[1].split('```')[0].strip()
                        try:
                            essential_indices = json.loads(extracted)
                            print(f"    ✓ Extracted from markdown: {essential_indices}")
                        except json.JSONDecodeError:
                            pass
                    
                    # Method 3: Find array with regex
                    if not essential_indices:
                        import re
                        # Look for array pattern - more flexible regex
                        match = re.search(r'\[\s*(?:\d+\s*(?:,\s*\d+\s*)*)?\]', response_text)
                        if match:
                            try:
                                essential_indices = json.loads(match.group())
                                print(f"    ✓ Extracted with regex: {essential_indices}")
                            except json.JSONDecodeError:
                                pass
                    
                    # Method 4: Extract first array-like structure
                    if not essential_indices and '[' in response_text:
                        start = response_text.find('[')
                        if start != -1:
                            # Find matching bracket
                            count = 0
                            end = -1
                            for i in range(start, len(response_text)):
                                if response_text[i] == '[':
                                    count += 1
                                elif response_text[i] == ']':
                                    count -= 1
                                    if count == 0:
                                        end = i
                                        break
                            
                            if end != -1:
                                try:
                                    essential_indices = json.loads(response_text[start:end+1])
                                    print(f"    ✓ Extracted by bracket matching: {essential_indices}")
                                except json.JSONDecodeError:
                                    pass
                    
                    # Validate indices
                    if essential_indices and isinstance(essential_indices, list):
                        # Filter to only valid integers
                        essential_indices = [i for i in essential_indices if isinstance(i, int) and i >= 0]
                        print(f"    ✅ Using indices: {essential_indices}")
                    else:
                        print(f"    ⚠️ No valid indices extracted, using fallback")
                        essential_indices = []
                        
                        # Get the essential scripts
                        for i in essential_indices:
                            if i < len(page_data.get('scripts', [])):
                                script = page_data['scripts'][i]
                                if script['type'] == 'inline':
                                    essential_scripts.append(f"<script>\n{script['content']}\n</script>")
                        
                        print(f"    ✨ Gemini identified {len(essential_indices)} essential scripts")
                        return '\n'.join(essential_scripts)
                except json.JSONDecodeError as e:
                    print(f"    ⚠️ Error extracting calculations: {e}")
                    print(f"    👀 Falling back to pattern matching")
                    essential_indices = []
                except Exception as e:
                    print(f"    ❌ GEMINI FAILED: {e}")
                    print(f"    👀 Falling back to pattern matching instead of stopping")
                    # Don't raise exception - just continue with fallback
                    essential_indices = []
        
        # Fallback to pattern matching
        for script in page_data.get('scripts', []):
            if script['type'] == 'inline':
                content = script.get('content', '')
                
                # Skip analytics, tracking, and styling scripts
                skip_patterns = [
                    'google-analytics', 'gtag', 'analytics', 'tracking',
                    'style', 'css', 'font', 'theme'
                ]
                
                if not any(pattern in content.lower() for pattern in skip_patterns):
                    # Check if it contains form logic or calculations
                    keep_patterns = [
                        'calculate', 'validate', 'submit', 'form',
                        'total', 'sum', 'amount'
                    ]
                    
                    if any(pattern in content.lower() for pattern in keep_patterns):
                        essential_scripts.append(f"<script>\n{content}\n</script>")
        
        return '\n'.join(essential_scripts)
    
    def enhance_fields_in_html(self, html: str, fields: List[Dict]) -> str:
        """Enhance form fields in HTML with AI intelligence attributes"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Create field lookup
        field_lookup = {f['field_name']: f for f in fields}
        
        # Find and enhance all form fields
        for tag in soup.find_all(['input', 'select', 'textarea']):
            field_name = tag.get('name')
            if field_name and field_name in field_lookup:
                field_info = field_lookup[field_name]
                
                # Add data attributes for AI intelligence
                tag['data-ai-name'] = field_info.get('ai_generated_name', field_name)
                tag['data-semantic-type'] = field_info.get('semantic_type', 'unknown')
                tag['data-data-type'] = field_info.get('data_type', 'text')
                tag['data-confidence'] = str(field_info.get('confidence', 0))
                
                if field_info.get('is_calculated'):
                    tag['data-calculated'] = 'true'
                    if field_info.get('calculation_formula'):
                        tag['data-formula'] = field_info['calculation_formula']
                
                # Add CSS class for styling
                existing_classes = tag.get('class', [])
                if isinstance(existing_classes, str):
                    existing_classes = existing_classes.split()
                
                if field_info.get('is_calculated'):
                    existing_classes.append('ai-calculated-field')
                elif field_info.get('ai_generated_name') != field_name:
                    existing_classes.append('ai-enhanced-field')
                
                tag['class'] = ' '.join(existing_classes)
                
                # Add title for tooltip
                confidence_pct = field_info.get('confidence', 0) * 100
                tag['title'] = f"AI: {field_info.get('ai_generated_name')} ({field_info.get('semantic_type')}) - {confidence_pct:.0f}% confidence"
        
        return str(soup)
    
    def save_template(self, url: str, html: str) -> str:
        """Save template with PROPER DESCRIPTIVE NAMES - NO index.html"""
        try:
            parsed = urlparse(url)
            path_parts = parsed.path.strip('/').split('/')
            
            # Determine proper directory and filename based on URL/content
            url_lower = url.lower()
            path_str = parsed.path.lower()
            
            # Extract the last meaningful part of the URL for naming
            if path_parts and path_parts[-1]:
                base_name = path_parts[-1]
            elif path_parts and len(path_parts) > 1 and path_parts[-2]:
                base_name = path_parts[-2]
            else:
                # Parse domain for home pages
                if 'dashboard' in url_lower:
                    base_name = 'dashboard'
                elif 'home' in url_lower:
                    base_name = 'home'
                elif 'main' in url_lower:
                    base_name = 'main'
                else:
                    base_name = 'portal'  # Better than index
            
            # CATEGORY MAPPING with proper file names
            if 'vacancies' in path_str or 'vacancy' in path_str:
                template_dir = self.templates_dir / 'leasing'
                filename = 'vacancies.html'
            elif 'tenant' in path_str:
                template_dir = self.templates_dir / 'people'
                filename = 'tenants.html'
            elif 'resident' in path_str:
                template_dir = self.templates_dir / 'people'
                filename = 'residents.html'
            elif 'owner' in path_str:
                template_dir = self.templates_dir / 'people'
                filename = 'owners.html'
            elif 'vendor' in path_str:
                template_dir = self.templates_dir / 'people'
                filename = 'vendors.html'
            elif 'rental' in path_str and 'application' in path_str:
                template_dir = self.templates_dir / 'leasing'
                filename = 'rental_applications.html'
            elif 'lease_document' in path_str:
                template_dir = self.templates_dir / 'leasing'
                if 'out_for_signing' in path_str:
                    filename = 'lease_documents_out_for_signing.html'
                elif 'printed' in path_str:
                    filename = 'lease_documents_printed.html'
                else:
                    filename = 'lease_documents.html'
            elif 'lease' in path_str and 'leasing' not in path_str:
                template_dir = self.templates_dir / 'leasing'
                filename = 'leases.html'
            elif 'guest_card' in path_str:
                template_dir = self.templates_dir / 'leasing'
                filename = 'guest_cards.html'
            elif 'listing' in path_str:
                template_dir = self.templates_dir / 'leasing'
                filename = 'listings.html'
            elif 'renewal' in path_str:
                template_dir = self.templates_dir / 'leasing'
                filename = 'renewals.html'
            elif 'signal' in path_str:
                template_dir = self.templates_dir / 'leasing'
                filename = 'signals.html'
            elif 'metric' in path_str and 'leasing' in path_str:
                template_dir = self.templates_dir / 'leasing'
                filename = 'metrics.html'
            elif 'property' in path_str and 'dashboard' in path_str:
                template_dir = self.templates_dir
                filename = 'property_dashboard.html'
            elif 'properties' in path_str:
                template_dir = self.templates_dir / 'properties'
                filename = 'properties.html'
            elif 'unit_turn' in path_str:
                template_dir = self.templates_dir / 'maintenance'
                filename = 'unit_turns.html'
            elif 'work_order' in path_str:
                template_dir = self.templates_dir / 'maintenance'
                if 'recurring' in path_str:
                    filename = 'recurring_work_orders.html'
                else:
                    filename = 'work_orders.html'
            elif 'inspection' in path_str:
                template_dir = self.templates_dir / 'maintenance'
                filename = 'inspections.html'
            elif 'inventory' in path_str:
                template_dir = self.templates_dir / 'maintenance'
                filename = 'inventory.html'
            elif 'purchase_order' in path_str:
                template_dir = self.templates_dir / 'maintenance'
                filename = 'purchase_orders.html'
            elif 'project' in path_str and 'maintenance' in path_str:
                template_dir = self.templates_dir / 'maintenance'
                filename = 'projects.html'
            elif 'bank' in path_str and 'account' in path_str:
                template_dir = self.templates_dir / 'accounting'
                filename = 'bank_accounts.html'
            elif 'bank' in path_str and 'transfer' in path_str:
                template_dir = self.templates_dir / 'accounting'
                filename = 'bank_transfers.html'
            elif 'gl_account' in path_str or 'general_ledger' in path_str:
                template_dir = self.templates_dir / 'accounting'
                filename = 'gl_accounts.html'
            elif 'journal' in path_str and 'entr' in path_str:
                template_dir = self.templates_dir / 'accounting'
                filename = 'journal_entries.html'
            elif 'payable' in path_str:
                template_dir = self.templates_dir / 'accounting'
                filename = 'payables.html'
            elif 'receivable' in path_str:
                template_dir = self.templates_dir / 'accounting'
                filename = 'receivables.html'
            elif 'diagnostic' in path_str:
                template_dir = self.templates_dir / 'accounting'
                filename = 'diagnostics.html'
            elif 'rent_roll' in path_str:
                template_dir = self.templates_dir
                filename = 'rent_roll.html'
            elif 'income_statement' in path_str:
                template_dir = self.templates_dir
                filename = 'income_statement.html'
            elif 'balance_sheet' in path_str:
                template_dir = self.templates_dir / 'buffered_reports'
                filename = 'balance_sheet.html'
            elif 'delinquency' in path_str:
                template_dir = self.templates_dir
                filename = 'delinquency_report.html'
            elif 'check_register' in path_str:
                template_dir = self.templates_dir / 'buffered_reports'
                filename = 'check_register.html'
            elif 'inventory_status' in path_str:
                template_dir = self.templates_dir / 'buffered_reports'
                filename = 'inventory_status.html'
            elif 'additional_fee' in path_str:
                template_dir = self.templates_dir / 'buffered_reports'
                filename = 'additional_fees.html'
            elif 'memorized_reports' in path_str:
                template_dir = self.templates_dir / 'memorized_reports'
                # Extract report ID if present
                id_match = re.search(r'/(\d+)', parsed.path)
                if id_match:
                    filename = f"{id_match.group(1)}.html"
                else:
                    filename = f"report_{base_name}.html"
            elif 'buffered_reports' in path_str:
                template_dir = self.templates_dir / 'buffered_reports'
                filename = f"{base_name}.html"
            elif 'report' in path_str:
                template_dir = self.templates_dir / 'reports'
                if base_name and base_name != 'report':
                    filename = f"{base_name}.html"
                else:
                    filename = 'financial_reports.html'
            elif 'auth' in path_str or 'login' in path_str or 'sign_in' in path_str:
                template_dir = self.templates_dir / 'auth'
                if 'register' in path_str:
                    filename = 'register.html'
                else:
                    filename = 'login.html'
            elif 'user' in path_str and 'sign_in' in path_str:
                template_dir = self.templates_dir / 'users'
                filename = 'sign_in.html'
            elif 'user' in path_str and 'setting' in path_str:
                template_dir = self.templates_dir / 'admin'
                filename = 'user_settings.html'
            elif 'company' in path_str and 'setting' in path_str:
                template_dir = self.templates_dir / 'admin'
                filename = 'company_settings.html'
            elif 'admin' in path_str and 'user' in path_str:
                template_dir = self.templates_dir / 'admin'
                filename = 'users.html'
            elif 'email' in path_str and 'admin' in path_str:
                template_dir = self.templates_dir / 'admin'
                filename = 'emails.html'
            elif 'showing' in path_str:
                template_dir = self.templates_dir / 'admin'
                filename = 'showings.html'
            elif 'dashboard' in path_str:
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
                    filename = 'dashboard.html'
            elif 'calendar' in path_str:
                template_dir = self.templates_dir
                filename = 'calendar.html'
            elif 'inbox' in path_str or 'message' in path_str:
                template_dir = self.templates_dir
                filename = 'inbox.html'
            elif 'pending' in path_str:
                template_dir = self.templates_dir
                filename = 'pending.html'
            elif 'processed' in path_str:
                template_dir = self.templates_dir
                filename = 'processed.html'
            elif 'payment' in path_str and 'online' in path_str:
                template_dir = self.templates_dir
                filename = 'online_payments.html'
            elif 'metric' in path_str:
                template_dir = self.templates_dir
                filename = 'metrics.html'
            elif 'letter' in path_str:
                template_dir = self.templates_dir / 'communication'
                filename = 'letters.html'
            elif 'phone' in path_str and 'log' in path_str:
                template_dir = self.templates_dir / 'communication'
                filename = 'phone_logs.html'
            elif 'search' in path_str and 'advanced' in path_str:
                template_dir = self.templates_dir / 'search'
                filename = 'advanced_search.html'
            elif 'stack' in path_str or 'marketplace' in path_str:
                template_dir = self.templates_dir / 'marketplace'
                filename = 'stack_marketplace.html'
            elif 'document_template' in path_str:
                template_dir = self.templates_dir
                filename = 'document_templates.html'
            elif 'whats_new' in path_str or 'what_new' in path_str:
                template_dir = self.templates_dir
                filename = 'whats_new.html'
            elif 'survey' in path_str:
                template_dir = self.templates_dir / 'reporting'
                filename = 'surveys.html'
            elif 'scheduled_report' in path_str:
                template_dir = self.templates_dir / 'reporting'
                filename = 'scheduled_reports.html'
            elif 'financial_report' in path_str:
                template_dir = self.templates_dir / 'reporting'
                filename = 'financial_reports.html'
            elif 'vacancy_report' in path_str:
                template_dir = self.templates_dir / 'reporting'
                filename = 'vacancy_reports.html'
            elif path_str == '/' or not path_str:
                # Root/home page - use descriptive name
                template_dir = self.templates_dir
                filename = 'dashboard.html'  # Most likely the dashboard
            else:
                # Default: use URL structure with meaningful name
                if len(path_parts) > 1:
                    template_dir = self.templates_dir / '/'.join(path_parts[:-1])
                    filename = f"{base_name}.html"
                else:
                    template_dir = self.templates_dir
                    filename = f"{base_name}.html"
            
            # NEVER use index.html - ensure we have a meaningful name
            if filename == 'index.html' or filename == '.html' or not filename:
                # Extract something meaningful from the URL
                if base_name and base_name != 'index':
                    filename = f"{base_name}.html"
                elif 'appfolio' in parsed.netloc:
                    filename = 'appfolio_property_manager.html'
                else:
                    filename = 'portal.html'  # Better default than index
            
            # Ensure directory exists
            template_dir.mkdir(parents=True, exist_ok=True)
            template_path = template_dir / filename
            
            # SHOW WHAT'S BEING CREATED RIGHT NOW
            print(f"\n{'='*60}")
            print(f"🎯 CREATING TEMPLATE RIGHT NOW:")
            print(f"📂 DIRECTORY: {template_dir}")
            print(f"📄 FILENAME: {filename}")
            print(f"🔗 FULL PATH: {template_path}")
            print(f"💾 SIZE: {len(html):,} bytes")
            print(f"🌐 FROM URL: {url}")
            print(f"{'='*60}\n")
            
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(html)
            
            return str(template_path)
            
        except Exception as e:
            print(f"❌ ERROR SAVING: {e}")
            import traceback
            print(traceback.format_exc())
            return ""

    def render_ai_field_summary(self, fields: List[Dict]) -> str:
        """Render AI field analysis summary"""
        # Group by data type
        data_types = {}
        for field in fields:
            dtype = field.get('data_type', 'text')
            if dtype not in data_types:
                data_types[dtype] = []
            data_types[dtype].append(field)
        
        html = ''
        colors = {
            'currency': '#27ae60',
            'percentage': '#e74c3c', 
            'date': '#3498db',
            'number': '#f39c12',
            'text': '#95a5a6',
            'boolean': '#9b59b6'
        }
        
        for dtype, dtype_fields in data_types.items():
            color = colors.get(dtype, '#7f8c8d')
            html += f'''
            <div class="col-md-4 mb-3">
                <div class="card" style="border-left: 4px solid {color};">
                    <div class="card-body">
                        <h6 class="card-title">{dtype.title()} Fields</h6>
                        <p class="card-text display-6">{len(dtype_fields)}</p>
                        <small class="text-muted">
                            {', '.join([f.get('ai_generated_name', f['field_name'])[:20] for f in dtype_fields[:3]])}
                            {f'... +{len(dtype_fields)-3} more' if len(dtype_fields) > 3 else ''}
                        </small>
                    </div>
                </div>
            </div>
            '''
        return html
    
    def render_calculations_summary(self, calculations: List[Dict]) -> str:
        """Render calculations with mapped variables"""
        if not calculations:
            return ''
        
        html = '<div class="calculations-section mb-4 bg-white p-4 rounded">'
        html += '<h4>Detected Calculations & Formulas</h4>'
        
        for calc in calculations:
            html += f'''
            <div class="calculation-card mb-3 p-3 border rounded">
                <h5>{calc.get('name', 'Calculation')}</h5>
                <p class="text-muted">{calc.get('description', '')}</p>
                <div class="formula">{calc.get('formula', 'No formula')}</div>
            '''
            
            # Show variable mappings
            if calc.get('variable_mappings'):
                html += '<div class="mt-2"><strong>Variables:</strong><ul>'
                for var in calc['variable_mappings']:
                    html += f'''<li>
                        <span class="ai-name">{var.get('variable_name')}</span>
                        → {var.get('semantic_meaning', 'Unknown')}
                        <span class="data-type">{var.get('data_type', 'unknown')}</span>
                    </li>'''
                html += '</ul></div>'
            
            html += '</div>'
        
        html += '</div>'
        return html
    
    def render_forms_with_ai_intelligence(self, forms: List[Dict], fields: List[Dict]) -> str:
        """Render forms with AI field intelligence"""
        if not forms:
            return ''
        
        # Create field lookup
        field_lookup = {f['field_name']: f for f in fields}
        
        html = '<div class="forms-section mb-4">'
        for form in forms:
            html += '<div class="form-modern bg-white p-4 rounded mb-3">'
            html += f'<form id="{form.get("id", "")}" method="{form.get("method", "POST")}">'
            
            for field in form.get('fields', []):
                field_name = field.get('name', '')
                field_info = field_lookup.get(field_name, {})
                
                ai_name = field_info.get('ai_generated_name', field_name)
                semantic_type = field_info.get('semantic_type', 'unknown')
                data_type = field_info.get('data_type', 'text')
                confidence = field_info.get('confidence', 0)
                is_calculated = field_info.get('is_calculated', False)
                unit = field_info.get('unit_of_measure', '')
                
                html += '<div class="mb-3 position-relative">'
                
                # Add badges for special fields
                if is_calculated:
                    html += f'<span class="field-badge calculated-badge">CALCULATED</span>'
                elif ai_name != field_name:
                    html += f'<span class="field-badge">AI NAMED</span>'
                
                # Label with AI name
                html += f'<label class="form-label">'
                html += f'<span class="ai-name">{ai_name}</span>'
                if ai_name != field_name:
                    html += f' <span class="original-name">(was: {field_name})</span>'
                html += f'<span class="data-type">{data_type}</span>'
                if unit:
                    html += f' <small class="text-muted">({unit})</small>'
                html += '</label>'
                
                # Render field
                field_classes = 'form-control'
                if is_calculated:
                    field_classes += ' calculated-field'
                elif ai_name != field_name:
                    field_classes += ' ai-field'
                
                if field['type'] == 'select':
                    html += f'<select class="{field_classes}" name="{field_name}" '
                    html += f'data-ai-name="{ai_name}" data-semantic-type="{semantic_type}">'
                    for option in field.get('options', []):
                        html += f'<option value="{option["value"]}">{option["text"]}</option>'
                    html += '</select>'
                else:
                    input_type = field['type']
                    # Map data type to HTML input type
                    if data_type == 'currency' or data_type == 'number':
                        input_type = 'number'
                    elif data_type == 'date':
                        input_type = 'date'
                    elif data_type == 'boolean':
                        input_type = 'checkbox'
                    
                    html += f'<input type="{input_type}" class="{field_classes}" '
                    html += f'name="{field_name}" '
                    html += f'data-ai-name="{ai_name}" data-semantic-type="{semantic_type}" '
                    html += f'placeholder="{field.get("placeholder", "")}" '
                    
                    if data_type == 'currency':
                        html += 'step="0.01" '
                    
                    html += '/>'
                
                # Add field intelligence info
                if semantic_type != 'unknown' or is_calculated:
                    html += '<div class="field-info">'
                    html += f'<strong>AI Analysis:</strong> {semantic_type.replace("_", " ").title()}<br>'
                    html += f'<strong>Data Type:</strong> {data_type}<br>'
                    html += f'<strong>Confidence:</strong> {confidence:.0%}'
                    
                    if is_calculated and field_info.get('calculation_formula'):
                        html += f'<div class="calculation-info mt-2">'
                        html += f'<strong>Formula:</strong> <code>{field_info["calculation_formula"]}</code>'
                        html += '</div>'
                    
                    html += '</div>'
                
                html += '</div>'
            
            html += '<button type="submit" class="btn btn-primary">Submit</button>'
            html += '</form>'
            html += '</div>'
        
        html += '</div>'
        return html
    
    def show_identified_fields(self):
        """Display all AI-identified fields"""
        print("\n🧠 AI-IDENTIFIED FIELDS:")
        print("-" * 50)
        
        # Show AI-named fields
        ai_named = {k: v for k, v in self.ai_field_mappings.items() 
                   if v['ai_name'] != v['original']}
        
        if ai_named:
            print("\n✨ AI-NAMED FIELDS:")
            for key, mapping in list(ai_named.items())[:10]:
                print(f"  • {mapping['original']} → {mapping['ai_name']} ({mapping['semantic_type']})")
            if len(ai_named) > 10:
                print(f"  ... and {len(ai_named) - 10} more")
        
        # Show calculated fields
        calculated = {k: v for k, v in self.identified_fields.items() 
                     if v.get('is_calculated')}
        
        if calculated:
            print("\n📊 CALCULATED FIELDS:")
            for key, field in list(calculated.items())[:5]:
                print(f"  • {field['ai_generated_name']}")
                if field.get('calculation_formula'):
                    print(f"    Formula: {field['calculation_formula']}")
        
        # Group by data type
        by_data_type = {}
        for field_data in self.identified_fields.values():
            dtype = field_data.get('data_type', 'text')
            if dtype not in by_data_type:
                by_data_type[dtype] = 0
            by_data_type[dtype] += 1
        
        print("\n📈 BY DATA TYPE:")
        for dtype, count in sorted(by_data_type.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {dtype}: {count} fields")
        
        print(f"\nTotal fields identified: {self.stats['fields_identified']}")
        print(f"Fields with AI naming: {self.stats['fields_ai_named']}")
        print(f"Calculations mapped: {self.stats['calculations_mapped']}")
    
    def print_statistics(self):
        """Print session statistics"""
        print("\n" + "="*60)
        print("🧠 AI-POWERED SESSION STATISTICS")
        print("="*60)
        print(f"Pages Processed: {self.stats['pages_processed']}")
        print(f"Fields Identified: {self.stats['fields_identified']}")
        print(f"Fields AI-Named: {self.stats['fields_ai_named']}")
        print(f"Calculations Mapped: {self.stats['calculations_mapped']}")
        print(f"Duplicates Prevented: {self.stats['duplicates_prevented']}")
        
        # Show AI naming effectiveness
        if self.stats['fields_identified'] > 0:
            ai_naming_rate = (self.stats['fields_ai_named'] / self.stats['fields_identified']) * 100
            print(f"\nAI Naming Rate: {ai_naming_rate:.1f}%")
        
        # Show field type breakdown
        if self.identified_fields:
            field_types = {}
            for field_data in self.identified_fields.values():
                semantic_type = field_data['semantic_type']
                field_types[semantic_type] = field_types.get(semantic_type, 0) + 1
            
            print("\nField Types Identified:")
            for field_type, count in sorted(field_types.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  • {field_type}: {count}")
        
        print("="*60)
    
    async def store_in_supabase_with_dedup(self, url: str, page_data: Dict, 
                                          template_path: str, calculations: List[Dict],
                                          api_responses: List[Dict], fields: List[Dict]):
        """Store page in Supabase with AI field intelligence"""
        print("  💾 Storing in Supabase with AI field intelligence...")
        
        try:
            # Generate checksum for duplicate prevention
            checksum = self.duplicate_preventor.generate_page_checksum(
                url, page_data.get('html', '')
            )
            
            # Prepare page record
            page_record = {
                'company_id': self.company_id,
                'url': url,
                'title': page_data.get('title', ''),
                'html': page_data.get('html', ''),
                'main_content': page_data.get('main_content', ''),
                'text_content': page_data.get('text_content', ''),
                'content_checksum': checksum,
                'template_path': template_path,
                'forms': page_data.get('forms', []),
                'tables': page_data.get('tables', []),
                'scripts': page_data.get('scripts', []),
                'calculations': calculations,
                'api_responses': api_responses,
                'ai_field_mappings': [
                    {
                        'field_name': f['field_name'],
                        'ai_name': f.get('ai_generated_name'),
                        'semantic_type': f.get('semantic_type'),
                        'data_type': f.get('data_type'),
                        'confidence': f.get('confidence')
                    } for f in fields
                ],
                'field_count': len(fields),
                'ai_named_count': len([f for f in fields if f.get('ai_generated_name') != f['field_name']]),
                'calculation_count': len(calculations),
                'is_active': True
            }
            
            # Insert into database
            result = self.supabase.table('pages').insert(page_record).execute()
            
            if result.data:
                print(f"  ✅ Page stored in Supabase")
                print(f"     • {len(fields)} fields with AI intelligence")
                print(f"     • {len(calculations)} calculations mapped")
                print(f"     • {len(api_responses)} API responses captured")
            
        except Exception as e:
            print(f"  ❌ Error storing in Supabase: {e}")
            logger.error(f"Supabase storage error: {e}")
    
    async def capture_real_page(self, url: str) -> Dict:
        """Capture complete page data"""
        try:
            print("  📸 Capturing page data...")
            
            # Get page HTML
            html = await self.page.content()
            
            # Get title
            title = await self.page.title()
            
            # Extract text content
            text_content = await self.page.evaluate("""
                () => document.body ? document.body.innerText : ''
            """)
            
            # Extract main content
            main_content = await self.extract_exact_main_content({'html': html})
            
            # Extract forms
            forms = await self.page.evaluate("""
                () => {
                    const forms = [];
                    document.querySelectorAll('form').forEach(form => {
                        const fields = [];
                        form.querySelectorAll('input, select, textarea').forEach(field => {
                            fields.push({
                                name: field.name,
                                id: field.id,
                                type: field.type || field.tagName.toLowerCase(),
                                placeholder: field.placeholder,
                                required: field.required,
                                value: field.value,
                                options: field.tagName === 'SELECT' ? 
                                    Array.from(field.options).map(opt => ({
                                        value: opt.value,
                                        text: opt.text
                                    })) : []
                            });
                        });
                        forms.push({
                            id: form.id,
                            name: form.name,
                            action: form.action,
                            method: form.method,
                            fields: fields
                        });
                    });
                    return forms;
                }
            """)
            
            # Extract tables
            tables = await self.page.evaluate("""
                () => {
                    const tables = [];
                    document.querySelectorAll('table').forEach(table => {
                        const rows = [];
                        table.querySelectorAll('tr').forEach(tr => {
                            const cells = [];
                            tr.querySelectorAll('td, th').forEach(cell => {
                                cells.push(cell.innerText);
                            });
                            if (cells.length > 0) rows.push(cells);
                        });
                        tables.push({
                            id: table.id,
                            class: table.className,
                            rows: rows
                        });
                    });
                    return tables;
                }
            """)
            
            # Extract scripts
            scripts = await self.page.evaluate("""
                () => {
                    const scripts = [];
                    document.querySelectorAll('script').forEach(script => {
                        if (script.src) {
                            scripts.push({
                                type: 'external',
                                src: script.src
                            });
                        } else if (script.innerHTML) {
                            scripts.push({
                                type: 'inline',
                                content: script.innerHTML.substring(0, 5000)
                            });
                        }
                    });
                    return scripts;
                }
            """)
            
            return {
                'url': url,
                'title': title,
                'html': html,
                'main_content': main_content,
                'text_content': text_content,
                'forms': forms,
                'tables': tables,
                'scripts': scripts
            }
            
        except Exception as e:
            print(f"  ❌ Error capturing page: {e}")
            return None
    
    async def discover_links(self, page_data: Dict) -> List[str]:
        """Discover new links from the page"""
        try:
            links = await self.page.evaluate("""
                () => {
                    const links = new Set();
                    document.querySelectorAll('a[href]').forEach(a => {
                        const href = a.href;
                        if (href && !href.startsWith('javascript:') && 
                            !href.startsWith('#') && !href.startsWith('mailto:')) {
                            links.add(href);
                        }
                    });
                    return Array.from(links);
                }
            """)
            
            # Filter to only include target site links
            filtered_links = [
                link for link in links 
                if link.startswith(self.target_base)
            ]
            
            return filtered_links
            
        except Exception as e:
            print(f"  ⚠️ Error discovering links: {e}")
            return []
    
    # Include all the other helper methods from the original implementation
    async def run(self):
        """Main execution with AI-powered field intelligence"""
        print("\n🎯 STARTING AI-POWERED PAGE REPLICATION")
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
            await self.safe_navigate(start_url, action='goto')
            
            print("\n" + "="*60)
            print("🔑 MANUAL AUTHORIZATION REQUIRED")
            print("="*60)
            print("\n👉 Please do the following in the browser window:")
            print("   1. Log into the site if needed")
            print("   2. Navigate to any page you want to start with")
            print("   3. Make sure you can see the main content")
            print("\n⚠️  BROWSER WILL STAY OPEN - DO NOT CLOSE IT")
            print("\n✅ When ready, press ENTER in this terminal to continue...")
            
            input("\n>>> Press ENTER to start AI-powered replication: ")
            
            print("\n🚀 Starting replication with AI field intelligence...")
            
            await self.page.wait_for_timeout(500)
            
            current_url = self.page.url
            print(f"✅ Current page detected: {current_url}")
            
            if 'sign_in' not in current_url and 'login' not in current_url:
                print("🔄 Reloading page to ensure full content...")
                await self.safe_navigate(action='reload')
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
            
            # Generate Flask app with all captured pages
            if len(self.processed_pages) > 0:
                print("\n" + "="*60)
                print("🎯 FINALIZING FLASK APPLICATION")
                print("="*60)
                self.generate_flask_app()
                print("\n✅ COMPLETE! Your Flask app is ready to run:")
                print("   python app_generated.py")
                print("\n🌐 Then visit: http://localhost:8080")
                print("="*60)
    
    async def process_pages_loop(self):
        """Process pages with AI intelligence"""
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
            print(f"📊 AI-Named Fields: {self.stats['fields_ai_named']}")
            print(f"📊 Calculations Mapped: {self.stats['calculations_mapped']}")
            print(f"📊 Duplicates Prevented: {self.stats['duplicates_prevented']}")
            print(f"📊 Queue: {len(unprocessed)} pages remaining")
            print(f"📍 Next: {unprocessed[0]}")
            
            print("\nOptions:")
            print("  ENTER = Process next page")
            print("  'a' = AUTO mode (process every 60 seconds)")
            print("  'q' = Quit and close browser")
            print("  'l' = List all remaining pages")
            print("  's' = Skip this page")
            print("  'f' = Show AI-identified fields")
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
    
    # Include all other helper methods from original implementation
    async def extract_forms_data(self) -> List[Dict]:
        """Extract forms data from the page"""
        try:
            forms = await self.page.evaluate("""
                () => {
                    const forms = [];
                    document.querySelectorAll('form').forEach((form, formIndex) => {
                        const formData = {
                            id: form.id || `form_${formIndex}`,
                            name: form.name || '',
                            action: form.action || '',
                            method: form.method || 'GET',
                            fields: []
                        };
                        
                        form.querySelectorAll('input, select, textarea').forEach(field => {
                            const fieldData = {
                                name: field.name || field.id || '',
                                type: field.type || field.tagName.toLowerCase(),
                                id: field.id || '',
                                placeholder: field.placeholder || '',
                                required: field.required || false,
                                value: field.value || '',
                                options: []
                            };
                            
                            if (field.tagName === 'SELECT') {
                                field.querySelectorAll('option').forEach(option => {
                                    fieldData.options.push({
                                        value: option.value,
                                        text: option.textContent
                                    });
                                });
                            }
                            
                            formData.fields.push(fieldData);
                        });
                        
                        forms.push(formData);
                    });
                    return forms;
                }
            """)
            return forms
        except Exception as e:
            print(f"  ⚠️ Error extracting forms: {e}")
            return []
    
    async def extract_tables_data(self) -> List[Dict]:
        """Extract tables data from the page"""
        try:
            tables = await self.page.evaluate("""
                () => {
                    const tables = [];
                    document.querySelectorAll('table').forEach((table, tableIndex) => {
                        const tableData = {
                            id: table.id || `table_${tableIndex}`,
                            headers: [],
                            rows: []
                        };
                        
                        // Extract headers
                        table.querySelectorAll('thead th, thead td').forEach(header => {
                            tableData.headers.push(header.textContent.trim());
                        });
                        
                        // If no thead, check first row for headers
                        if (tableData.headers.length === 0) {
                            const firstRow = table.querySelector('tr');
                            if (firstRow) {
                                firstRow.querySelectorAll('th').forEach(header => {
                                    tableData.headers.push(header.textContent.trim());
                                });
                            }
                        }
                        
                        // Extract rows
                        table.querySelectorAll('tbody tr, tr').forEach(row => {
                            const rowData = [];
                            row.querySelectorAll('td').forEach(cell => {
                                rowData.push(cell.textContent.trim());
                            });
                            if (rowData.length > 0) {
                                tableData.rows.push(rowData);
                            }
                        });
                        
                        tables.push(tableData);
                    });
                    return tables;
                }
            """)
            return tables
        except Exception as e:
            print(f"  ⚠️ Error extracting tables: {e}")
            return []
    
    async def extract_scripts(self) -> List[Dict]:
        """Extract scripts from the page"""
        try:
            scripts = await self.page.evaluate("""
                () => {
                    const scripts = [];
                    document.querySelectorAll('script').forEach(script => {
                        if (script.src) {
                            scripts.push({
                                type: 'external',
                                src: script.src
                            });
                        } else if (script.textContent) {
                            scripts.push({
                                type: 'inline',
                                content: script.textContent
                            });
                        }
                    });
                    return scripts;
                }
            """)
            return scripts
        except Exception as e:
            print(f"  ⚠️ Error extracting scripts: {e}")
            return []
    
    async def discover_links(self, page_data: Dict) -> List[str]:
        """Discover new links from the page"""
        try:
            links = await self.page.evaluate(f"""
                () => {{
                    const links = new Set();
                    document.querySelectorAll('a[href]').forEach(link => {{
                        const href = link.href;
                        if (href && href.startsWith('{self.target_base}')) {{
                            links.add(href);
                        }}
                    }});
                    return Array.from(links);
                }}
            """)
            
            # Filter out unwanted links
            filtered_links = [
                link for link in links 
                if 'logout' not in link.lower() 
                and 'sign_out' not in link.lower()
                and 'login' not in link.lower()
                and '#' not in link
            ]
            
            return filtered_links
        except Exception as e:
            print(f"  ⚠️ Error discovering links: {e}")
            return []
    
    async def store_in_supabase_with_dedup(self, url: str, page_data: Dict, template_path: str, 
                                          calculations: List[Dict], api_responses: List[Dict], 
                                          fields: List[Dict]):
        """Store page data in Supabase with deduplication"""
        try:
            print("  🐘 Storing in Supabase...")
            
            # Generate checksum
            checksum = self.duplicate_preventor.generate_page_checksum(
                url, page_data.get('html', '')
            )
            
            # Prepare page record
            page_record = {
                'company_id': self.company_id,
                'url': url,
                'title': page_data.get('title', ''),
                'html_content': page_data['html'][:65000] if len(page_data['html']) > 65000 else page_data['html'],
                'main_content': page_data.get('main_content', '')[:65000] if page_data.get('main_content') and len(page_data.get('main_content', '')) > 65000 else page_data.get('main_content', ''),
                'template_path': template_path,
                'content_checksum': checksum,
                'forms': page_data.get('forms', []),
                'tables': page_data.get('tables', []),
                'calculations': calculations,
                'api_responses': api_responses,
                'field_mappings': fields,
                'field_statistics': {
                    'total_fields': len(fields),
                    'ai_named_fields': len([f for f in fields if f.get('ai_generated_name') != f['field_name']]),
                    'calculated_fields': len([f for f in fields if f.get('is_calculated')]),
                    'data_types': {}
                },
                'is_form_page': len(page_data.get('forms', [])) > 0,
                'is_report_page': 'report' in url.lower() or len(page_data.get('tables', [])) > 0,
                'captured_at': page_data.get('captured_at'),
                'replicated_at': datetime.now().isoformat()
            }
            
            # Calculate data type statistics
            for field in fields:
                dtype = field.get('data_type', 'text')
                if dtype not in page_record['field_statistics']['data_types']:
                    page_record['field_statistics']['data_types'][dtype] = 0
                page_record['field_statistics']['data_types'][dtype] += 1
            
            # Insert into pages table
            result = self.supabase.table('pages').insert(page_record).execute()
            
            if result.data:
                print(f"  ✅ Stored in Supabase with {len(fields)} AI-analyzed fields")
                if page_record['field_statistics']['ai_named_fields'] > 0:
                    print(f"    ✨ {page_record['field_statistics']['ai_named_fields']} fields with AI naming")
                if page_record['field_statistics']['calculated_fields'] > 0:
                    print(f"    📊 {page_record['field_statistics']['calculated_fields']} calculated fields")
            
        except Exception as e:
            if 'duplicate key' in str(e).lower():
                print(f"  ⚠️ Page already exists in database (duplicate prevented)")
                self.stats['duplicates_prevented'] += 1
            else:
                print(f"  ❌ Error storing in Supabase: {e}")
                logger.error(f"Supabase storage error: {e}")
    
    async def capture_real_page(self, url: str) -> Optional[Dict]:
        """Enhanced capture to get exact target structure"""
        try:
            print("  📸 Capturing exact page structure...")
            
            title = await self.page.title()
            
            # Get the full HTML first
            html_content = await self.page.content()
            
            # Get the main content with inline styles preserved
            main_with_styles = await self.page.evaluate("""
                () => {
                    // Function to get computed styles for an element
                    function getImportantStyles(element) {
                        const computed = window.getComputedStyle(element);
                        const important = {
                            'display': computed.display,
                            'position': computed.position,
                            'width': computed.width,
                            'height': computed.height,
                            'margin': computed.margin,
                            'padding': computed.padding,
                            'border': computed.border,
                            'background': computed.background,
                            'color': computed.color,
                            'font-size': computed.fontSize,
                            'font-weight': computed.fontWeight,
                            'text-align': computed.textAlign,
                            'vertical-align': computed.verticalAlign,
                            'float': computed.float,
                            'clear': computed.clear,
                            'overflow': computed.overflow
                        };
                        
                        // Filter out default values
                        const filtered = {};
                        for (const [key, value] of Object.entries(important)) {
                            if (value && value !== 'none' && value !== 'auto' && value !== '0px') {
                                filtered[key] = value;
                            }
                        }
                        
                        return filtered;
                    }
                    
                    // Find main content
                    let mainElement = document.querySelector('main, [role="main"], #content, .content');
                    if (!mainElement) mainElement = document.body;
                    
                    // Clone and process
                    const clone = mainElement.cloneNode(true);
                    
                    // Add inline styles for critical layout elements
                    clone.querySelectorAll('table, form, .row, .col, .container').forEach(el => {
                        const styles = getImportantStyles(el);
                        const styleString = Object.entries(styles)
                            .map(([key, value]) => `${key}: ${value}`)
                            .join('; ');
                        
                        if (styleString) {
                            el.setAttribute('data-original-style', styleString);
                        }
                    });
                    
                    return clone.outerHTML;
                }
            """)
            
            # Extract text content for AI analysis
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
            
            # Extract forms with full details
            forms_data = await self.extract_forms_data()
            
            # Extract tables with full structure
            tables_data = await self.extract_tables_data()
            
            # Extract essential scripts only
            scripts = await self.extract_scripts()
            filtered_scripts = [s for s in scripts if s['type'] == 'inline' and 'calculate' in s.get('content', '').lower()]
            
            page_data = {
                'url': url,
                'title': title,
                'html': html_content,
                'main_content': main_with_styles,
                'text_content': text_content,
                'scripts': filtered_scripts,
                'forms': forms_data,
                'tables': tables_data,
                'captured_at': datetime.now().isoformat()
            }
            
            print(f"  ✅ Captured exact structure: {len(main_with_styles)} bytes")
            return page_data
            
        except Exception as e:
            print(f"  ❌ Error capturing page: {e}")
            return None
    
    async def extract_styles(self) -> List[Dict]:
        """Extract all CSS stylesheets and inline styles"""
        try:
            styles = await self.page.evaluate("""
                () => {
                    const styles = [];
                    
                    // Get all <link> stylesheets
                    document.querySelectorAll('link[rel="stylesheet"]').forEach(link => {
                        styles.push({
                            type: 'link',
                            href: link.href,
                            media: link.media || 'all'
                        });
                    });
                    
                    // Get all <style> tags
                    document.querySelectorAll('style').forEach(style => {
                        styles.push({
                            type: 'inline',
                            content: style.textContent,
                            media: style.media || 'all'
                        });
                    });
                    
                    // Get computed styles for critical elements
                    const criticalSelectors = ['body', 'main', '.container', '#content'];
                    const computedStyles = {};
                    criticalSelectors.forEach(selector => {
                        const elem = document.querySelector(selector);
                        if (elem) {
                            computedStyles[selector] = window.getComputedStyle(elem).cssText;
                        }
                    });
                    
                    styles.push({
                        type: 'computed',
                        content: computedStyles
                    });
                    
                    return styles;
                }
            """)
            
            # Download external stylesheets
            for style in styles:
                if style['type'] == 'link' and style.get('href'):
                    try:
                        response = await self.page.evaluate(f"""
                            async () => {{
                                const response = await fetch('{style['href']}');
                                return await response.text();
                            }}
                        """)
                        style['content'] = response
                    except:
                        print(f"    ⚠️ Could not fetch stylesheet: {style.get('href')}")
            
            return styles
        except Exception as e:
            print(f"  ⚠️ Error extracting styles: {e}")
            return []
    
    async def extract_scripts(self) -> List[Dict]:
        """Extract all JavaScript files and inline scripts"""
        try:
            scripts = await self.page.evaluate("""
                () => {
                    const scripts = [];
                    
                    // Get all script tags
                    document.querySelectorAll('script').forEach(script => {
                        if (script.src) {
                            scripts.push({
                                type: 'external',
                                src: script.src,
                                async: script.async,
                                defer: script.defer
                            });
                        } else if (script.textContent) {
                            scripts.push({
                                type: 'inline',
                                content: script.textContent
                            });
                        }
                    });
                    
                    return scripts;
                }
            """)
            return scripts
        except Exception as e:
            print(f"  ⚠️ Error extracting scripts: {e}")
            return []
    
    async def extract_assets(self) -> List[Dict]:
        """Extract images, fonts, and other assets"""
        try:
            assets = await self.page.evaluate("""
                () => {
                    const assets = [];
                    
                    // Get all images
                    document.querySelectorAll('img').forEach(img => {
                        if (img.src) {
                            assets.push({
                                type: 'image',
                                src: img.src,
                                alt: img.alt,
                                width: img.width,
                                height: img.height
                            });
                        }
                    });
                    
                    // Get background images from computed styles
                    const elements = document.querySelectorAll('*');
                    elements.forEach(el => {
                        const bg = window.getComputedStyle(el).backgroundImage;
                        if (bg && bg !== 'none') {
                            const urls = bg.match(/url\(["']?([^"')]+)["']?\)/g);
                            if (urls) {
                                urls.forEach(url => {
                                    const cleanUrl = url.replace(/url\(["']?|["']?\)/g, '');
                                    assets.push({
                                        type: 'background',
                                        src: cleanUrl
                                    });
                                });
                            }
                        }
                    });
                    
                    // Get fonts
                    if (document.fonts) {
                        document.fonts.forEach(font => {
                            assets.push({
                                type: 'font',
                                family: font.family,
                                source: font.source
                            });
                        });
                    }
                    
                    return assets;
                }
            """)
            
            # Download and store assets
            for asset in assets:
                if asset.get('src'):
                    asset['local_path'] = await self.download_asset(asset['src'])
            
            return assets
        except Exception as e:
            print(f"  ⚠️ Error extracting assets: {e}")
            return []
    
    async def download_asset(self, url: str) -> str:
        """Download and save an asset locally"""
        try:
            parsed = urlparse(url)
            
            # Create assets directory structure
            asset_path = self.static_dir / parsed.netloc / parsed.path.lstrip('/')
            asset_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download the asset
            response = await self.page.evaluate(f"""
                async () => {{
                    const response = await fetch('{url}');
                    const blob = await response.blob();
                    const arrayBuffer = await blob.arrayBuffer();
                    const uint8Array = new Uint8Array(arrayBuffer);
                    return Array.from(uint8Array);
                }}
            """)
            
            # Save to file
            with open(asset_path, 'wb') as f:
                f.write(bytes(response))
            
            return str(asset_path.relative_to(self.project_root))
            
        except Exception as e:
            print(f"    ⚠️ Could not download asset {url}: {e}")
            return url
    
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
                                readonly: input.readOnly,
                                disabled: input.disabled,
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
            
            # If Gemini is available, analyze JavaScript directly
            if self.gemini_model:
                # Get all JavaScript from the page
                all_scripts = await self.page.evaluate("""
                    () => {
                        const scripts = [];
                        document.querySelectorAll('script').forEach(script => {
                            if (script.textContent) {
                                scripts.push(script.textContent);
                            }
                        });
                        return scripts.join('\\n');
                    }
                """)
                
                prompt = f"""
                Analyze this JavaScript code and identify ALL calculations and formulas.
                Look for mathematical operations, aggregations, and financial calculations.
                
                JavaScript Code:
                {all_scripts[:10000]}
                
                Page Context: {page_data.get('title', '')}
                
                Find:
                1. Variable assignments with math operations
                2. Function calculations
                3. DOM updates with calculated values
                4. Financial formulas (rent, fees, totals)
                
                Return as JSON array with: name, description, formula, variables, sample_data
                """
                
                try:
                    response = self.gemini_model.generate_content(prompt)
                    content = response.text
                    print("    ✨ Using Gemini to analyze JavaScript calculations")
                except Exception as e:
                    print(f"    ❌ GEMINI FAILED: {e}")
                    print("    🛑 STOPPING - Gemini is required for calculation extraction")
                    raise Exception("Gemini failed - cannot continue")
            else:
                # Fallback to original text analysis
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
                
                try:
                    response = self.anthropic_client.messages.create(
                        model="claude-opus-4-1-20250805",
                        max_tokens=2000,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    content = response.content[0].text
                except Exception as e:
                    print(f"    ❌ CLAUDE OPUS FAILED: {e}")
                    print("    🛑 STOPPING - Claude is required for calculation extraction")
                    raise Exception("Claude failed - cannot continue")
            
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
            
            api_responses = []
            
            # Set up response interceptor
            async def handle_response(response):
                try:
                    if 'api' in response.url or 'json' in response.headers.get('content-type', '').lower():
                        # Try to get JSON data
                        try:
                            data = await response.json()
                            
                            # Use Gemini to analyze if available
                            if self.gemini_model:
                                prompt = f"""
                                Analyze this API response for calculations and formulas:
                                
                                URL: {response.url}
                                Data (first 5000 chars): {json.dumps(data)[:5000]}
                                
                                Identify:
                                1. Calculation fields
                                2. Formulas used
                                3. Data relationships
                                
                                Return as JSON with: fields, calculations, relationships
                                """
                                
                                try:
                                    analysis = self.gemini_model.generate_content(prompt)
                                    import re
                                    json_match = re.search(r'\{.*\}', analysis.text, re.DOTALL)
                                    if json_match:
                                        analysis_data = json.loads(json_match.group())
                                    else:
                                        analysis_data = {}
                                except Exception as e:
                                    print(f"    ❌ GEMINI FAILED during API analysis: {e}")
                                    print("    🛑 STOPPING - Gemini is required for API analysis")
                                    analysis_data = {}
                                
                                api_responses.append({
                                    'url': response.url,
                                    'data': data,
                                    'analysis': analysis_data
                                })
                                print(f"    ✨ Analyzed API response with Gemini: {response.url}")
                            else:
                                api_responses.append({
                                    'url': response.url,
                                    'data': data
                                })
                        except:
                            pass
                except:
                    pass
            
            # Add listener
            self.page.on('response', handle_response)
            
            # Navigate and wait for API calls
            if self.page.url != url:
                await self.page.goto(url)
            await self.page.wait_for_timeout(3000)
            
            # Remove listener
            self.page.remove_listener('response', handle_response)
            
            # Fallback to performance API if no responses captured
            if not api_responses:
                responses = await self.page.evaluate("""
                    () => {
                        if (window.performance && window.performance.getEntriesByType) {
                            const resources = window.performance.getEntriesByType('resource');
                            return resources
                                .filter(r => r.initiatorType === 'xmlhttprequest' || r.initiatorType === 'fetch')
                                .map(r => ({
                                    url: r.name,
                                    duration: r.duration,
                                    size: r.transferSize
                                }));
                        }
                        return [];
                    }
                """)
                api_responses = responses
            
            print(f"  ✅ Found {len(api_responses)} API responses")
            return api_responses
            
        except Exception as e:
            print(f"  ⚠️ Error extracting API responses: {e}")
            return []
    
    async def discover_links(self, page_data: Dict) -> List[str]:
        """Discover new links from the page"""
        try:
            soup = BeautifulSoup(page_data['html'], 'html.parser')
            links = []
            
            for a in soup.find_all('a', href=True):
                href = a['href']
                absolute_url = urljoin(page_data['url'], href)
                
                if absolute_url.startswith(self.target_base):
                    if absolute_url not in self.processed_pages and absolute_url not in self.discovered_links:
                        links.append(absolute_url)
            
            return links
            
        except Exception as e:
            print(f"  ⚠️ Error discovering links: {e}")
            return []
    
    async def store_in_supabase_with_dedup(self, url: str, page_data: Dict, template_path: str, 
                                          calculations: List[Dict], api_responses: List[Dict],
                                          fields: List[Dict]):
        """Store page in Supabase with duplicate prevention"""
        try:
            print("  💾 Storing in Supabase with AI field intelligence...")
            
            # Generate content checksum
            checksum = self.duplicate_preventor.generate_page_checksum(url, page_data['html'])
            
            page_record = {
                'company_id': self.company_id,
                'url': url,
                'title': page_data.get('title', ''),
                'html_content': page_data['html'][:65000] if len(page_data['html']) > 65000 else page_data['html'],
                'main_content': page_data.get('main_content', '')[:65000] if page_data.get('main_content') and len(page_data.get('main_content', '')) > 65000 else page_data.get('main_content', ''),
                'template_path': template_path,
                'content_checksum': checksum,
                'forms': page_data.get('forms', []),
                'tables': page_data.get('tables', []),
                'calculations': calculations,
                'api_responses': api_responses,
                'field_mappings': fields,
                'field_statistics': {
                    'total_fields': len(fields),
                    'ai_named_fields': len([f for f in fields if f.get('ai_generated_name') != f['field_name']]),
                    'calculated_fields': len([f for f in fields if f.get('is_calculated')]),
                    'data_types': {}
                },
                'is_form_page': len(page_data.get('forms', [])) > 0,
                'is_report_page': 'report' in url.lower() or len(page_data.get('tables', [])) > 0,
                'captured_at': page_data.get('captured_at'),
                'replicated_at': datetime.now().isoformat()
            }
            
            # Calculate data type statistics
            for field in fields:
                dtype = field.get('data_type', 'text')
                if dtype not in page_record['field_statistics']['data_types']:
                    page_record['field_statistics']['data_types'][dtype] = 0
                page_record['field_statistics']['data_types'][dtype] += 1
            
            # Insert into pages table
            result = self.supabase.table('pages').insert(page_record).execute()
            
            if result.data:
                print(f"  ✅ Stored in Supabase with {len(fields)} AI-analyzed fields")
                if page_record['field_statistics']['ai_named_fields'] > 0:
                    print(f"    ✨ {page_record['field_statistics']['ai_named_fields']} fields with AI naming")
                if page_record['field_statistics']['calculated_fields'] > 0:
                    print(f"    📊 {page_record['field_statistics']['calculated_fields']} calculated fields")
            
        except Exception as e:
            if 'duplicate key' in str(e).lower():
                print(f"  ⚠️ Page already exists in database (duplicate prevented)")
                self.stats['duplicates_prevented'] += 1
            else:
                print(f"  ❌ Error storing in Supabase: {e}")
                logger.error(f"Supabase storage error: {e}")
    
    def print_statistics(self):
        """Print session statistics"""
        print("\n" + "="*60)
        print("🧠 AI-POWERED SESSION STATISTICS")
        print("="*60)
        print(f"Pages Processed: {self.stats['pages_processed']}")
        print(f"Fields Identified: {self.stats['fields_identified']}")
        print(f"Fields AI-Named: {self.stats['fields_ai_named']}")
        print(f"Calculations Mapped: {self.stats['calculations_mapped']}")
        print(f"Duplicates Prevented: {self.stats['duplicates_prevented']}")
        
        # Show AI naming effectiveness
        if self.stats['fields_identified'] > 0:
            ai_naming_rate = (self.stats['fields_ai_named'] / self.stats['fields_identified']) * 100
            print(f"\nAI Naming Rate: {ai_naming_rate:.1f}%")
        
        # Show costs
        print(f"\n💰 API COSTS:")
        print(f"  Claude: ${self.stats['claude_cost']:.2f}")
        print(f"  Gemini: ${self.stats['gemini_cost']:.2f}")
        print(f"  TOTAL: ${self.stats['total_cost']:.2f}")
        if self.stats['pages_processed'] > 0:
            print(f"  Per Page: ${self.stats['total_cost']/self.stats['pages_processed']:.2f}")
        
        print("="*60)


def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("🚀 AIVIIZN REAL AGENT - AI-POWERED FIELD INTELLIGENCE")
    print("="*60)
    print("\nThis agent will:")
    print("  ✓ Replicate pages from target sites")
    print("  ✓ Use AI to intelligently name fields")
    print("  ✓ Identify field types and data types")
    print("  ✓ Map calculation variables to fields")
    print("  ✓ Prevent duplicate pages and fields")
    print("  ✓ Store everything in Supabase")
    print("\n⚠️  IMPORTANT: Browser will open for manual login")
    print("="*60)
    
    try:
        agent = AIVIIZNRealAgent()
        asyncio.run(agent.run())
    except KeyboardInterrupt:
        print("\n⚠️ Stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.error(f"Main error: {traceback.format_exc()}")

if __name__ == "__main__":
    main()
