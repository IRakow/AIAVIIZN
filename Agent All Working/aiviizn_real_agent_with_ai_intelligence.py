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

# Import the enhanced field intelligence
from enhanced_field_intelligence import (
    EnhancedFieldMapper,
    CalculationVariableMapper,
    FieldIntelligence
)

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
        
        # Check placeholders and labels
        placeholder = field_attributes.get('placeholder', '').lower()
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
        print("✓ Claude API ready (Opus 4.1)")
        
        # Initialize OpenAI client
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if openai_api_key:
            self.openai_client = AsyncOpenAI(api_key=openai_api_key)
            print(f"✓ GPT-4o (Omni) connected")
        else:
            print("⚠️ OpenAI API key not found")
            self.openai_client = None
        
        # Initialize BOTH field mappers
        # Basic pattern-based mapper for fallback
        self.field_mapper = FieldMapper()
        print("✓ Basic field mapping ready (fallback)")
        
        # AI-powered enhanced mapper for intelligent analysis
        self.enhanced_field_mapper = EnhancedFieldMapper(
            self.anthropic_client,
            self.openai_client
        )
        print("✓ AI-powered field intelligence ready")
        
        # Calculation variable mapper
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
        
        # Target site settings
        self.target_base = "https://celticprop.appfolio.com"
        
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
            'pages_processed': 0
        }
        
        print("✓ Ready to create beautiful pages with AI field intelligence")
    
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
                
                try:
                    # Try AI-powered analysis first
                    print(f"    🔍 Analyzing field: {field_name}")
                    
                    field_intelligence = await self.enhanced_field_mapper.analyze_field_intelligently(
                        field_name,
                        field,
                        page_data.get('text_content', ''),
                        surrounding_fields
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
                            print(f"    ✓ Identified: {field_intelligence.ai_generated_name} → {field_intelligence.semantic_type} ({field_intelligence.confidence:.1%})")
                    
                    # Store AI mapping
                    self.ai_field_mappings[field_key] = {
                        'original': field_name,
                        'ai_name': field_intelligence.ai_generated_name,
                        'semantic_type': field_intelligence.semantic_type,
                        'data_type': field_intelligence.data_type,
                        'is_calculated': field_intelligence.is_calculated
                    }
                    
                except Exception as e:
                    print(f"    ⚠️ AI analysis failed for {field_name}: {e}")
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
    
    async def extract_calculations_with_mapping(self, page_data: Dict, fields: List[Dict]) -> List[Dict]:
        """Extract calculations and map their variables to fields"""
        try:
            print("  🧮 Extracting calculations with variable mapping...")
            
            # First extract calculations using Claude
            calculations = await self.extract_calculations_real(page_data)
            
            # Now map variables for each calculation
            enhanced_calculations = []
            for calc in calculations:
                formula = calc.get('formula', '')
                if formula:
                    # Map variables to fields
                    variable_mappings = await self.calculation_mapper.map_calculation_variables(
                        formula,
                        fields,
                        page_data.get('text_content', '')
                    )
                    
                    calc['variable_mappings'] = variable_mappings
                    calc['formula_type'] = self.calculation_mapper.identify_formula_type(
                        formula,
                        [v['variable_name'] for v in variable_mappings]
                    )
                    
                    if variable_mappings:
                        self.stats['calculations_mapped'] += 1
                        print(f"    ✓ Mapped calculation: {calc.get('name')} with {len(variable_mappings)} variables")
                
                enhanced_calculations.append(calc)
            
            return enhanced_calculations
            
        except Exception as e:
            print(f"  ⚠️ Error in calculation mapping: {e}")
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
            
        except Exception as e:
            print(f"❌ Error replicating {url}: {e}")
            logger.error(f"Replication error for {url}: {traceback.format_exc()}")
            self.processed_pages.add(url)
            self.save_state()
    
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
        """Rewrite internal links to point to saved templates"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Rewrite all internal links
        for tag in soup.find_all(['a', 'form']):
            attr = 'href' if tag.name == 'a' else 'action'
            url = tag.get(attr)
            
            if url:
                # Convert to absolute URL
                absolute_url = urljoin(current_url, url)
                
                # If it's an internal link, rewrite it
                if absolute_url.startswith(self.target_base):
                    # Generate template filename from URL
                    parsed = urlparse(absolute_url)
                    path_parts = parsed.path.strip('/').split('/')
                    template_name = '_'.join(path_parts) if path_parts[0] else 'index'
                    template_name = f"{template_name}.html"
                    
                    # Update the link
                    tag[attr] = f"/templates/{template_name}"
        
        # Rewrite asset links
        for tag in soup.find_all(['img', 'script', 'link']):
            if tag.name == 'img':
                attr = 'src'
            elif tag.name == 'script':
                attr = 'src'
            else:  # link
                attr = 'href'
            
            url = tag.get(attr)
            if url and not url.startswith(('data:', 'blob:', '#')):
                absolute_url = urljoin(current_url, url)
                
                # If it's from the target site, use local version
                if absolute_url.startswith(self.target_base):
                    parsed = urlparse(absolute_url)
                    local_path = f"/static/{parsed.netloc}{parsed.path}"
                    tag[attr] = local_path
        
        return str(soup)
    
    async def generate_beautiful_template_with_ai(self, page_data: Dict, calculations: List[Dict], fields: List[Dict]) -> str:
        """Generate exact replica template with preserved styles and functionality"""
        try:
            print("  🎨 Generating exact replica with AI field intelligence...")
            
            # Create base template
            self.create_base_template()
            
            # Get the original HTML
            html_content = page_data.get('html', '')
            
            # Rewrite internal links
            html_content = self.rewrite_links(html_content, page_data['url'])
            
            # If we have fields, enhance them with AI intelligence
            if fields:
                html_content = self.enhance_fields_in_html(html_content, fields)
            
            # Preserve all styles
            style_tags = ''
            for style in page_data.get('styles', []):
                if style['type'] == 'link':
                    # Use local copy if downloaded, otherwise original
                    href = style.get('local_path', style['href'])
                    style_tags += f'<link rel="stylesheet" href="{href}" media="{style.get("media", "all")}">
'
                elif style['type'] == 'inline' and style.get('content'):
                    style_tags += f'<style media="{style.get("media", "all")}">{style["content"]}</style>
'
            
            # Preserve all scripts
            script_tags = ''
            for script in page_data.get('scripts', []):
                if script['type'] == 'external':
                    src = script.get('local_path', script['src'])
                    async_attr = 'async' if script.get('async') else ''
                    defer_attr = 'defer' if script.get('defer') else ''
                    script_tags += f'<script src="{src}" {async_attr} {defer_attr}></script>
'
                elif script['type'] == 'inline' and script.get('content'):
                    # Skip analytics and tracking scripts
                    if not any(tracker in script['content'] for tracker in ['google-analytics', 'gtag', 'analytics', 'tracking']):
                        script_tags += f'<script>{script["content"]}</script>
'
            
            # Parse the HTML to inject our enhancements
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Inject styles into head
            head = soup.find('head')
            if head and style_tags:
                # Preserve existing styles and add ours
                head.append(BeautifulSoup(style_tags, 'html.parser'))
            
            # Add field intelligence data
            if fields:
                field_data_script = f'''
<script type="module">
    // AI field mappings
    window.aiFieldMappings = {json.dumps([{{
        'original': f['field_name'],
        'ai_name': f.get('ai_generated_name', f['field_name']),
        'semantic_type': f['semantic_type'],
        'data_type': f.get('data_type', 'text'),
        'is_calculated': f.get('is_calculated', False),
        'confidence': f.get('confidence', 0)
    }} for f in fields])};
    console.log('🤖 AI Field Intelligence loaded:', window.aiFieldMappings.length, 'fields');
</script>'''
                body = soup.find('body')
                if body:
                    body.append(BeautifulSoup(field_data_script, 'html.parser'))
            
            # Inject scripts at end of body
            if script_tags:
                body = soup.find('body')
                if body:
                    body.append(BeautifulSoup(script_tags, 'html.parser'))
            
            return str(soup)
            
        except Exception as e:
            print(f"  ⚠️ Error generating template: {e}")
            return page_data.get('html', '')
    
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
        """Save template to file with proper URL structure"""
        try:
            parsed = urlparse(url)
            path_parts = parsed.path.strip('/').split('/')
            
            # Create directory structure matching URL
            if len(path_parts) > 1:
                # Create subdirectories
                template_dir = self.templates_dir / '/'.join(path_parts[:-1])
                template_dir.mkdir(parents=True, exist_ok=True)
                filename = f"{path_parts[-1]}.html" if path_parts[-1] else 'index.html'
                template_path = template_dir / filename
            else:
                # Root level
                filename = f"{path_parts[0]}.html" if path_parts[0] else 'index.html'
                template_path = self.templates_dir / filename
            
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(html)
            
            print(f"  💾 Saved template: {template_path}")
            return str(template_path)
            
        except Exception as e:
            print(f"  ⚠️ Error saving template: {e}")
            return ""
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_data['title']} - AIVIIZN AI</title>
    
    <!-- Bootstrap 5 -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Custom styles with AI field highlighting -->
    <style>
        :root {{
            --primary-color: #2c3e50;
            --secondary-color: #3498db;
            --success-color: #27ae60;
            --ai-color: #9b59b6;
            --calculated-color: #e74c3c;
        }}
        
        body {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
        }}
        
        .main-container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .page-header {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}
        
        .ai-field {{
            position: relative;
            border: 2px solid var(--ai-color);
            background: linear-gradient(45deg, rgba(155, 89, 182, 0.05), rgba(155, 89, 182, 0.1));
            transition: all 0.3s;
        }}
        
        .ai-field:hover {{
            box-shadow: 0 0 20px rgba(155, 89, 182, 0.4);
            transform: translateY(-2px);
        }}
        
        .calculated-field {{
            border: 2px solid var(--calculated-color);
            background: linear-gradient(45deg, rgba(231, 76, 60, 0.05), rgba(231, 76, 60, 0.1));
        }}
        
        .field-badge {{
            position: absolute;
            top: -10px;
            right: -10px;
            background: var(--ai-color);
            color: white;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
            z-index: 10;
            animation: pulse 2s infinite;
        }}
        
        .calculated-badge {{
            background: var(--calculated-color);
        }}
        
        @keyframes pulse {{
            0% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
            100% {{ transform: scale(1); }}
        }}
        
        .field-info {{
            background: linear-gradient(135deg, #667eea22, #764ba222);
            border-left: 4px solid var(--ai-color);
            padding: 12px;
            margin-top: 8px;
            border-radius: 6px;
            font-size: 13px;
        }}
        
        .ai-name {{
            color: var(--ai-color);
            font-weight: 600;
        }}
        
        .original-name {{
            color: #7f8c8d;
            font-size: 11px;
            font-style: italic;
        }}
        
        .data-type {{
            display: inline-block;
            background: var(--secondary-color);
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            margin-left: 8px;
        }}
        
        .calculation-info {{
            background: rgba(231, 76, 60, 0.1);
            border: 1px solid var(--calculated-color);
            padding: 10px;
            border-radius: 6px;
            margin-top: 10px;
        }}
        
        .formula {{
            font-family: 'Courier New', monospace;
            background: #2c3e50;
            color: #ecf0f1;
            padding: 8px;
            border-radius: 4px;
            margin-top: 5px;
        }}
        
        .ai-stats {{
            display: flex;
            gap: 20px;
            margin-top: 20px;
        }}
        
        .stat-card {{
            flex: 1;
            background: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        }}
        
        .stat-number {{
            font-size: 28px;
            font-weight: bold;
            color: var(--ai-color);
        }}
        
        .stat-label {{
            font-size: 12px;
            color: #7f8c8d;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
    </style>
</head>
<body>
    <div class="main-container">
        <div class="page-header">
            <h1>{page_data['title']}</h1>
            <p class="text-muted">Powered by AI Field Intelligence</p>
            
            <!-- AI Statistics -->
            <div class="ai-stats">
                <div class="stat-card">
                    <div class="stat-number">{len(fields)}</div>
                    <div class="stat-label">Fields Analyzed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len([f for f in fields if f.get('ai_generated_name') != f.get('field_name')])}</div>
                    <div class="stat-label">AI Named</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len([f for f in fields if f.get('is_calculated')])}</div>
                    <div class="stat-label">Calculated Fields</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(calculations)}</div>
                    <div class="stat-label">Formulas Mapped</div>
                </div>
            </div>
        </div>
        
        <!-- Field Intelligence Summary -->
        <div class="field-intelligence-summary mb-4">
            <h3>AI Field Intelligence Report</h3>
            <div class="row">
                {self.render_ai_field_summary(fields)}
            </div>
        </div>
        
        <!-- Calculations Summary -->
        {self.render_calculations_summary(calculations)}
        
        <!-- Forms with AI Intelligence -->
        {self.render_forms_with_ai_intelligence(page_data.get('forms', []), fields)}
    </div>
    
    <script type="module">
        // AI field mappings
        const aiFieldMappings = {json.dumps([{{
            'original': f['field_name'],
            'ai_name': f.get('ai_generated_name', f['field_name']),
            'semantic_type': f['semantic_type'],
            'data_type': f.get('data_type', 'text'),
            'is_calculated': f.get('is_calculated', False),
            'formula': f.get('calculation_formula', ''),
            'confidence': f.get('confidence', 0)
        }} for f in fields])};
        
        console.log('🧠 AI Field Mappings loaded:', aiFieldMappings.length);
        
        // Enhance fields with AI information
        aiFieldMappings.forEach(mapping => {{
            const element = document.querySelector(`[name="${{mapping.original}}"]`);
            if (element) {{
                element.classList.add(mapping.is_calculated ? 'calculated-field' : 'ai-field');
                element.setAttribute('data-ai-name', mapping.ai_name);
                element.setAttribute('data-semantic-type', mapping.semantic_type);
                element.setAttribute('data-confidence', mapping.confidence);
                
                // Add tooltip
                element.title = `AI: ${{mapping.ai_name}} (${{mapping.semantic_type}}) - Confidence: ${{(mapping.confidence * 100).toFixed(0)}}%`;
            }}
        }});
        
        // Highlight calculated fields
        document.querySelectorAll('.calculated-field').forEach(field => {{
            field.addEventListener('change', () => {{
                console.log('📊 Calculated field changed:', field.getAttribute('data-ai-name'));
                // Here you could trigger recalculation
            }});
        }});
    </script>
</body>
</html>"""
            
            return template
            
        except Exception as e:
            print(f"  ⚠️ Error generating template: {e}")
            return page_data.get('html', '')
    
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
    async def capture_real_page(self, url: str) -> Optional[Dict]:
        """Capture complete page data with styles and scripts"""
        try:
            print("  📸 Capturing page content...")
            
            title = await self.page.title()
            html_content = await self.page.content()
            main_content = await self.extract_main_content_real(html_content)
            
            # Extract CSS and JavaScript
            styles = await self.extract_styles()
            scripts = await self.extract_scripts()
            assets = await self.extract_assets()
            
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
                'styles': styles,
                'scripts': scripts,
                'assets': assets,
                'forms': forms_data,
                'tables': tables_data,
                'navigation': nav_data,
                'captured_at': datetime.now().isoformat()
            }
            
            print(f"  ✅ Captured {len(html_content)} bytes of content")
            print(f"  ✅ Captured {len(styles)} stylesheets, {len(scripts)} scripts")
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
                model="claude-opus-4-1-20250805",
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
                    'ai_named_fields': len([f for f in fields if f.get('ai_generated_name') != f.get('field_name')]),
                    'calculated_fields': len([f for f in fields if f.get('is_calculated')]),
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
            
            # Store calculations with variable mappings
            for calc in calculations:
                calc_record = {
                    'company_id': self.company_id,
                    'page_id': page_id,
                    'page_url': url,
                    'name': calc.get('name', 'Unknown'),
                    'description': calc.get('description', ''),
                    'formula': calc.get('formula', ''),
                    'formula_type': calc.get('formula_type', 'custom_calculation'),
                    'variables': calc.get('variables', []),
                    'variable_mappings': calc.get('variable_mappings', []),
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
