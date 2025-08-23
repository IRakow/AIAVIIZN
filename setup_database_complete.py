#!/usr/bin/env python3
"""
Complete database setup for AIVIIZN Multi-Tenant SaaS
This will DELETE all existing tables and create the new structure
"""

import os
import sys
from supabase import create_client
from dotenv import load_dotenv
import time

load_dotenv()

def setup_database():
    """Delete everything and create new multi-tenant structure"""
    
    print("🚀 AIVIIZN DATABASE SETUP - COMPLETE REBUILD")
    print("=" * 60)
    print("⚠️  WARNING: This will DELETE all existing data!")
    print("=" * 60)
    
    # Connect to Supabase
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Missing environment variables!")
        print("   Required: SUPABASE_URL, SUPABASE_SERVICE_KEY")
        return False
    
    try:
        supabase = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return False
    
    # Confirm deletion
    confirm = input("\n⚠️  Type 'DELETE ALL' to confirm database reset: ")
    if confirm != "DELETE ALL":
        print("❌ Cancelled")
        return False
    
    print("\n🗑️ Deleting old tables...")
    
    # SQL commands to execute
    sql_commands = [
        # Drop all old tables first
        """
        DROP TABLE IF EXISTS pages CASCADE;
        DROP TABLE IF EXISTS calculations CASCADE;
        DROP TABLE IF EXISTS api_responses CASCADE;
        DROP TABLE IF EXISTS captured_entities CASCADE;
        DROP TABLE IF EXISTS captured_pages CASCADE;
        DROP TABLE IF EXISTS company_calculations CASCADE;
        DROP TABLE IF EXISTS company_templates CASCADE;
        DROP TABLE IF EXISTS field_mappings CASCADE;
        DROP TABLE IF EXISTS field_patterns CASCADE;
        DROP TABLE IF EXISTS companies CASCADE;
        """,
        
        # Create companies table
        """
        CREATE TABLE companies (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            name TEXT NOT NULL,
            domain TEXT UNIQUE,
            base_url TEXT,
            subscription_tier TEXT DEFAULT 'trial',
            settings JSONB DEFAULT '{}',
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        """,
        
        # Create field_mappings table
        """
        CREATE TABLE field_mappings (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
            page_url TEXT,
            source_field TEXT NOT NULL,
            field_type TEXT NOT NULL,
            canonical_name TEXT,
            sample_values JSONB,
            confidence_score FLOAT DEFAULT 0.5,
            verified BOOLEAN DEFAULT FALSE,
            css_selector TEXT,
            xpath TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(company_id, page_url, source_field)
        );
        """,
        
        # Create captured_pages table
        """
        CREATE TABLE captured_pages (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
            url TEXT NOT NULL,
            title TEXT,
            html_content TEXT,
            main_content TEXT,
            screenshot_path TEXT,
            field_data JSONB,
            api_responses JSONB,
            captured_at TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(company_id, url)
        );
        """,
        
        # Create company_calculations table
        """
        CREATE TABLE company_calculations (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
            page_url TEXT,
            name TEXT NOT NULL,
            description TEXT,
            formula TEXT,
            variables JSONB,
            javascript_function TEXT,
            source TEXT,
            confidence TEXT,
            verified BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        """,
        
        # Create company_templates table
        """
        CREATE TABLE company_templates (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
            page_type TEXT NOT NULL,
            template_path TEXT,
            template_content TEXT,
            field_mappings JSONB,
            calculations JSONB,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(company_id, page_type)
        );
        """,
        
        # Create captured_entities table
        """
        CREATE TABLE captured_entities (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
            entity_type TEXT NOT NULL,
            external_id TEXT,
            field_values JSONB NOT NULL,
            raw_data JSONB,
            page_url TEXT,
            captured_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(company_id, entity_type, external_id)
        );
        """,
        
        # Create field_patterns table
        """
        CREATE TABLE field_patterns (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            field_type TEXT NOT NULL,
            pattern TEXT NOT NULL,
            pattern_type TEXT,
            confidence FLOAT DEFAULT 0.5,
            occurrence_count INT DEFAULT 1,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(field_type, pattern, pattern_type)
        );
        """,
        
        # Create indexes
        """
        CREATE INDEX idx_field_mappings_company ON field_mappings(company_id);
        CREATE INDEX idx_field_mappings_field_type ON field_mappings(field_type);
        CREATE INDEX idx_captured_pages_company ON captured_pages(company_id);
        CREATE INDEX idx_captured_entities_company ON captured_entities(company_id, entity_type);
        CREATE INDEX idx_captured_entities_external ON captured_entities(company_id, external_id);
        CREATE INDEX idx_field_patterns_type ON field_patterns(field_type);
        CREATE INDEX idx_company_calculations_company ON company_calculations(company_id);
        CREATE INDEX idx_company_templates_company_type ON company_templates(company_id, page_type);
        """,
        
        # Insert seed data for field patterns
        """
        INSERT INTO field_patterns (field_type, pattern, pattern_type, confidence) VALUES
            ('tenant_name', 'tenant', 'field_name', 0.9),
            ('tenant_name', 'resident', 'field_name', 0.9),
            ('tenant_name', 'lessee', 'field_name', 0.85),
            ('tenant_name', 'occupant', 'field_name', 0.85),
            ('tenant_email', 'email', 'field_name', 0.95),
            ('tenant_email', 'e-mail', 'field_name', 0.95),
            ('tenant_phone', 'phone', 'field_name', 0.95),
            ('tenant_phone', 'tel', 'field_name', 0.9),
            ('tenant_phone', 'mobile', 'field_name', 0.85),
            ('property_name', 'property', 'field_name', 0.85),
            ('property_name', 'building', 'field_name', 0.8),
            ('property_address', 'address', 'field_name', 0.9),
            ('property_address', 'location', 'field_name', 0.7),
            ('unit_number', 'unit', 'field_name', 0.9),
            ('unit_number', 'apt', 'field_name', 0.85),
            ('unit_number', 'apartment', 'field_name', 0.85),
            ('unit_number', 'suite', 'field_name', 0.85),
            ('rent_amount', 'rent', 'field_name', 0.95),
            ('rent_amount', 'monthly_rent', 'field_name', 0.95),
            ('rent_amount', 'base_rent', 'field_name', 0.9),
            ('security_deposit', 'security', 'field_name', 0.85),
            ('security_deposit', 'deposit', 'field_name', 0.8),
            ('balance_due', 'balance', 'field_name', 0.85),
            ('balance_due', 'outstanding', 'field_name', 0.85),
            ('balance_due', 'owed', 'field_name', 0.8),
            ('late_fee', 'late', 'field_name', 0.8),
            ('late_fee', 'penalty', 'field_name', 0.7),
            ('lease_start', 'lease_start', 'field_name', 0.95),
            ('lease_start', 'start_date', 'field_name', 0.85),
            ('lease_start', 'move_in', 'field_name', 0.8),
            ('lease_end', 'lease_end', 'field_name', 0.95),
            ('lease_end', 'end_date', 'field_name', 0.85),
            ('lease_end', 'expir', 'field_name', 0.8),
            ('unit_status', 'status', 'field_name', 0.7),
            ('unit_status', 'occupied', 'field_name', 0.8),
            ('unit_status', 'vacant', 'field_name', 0.8),
            ('bedrooms', 'bedroom', 'field_name', 0.95),
            ('bedrooms', 'bed', 'field_name', 0.85),
            ('bedrooms', 'br', 'field_name', 0.9),
            ('bathrooms', 'bathroom', 'field_name', 0.95),
            ('bathrooms', 'bath', 'field_name', 0.85),
            ('bathrooms', 'ba', 'field_name', 0.9),
            ('square_feet', 'sqft', 'field_name', 0.95),
            ('square_feet', 'sq_ft', 'field_name', 0.95),
            ('square_feet', 'square', 'field_name', 0.8),
            ('square_feet', 'area', 'field_name', 0.6),
            ('payment_date', 'payment_date', 'field_name', 0.95),
            ('payment_date', 'paid_date', 'field_name', 0.9),
            ('payment_amount', 'payment', 'field_name', 0.8),
            ('payment_amount', 'amount', 'field_name', 0.6)
        ON CONFLICT (field_type, pattern, pattern_type) DO UPDATE
            SET confidence = GREATEST(field_patterns.confidence, EXCLUDED.confidence),
                occurrence_count = field_patterns.occurrence_count + 1;
        """
    ]
    
    print("\n📝 Creating new multi-tenant structure...")
    print("   This will create:")
    print("   • companies table (for each PM company)")
    print("   • field_mappings (intelligent field recognition)")
    print("   • captured_pages (isolated page storage)")
    print("   • captured_entities (tenants, units, properties)")
    print("   • company_calculations (formulas per company)")
    print("   • company_templates (generated pages)")
    print("   • field_patterns (machine learning)")
    
    # Note: Supabase Python client doesn't support raw SQL execution
    # We need to use the Supabase SQL editor or create tables via API
    
    print("\n" + "=" * 60)
    print("📋 MANUAL STEP REQUIRED")
    print("=" * 60)
    print("\nThe Supabase Python client cannot execute raw SQL directly.")
    print("Please follow these steps:\n")
    print("1. Go to your Supabase Dashboard")
    print("2. Navigate to SQL Editor")
    print("3. Copy the following SQL and run it:")
    print("\n" + "-" * 40)
    
    # Output the complete SQL
    complete_sql = "\n".join(sql_commands)
    
    # Save to file
    sql_file = "/Users/ianrakow/Desktop/AIVIIZN/complete_database_setup.sql"
    with open(sql_file, 'w') as f:
        f.write("-- AIVIIZN Complete Database Setup\n")
        f.write("-- This will DELETE all existing tables and create new structure\n\n")
        f.write(complete_sql)
    
    print(f"\n✅ SQL saved to: {sql_file}")
    print("\n📋 Copy and paste the contents of that file into Supabase SQL Editor")
    
    # Now let's verify what we can do via API
    print("\n🔍 Checking current database state...")
    
    tables_to_check = [
        'companies',
        'field_mappings',
        'captured_pages',
        'captured_entities',
        'company_calculations',
        'company_templates',
        'field_patterns'
    ]
    
    print("\nExisting tables:")
    for table in tables_to_check:
        try:
            result = supabase.table(table).select('id').limit(1).execute()
            print(f"  ✅ {table} exists")
        except:
            print(f"  ❌ {table} not found")
    
    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("1. Run the SQL in Supabase SQL Editor")
    print("2. Run: python3 aiviizn_real_agent_saas.py")
    print("3. Create your first company")
    print("4. Start capturing with intelligent field mapping!")
    
    return True

def create_test_company():
    """Create a test company to verify everything works"""
    
    print("\n🧪 Creating test company...")
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Missing environment variables")
        return
    
    try:
        supabase = create_client(supabase_url, supabase_key)
        
        # Create test company
        test_company = {
            'name': 'Demo Property Management',
            'domain': 'demo.example.com',
            'base_url': 'https://demo.example.com',
            'subscription_tier': 'trial',
            'settings': {
                'auto_detect_fields': True,
                'capture_api_responses': True,
                'require_field_verification': False
            }
        }
        
        result = supabase.table('companies').insert(test_company).execute()
        
        if result.data:
            company = result.data[0]
            print(f"✅ Test company created successfully!")
            print(f"   Name: {company['name']}")
            print(f"   ID: {company['id']}")
            
            # Create some test field mappings
            test_mappings = [
                {
                    'company_id': company['id'],
                    'page_url': '/test',
                    'source_field': 'Tenant Name',
                    'field_type': 'tenant_name',
                    'canonical_name': 'tenant_full_name',
                    'confidence_score': 0.95,
                    'verified': True
                },
                {
                    'company_id': company['id'],
                    'page_url': '/test',
                    'source_field': 'Monthly Rent',
                    'field_type': 'rent_amount',
                    'canonical_name': 'monthly_rent_amount',
                    'confidence_score': 0.95,
                    'verified': True
                }
            ]
            
            for mapping in test_mappings:
                supabase.table('field_mappings').insert(mapping).execute()
            
            print("✅ Test field mappings created")
            
            # Create a test entity
            test_entity = {
                'company_id': company['id'],
                'entity_type': 'tenant',
                'external_id': 'test-tenant-001',
                'field_values': {
                    'tenant_full_name': 'John Demo',
                    'tenant_email_address': 'john@demo.com',
                    'monthly_rent_amount': 1500
                },
                'raw_data': {
                    'name': 'John Demo',
                    'email': 'john@demo.com',
                    'rent': '$1,500'
                },
                'page_url': '/test'
            }
            
            supabase.table('captured_entities').insert(test_entity).execute()
            print("✅ Test entity created")
            
            print("\n🎉 Database is working correctly!")
            print(f"   Test company ID: {company['id']}")
            
            # Optional: Clean up
            cleanup = input("\nDelete test data? (y/n): ").lower()
            if cleanup == 'y':
                supabase.table('companies').delete().eq('id', company['id']).execute()
                print("✅ Test data cleaned up")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure you've run the SQL setup first!")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("AIVIIZN DATABASE SETUP")
    print("=" * 60)
    print("\n1. Complete database rebuild (DELETE everything)")
    print("2. Create test company (verify setup)")
    print("3. Exit")
    
    choice = input("\nChoice (1-3): ").strip()
    
    if choice == "1":
        setup_database()
    elif choice == "2":
        create_test_company()
    else:
        print("Exiting...")
