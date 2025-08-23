#!/usr/bin/env python3
"""
AIVIIZN SaaS Database Setup - Automatic Setup Script
This script will create the complete database structure programmatically
"""

import os
import sys
from supabase import create_client
from dotenv import load_dotenv
import time

load_dotenv()

# Connect to Supabase
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_KEY')

if not supabase_url or not supabase_key:
    print("❌ Missing SUPABASE_URL or SUPABASE_SERVICE_KEY in .env")
    sys.exit(1)

supabase = create_client(supabase_url, supabase_key)

print("🚀 AIVIIZN SaaS Database Setup")
print("=" * 60)

# SQL statements broken into manageable chunks
sql_statements = [
    # Drop existing tables
    """
    DROP TABLE IF EXISTS page_errors CASCADE;
    DROP TABLE IF EXISTS api_responses CASCADE;
    DROP TABLE IF EXISTS calculations CASCADE;
    DROP TABLE IF EXISTS pages CASCADE;
    DROP TABLE IF EXISTS companies CASCADE;
    """,
    
    # Create companies table
    """
    CREATE TABLE companies (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        name VARCHAR(255) NOT NULL UNIQUE,
        domain VARCHAR(255),
        base_url VARCHAR(500),
        subscription_tier VARCHAR(50) DEFAULT 'free',
        settings JSONB DEFAULT '{
            "auto_detect_fields": true,
            "capture_api_responses": true,
            "require_field_verification": false,
            "max_pages": 1000,
            "max_storage_gb": 10
        }'::jsonb,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW(),
        is_active BOOLEAN DEFAULT true
    );
    """,
    
    # Insert AIVIIZN company
    """
    INSERT INTO companies (name, domain, base_url, subscription_tier, settings) 
    VALUES (
        'AIVIIZN',
        'aiviizn.com',
        'https://aiviizn.com',
        'enterprise',
        '{
            "auto_detect_fields": true,
            "capture_api_responses": true,
            "require_field_verification": false,
            "max_pages": 10000,
            "max_storage_gb": 100,
            "allowed_source_domains": ["celticprop.appfolio.com"]
        }'::jsonb
    ) ON CONFLICT (name) DO NOTHING;
    """,
    
    # Create pages table
    """
    CREATE TABLE pages (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
        url TEXT NOT NULL,
        source_domain VARCHAR(255) GENERATED ALWAYS AS (
            CASE 
                WHEN url LIKE 'http%' THEN 
                    split_part(split_part(url, '//', 2), '/', 1)
                ELSE NULL 
            END
        ) STORED,
        title TEXT,
        template_path TEXT,
        html_storage_path TEXT,
        html_preview TEXT,
        meta_data JSONB DEFAULT '{}'::jsonb,
        api_responses JSONB DEFAULT '[]'::jsonb,
        captured_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW(),
        version INTEGER DEFAULT 1,
        is_active BOOLEAN DEFAULT true,
        CONSTRAINT unique_company_url UNIQUE (company_id, url)
    );
    """,
    
    # Create indexes for pages
    """
    CREATE INDEX idx_pages_company_id ON pages(company_id);
    CREATE INDEX idx_pages_url ON pages(url);
    CREATE INDEX idx_pages_source_domain ON pages(source_domain);
    CREATE INDEX idx_pages_updated_at ON pages(updated_at DESC);
    """,
    
    # Create calculations table
    """
    CREATE TABLE calculations (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
        page_id UUID REFERENCES pages(id) ON DELETE CASCADE,
        page_url TEXT NOT NULL,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        formula TEXT,
        formula_type VARCHAR(50),
        javascript TEXT,
        variables JSONB DEFAULT '[]'::jsonb,
        sample_data JSONB,
        confidence_score DECIMAL(3,2),
        verified BOOLEAN DEFAULT false,
        verified_by VARCHAR(50),
        source VARCHAR(50),
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW(),
        CONSTRAINT unique_company_page_calc UNIQUE (company_id, page_url, name)
    );
    """,
    
    # Create calculations indexes
    """
    CREATE INDEX idx_calculations_company_id ON calculations(company_id);
    CREATE INDEX idx_calculations_page_id ON calculations(page_id);
    CREATE INDEX idx_calculations_page_url ON calculations(page_url);
    CREATE INDEX idx_calculations_verified ON calculations(verified);
    """,
    
    # Create api_responses table
    """
    CREATE TABLE api_responses (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
        page_id UUID REFERENCES pages(id) ON DELETE CASCADE,
        page_url TEXT NOT NULL,
        endpoint TEXT NOT NULL,
        method VARCHAR(10) DEFAULT 'GET',
        status_code INTEGER,
        request_data JSONB,
        response_data JSONB,
        response_headers JSONB,
        extracted_formulas JSONB,
        response_time_ms INTEGER,
        captured_at TIMESTAMPTZ DEFAULT NOW(),
        CONSTRAINT unique_page_endpoint UNIQUE (page_url, endpoint, method)
    );
    """,
    
    # Create api_responses indexes
    """
    CREATE INDEX idx_api_responses_page_url ON api_responses(page_url);
    CREATE INDEX idx_api_responses_endpoint ON api_responses(endpoint);
    CREATE INDEX idx_api_responses_captured_at ON api_responses(captured_at DESC);
    """,
    
    # Create page_errors table
    """
    CREATE TABLE page_errors (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
        url TEXT NOT NULL,
        error_type VARCHAR(50),
        error_message TEXT,
        error_details JSONB,
        retry_count INTEGER DEFAULT 0,
        resolved BOOLEAN DEFAULT false,
        resolved_at TIMESTAMPTZ,
        occurred_at TIMESTAMPTZ DEFAULT NOW()
    );
    """,
    
    # Create page_errors indexes
    """
    CREATE INDEX idx_page_errors_company_url ON page_errors(company_id, url);
    CREATE INDEX idx_page_errors_unresolved ON page_errors(resolved) WHERE resolved = false;
    """,
    
    # Create page_links table
    """
    CREATE TABLE page_links (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
        source_page_id UUID REFERENCES pages(id) ON DELETE CASCADE,
        source_url TEXT NOT NULL,
        target_url TEXT NOT NULL,
        link_text TEXT,
        link_type VARCHAR(50),
        is_processed BOOLEAN DEFAULT false,
        discovered_at TIMESTAMPTZ DEFAULT NOW(),
        processed_at TIMESTAMPTZ,
        CONSTRAINT unique_company_link UNIQUE (company_id, source_url, target_url)
    );
    """,
    
    # Create page_links indexes
    """
    CREATE INDEX idx_page_links_unprocessed ON page_links(company_id, is_processed) WHERE is_processed = false;
    CREATE INDEX idx_page_links_target ON page_links(target_url);
    """,
    
    # Create update trigger function
    """
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = NOW();
        IF TG_TABLE_NAME = 'pages' AND TG_OP = 'UPDATE' THEN
            NEW.version = OLD.version + 1;
        END IF;
        RETURN NEW;
    END;
    $$ language 'plpgsql';
    """,
    
    # Create triggers
    """
    CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
    CREATE TRIGGER update_pages_updated_at BEFORE UPDATE ON pages
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
    CREATE TRIGGER update_calculations_updated_at BEFORE UPDATE ON calculations
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """
]

# Unfortunately, we can't execute raw SQL through the Python client
# We need to use the Supabase Dashboard or connect directly to PostgreSQL

print("\n❌ The Supabase Python client doesn't support raw SQL execution.")
print("\n📋 Please follow these steps:\n")

print("1. Copy the complete SQL setup:")
print("   cat complete_saas_database_setup.sql\n")

print("2. Go to Supabase SQL Editor:")
print(f"   https://supabase.com/dashboard/project/{supabase_url.split('//')[1].split('.')[0]}/sql\n")

print("3. Click 'New Query'")
print("4. Paste the SQL")
print("5. Click 'Run'\n")

print("=" * 60)
print("\n📝 Alternative: Use the automated setup script")
print("   ./setup_saas_database.sh")

# Try to at least check if tables exist
print("\n🔍 Checking current database state...")

try:
    # Check if companies table exists
    companies = supabase.table('companies').select('*').limit(1).execute()
    print("✅ Companies table exists")
    
    # Check for AIVIIZN company
    aiviizn = supabase.table('companies').select('*').eq('name', 'AIVIIZN').execute()
    if aiviizn.data:
        print(f"✅ AIVIIZN company found (ID: {aiviizn.data[0]['id']})")
        
        # Try to create a test page to check constraints
        test_data = {
            'company_id': aiviizn.data[0]['id'],
            'url': 'https://test.duplicate.check',
            'title': 'Test'
        }
        
        # Try first insert
        try:
            result1 = supabase.table('pages').insert(test_data).execute()
            print("✅ Pages table accepts inserts")
            
            # Try duplicate (should fail if constraints work)
            try:
                result2 = supabase.table('pages').insert(test_data).execute()
                print("❌ WARNING: Duplicate prevention NOT working!")
            except:
                print("✅ Duplicate prevention is working!")
            
            # Clean up
            supabase.table('pages').delete().eq('url', 'https://test.duplicate.check').execute()
            
        except Exception as e:
            print(f"ℹ️ Pages table status: {str(e)[:50]}")
    else:
        print("❌ AIVIIZN company not found - database needs setup")
        
except Exception as e:
    print(f"❌ Database not set up yet: {str(e)[:100]}")
    print("\n⚠️ Please run the SQL setup first!")

print("\n" + "=" * 60)
print("📋 After running the SQL, test with:")
print("   python test_saas_database.py")
