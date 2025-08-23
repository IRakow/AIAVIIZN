-- AIVIIZN Complete Database Setup
-- This will DELETE all existing tables and create new multi-tenant structure
-- Run this ENTIRE script in Supabase SQL Editor

-- ============================================
-- STEP 1: DROP ALL EXISTING TABLES
-- ============================================

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

-- Drop any views if they exist
DROP VIEW IF EXISTS company_dashboard CASCADE;
DROP VIEW IF EXISTS entity_summary CASCADE;

-- Drop any functions if they exist
DROP FUNCTION IF EXISTS get_entity_counts(UUID) CASCADE;
DROP FUNCTION IF EXISTS get_field_mapping_stats(UUID) CASCADE;

-- ============================================
-- STEP 2: CREATE COMPANIES TABLE (Core)
-- ============================================

CREATE TABLE companies (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    domain TEXT UNIQUE,
    base_url TEXT,
    subscription_tier TEXT DEFAULT 'trial' CHECK (subscription_tier IN ('trial', 'basic', 'pro', 'enterprise', 'migrated')),
    settings JSONB DEFAULT '{"auto_detect_fields": true, "capture_api_responses": true, "require_field_verification": false}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- STEP 3: CREATE FIELD MAPPINGS TABLE
-- ============================================

CREATE TABLE field_mappings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    page_url TEXT,
    source_field TEXT NOT NULL,
    field_type TEXT NOT NULL,
    canonical_name TEXT,
    sample_values JSONB DEFAULT '[]'::jsonb,
    confidence_score FLOAT DEFAULT 0.5 CHECK (confidence_score >= 0 AND confidence_score <= 1),
    verified BOOLEAN DEFAULT FALSE,
    css_selector TEXT,
    xpath TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(company_id, page_url, source_field)
);

-- ============================================
-- STEP 4: CREATE CAPTURED PAGES TABLE
-- ============================================

CREATE TABLE captured_pages (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    title TEXT,
    html_content TEXT,
    main_content TEXT,
    screenshot_path TEXT,
    field_data JSONB DEFAULT '{}'::jsonb,
    api_responses JSONB DEFAULT '[]'::jsonb,
    captured_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(company_id, url)
);

-- ============================================
-- STEP 5: CREATE COMPANY CALCULATIONS TABLE
-- ============================================

CREATE TABLE company_calculations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    page_url TEXT,
    name TEXT NOT NULL,
    description TEXT,
    formula TEXT,
    variables JSONB DEFAULT '[]'::jsonb,
    javascript_function TEXT,
    source TEXT CHECK (source IN ('excel', 'reverse_engineering', 'api_trigger', 'source_code', 'gpt4', 'claude', 'manual', 'fallback')),
    confidence TEXT CHECK (confidence IN ('high', 'medium', 'low')),
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- STEP 6: CREATE COMPANY TEMPLATES TABLE
-- ============================================

CREATE TABLE company_templates (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    page_type TEXT NOT NULL,
    template_path TEXT,
    template_content TEXT,
    field_mappings JSONB DEFAULT '{}'::jsonb,
    calculations JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(company_id, page_type)
);

-- ============================================
-- STEP 7: CREATE CAPTURED ENTITIES TABLE
-- ============================================

CREATE TABLE captured_entities (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    entity_type TEXT NOT NULL CHECK (entity_type IN ('tenant', 'unit', 'property', 'payment', 'lease', 'owner', 'vendor', 'maintenance', 'other')),
    external_id TEXT,
    field_values JSONB NOT NULL DEFAULT '{}'::jsonb,
    raw_data JSONB DEFAULT '{}'::jsonb,
    page_url TEXT,
    captured_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(company_id, entity_type, external_id)
);

-- ============================================
-- STEP 8: CREATE FIELD PATTERNS TABLE
-- ============================================

CREATE TABLE field_patterns (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    field_type TEXT NOT NULL,
    pattern TEXT NOT NULL,
    pattern_type TEXT CHECK (pattern_type IN ('field_name', 'css_class', 'value_format', 'regex', 'xpath')),
    confidence FLOAT DEFAULT 0.5 CHECK (confidence >= 0 AND confidence <= 1),
    occurrence_count INT DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(field_type, pattern, pattern_type)
);

-- ============================================
-- STEP 9: CREATE ALL INDEXES
-- ============================================

CREATE INDEX idx_companies_domain ON companies(domain);
CREATE INDEX idx_companies_subscription ON companies(subscription_tier);

CREATE INDEX idx_field_mappings_company ON field_mappings(company_id);
CREATE INDEX idx_field_mappings_field_type ON field_mappings(field_type);
CREATE INDEX idx_field_mappings_confidence ON field_mappings(confidence_score);
CREATE INDEX idx_field_mappings_verified ON field_mappings(verified);

CREATE INDEX idx_captured_pages_company ON captured_pages(company_id);
CREATE INDEX idx_captured_pages_url ON captured_pages(url);
CREATE INDEX idx_captured_pages_captured_at ON captured_pages(captured_at);

CREATE INDEX idx_captured_entities_company ON captured_entities(company_id, entity_type);
CREATE INDEX idx_captured_entities_external ON captured_entities(company_id, external_id);
CREATE INDEX idx_captured_entities_type ON captured_entities(entity_type);
CREATE INDEX idx_captured_entities_updated ON captured_entities(updated_at);

CREATE INDEX idx_field_patterns_type ON field_patterns(field_type);
CREATE INDEX idx_field_patterns_confidence ON field_patterns(confidence);

CREATE INDEX idx_company_calculations_company ON company_calculations(company_id);
CREATE INDEX idx_company_calculations_verified ON company_calculations(verified);

CREATE INDEX idx_company_templates_company_type ON company_templates(company_id, page_type);

-- ============================================
-- STEP 10: CREATE HELPER FUNCTIONS
-- ============================================

-- Function to get entity counts by type for a company
CREATE OR REPLACE FUNCTION get_entity_counts(p_company_id UUID)
RETURNS TABLE(entity_type TEXT, count BIGINT) 
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ce.entity_type,
        COUNT(*)::BIGINT as count
    FROM captured_entities ce
    WHERE ce.company_id = p_company_id
    GROUP BY ce.entity_type
    ORDER BY count DESC;
END;
$$;

-- Function to get field mapping statistics for a company
CREATE OR REPLACE FUNCTION get_field_mapping_stats(p_company_id UUID)
RETURNS TABLE(
    total_fields BIGINT,
    high_confidence BIGINT,
    medium_confidence BIGINT,
    low_confidence BIGINT,
    verified BIGINT
) 
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::BIGINT as total_fields,
        COUNT(CASE WHEN confidence_score > 0.8 THEN 1 END)::BIGINT as high_confidence,
        COUNT(CASE WHEN confidence_score > 0.5 AND confidence_score <= 0.8 THEN 1 END)::BIGINT as medium_confidence,
        COUNT(CASE WHEN confidence_score <= 0.5 THEN 1 END)::BIGINT as low_confidence,
        COUNT(CASE WHEN verified = true THEN 1 END)::BIGINT as verified
    FROM field_mappings
    WHERE company_id = p_company_id;
END;
$$;

-- ============================================
-- STEP 11: CREATE VIEWS
-- ============================================

-- Company dashboard summary view
CREATE VIEW company_dashboard AS
SELECT 
    c.id as company_id,
    c.name as company_name,
    c.domain,
    c.subscription_tier,
    COUNT(DISTINCT cp.id) as pages_captured,
    COUNT(DISTINCT ce.id) as total_entities,
    COUNT(DISTINCT CASE WHEN ce.entity_type = 'tenant' THEN ce.id END) as total_tenants,
    COUNT(DISTINCT CASE WHEN ce.entity_type = 'unit' THEN ce.id END) as total_units,
    COUNT(DISTINCT CASE WHEN ce.entity_type = 'property' THEN ce.id END) as total_properties,
    COUNT(DISTINCT fm.id) as fields_mapped,
    COUNT(DISTINCT CASE WHEN fm.verified = true THEN fm.id END) as fields_verified,
    COUNT(DISTINCT cc.id) as calculations_found,
    MAX(cp.captured_at) as last_capture,
    c.created_at
FROM companies c
LEFT JOIN captured_pages cp ON c.id = cp.company_id
LEFT JOIN captured_entities ce ON c.id = ce.company_id
LEFT JOIN field_mappings fm ON c.id = fm.company_id
LEFT JOIN company_calculations cc ON c.id = cc.company_id
GROUP BY c.id, c.name, c.domain, c.subscription_tier, c.created_at;

-- Entity summary by company and type
CREATE VIEW entity_summary AS
SELECT 
    c.name as company_name,
    ce.company_id,
    ce.entity_type,
    COUNT(*) as count,
    MAX(ce.captured_at) as last_captured,
    MAX(ce.updated_at) as last_updated
FROM captured_entities ce
JOIN companies c ON ce.company_id = c.id
GROUP BY c.name, ce.company_id, ce.entity_type
ORDER BY c.name, ce.entity_type;

-- ============================================
-- STEP 12: INSERT SEED DATA FOR FIELD PATTERNS
-- ============================================

INSERT INTO field_patterns (field_type, pattern, pattern_type, confidence) VALUES
    -- Tenant patterns
    ('tenant_name', 'tenant', 'field_name', 0.9),
    ('tenant_name', 'resident', 'field_name', 0.9),
    ('tenant_name', 'lessee', 'field_name', 0.85),
    ('tenant_name', 'occupant', 'field_name', 0.85),
    ('tenant_name', 'renter', 'field_name', 0.85),
    ('tenant_email', 'email', 'field_name', 0.95),
    ('tenant_email', 'e-mail', 'field_name', 0.95),
    ('tenant_email', 'mail', 'field_name', 0.7),
    ('tenant_phone', 'phone', 'field_name', 0.95),
    ('tenant_phone', 'tel', 'field_name', 0.9),
    ('tenant_phone', 'mobile', 'field_name', 0.85),
    ('tenant_phone', 'cell', 'field_name', 0.85),
    
    -- Property/Unit patterns
    ('property_name', 'property', 'field_name', 0.85),
    ('property_name', 'building', 'field_name', 0.8),
    ('property_name', 'complex', 'field_name', 0.75),
    ('property_address', 'address', 'field_name', 0.9),
    ('property_address', 'location', 'field_name', 0.7),
    ('property_address', 'street', 'field_name', 0.85),
    ('unit_number', 'unit', 'field_name', 0.9),
    ('unit_number', 'apt', 'field_name', 0.85),
    ('unit_number', 'apartment', 'field_name', 0.85),
    ('unit_number', 'suite', 'field_name', 0.85),
    ('unit_number', 'room', 'field_name', 0.7),
    
    -- Financial patterns
    ('rent_amount', 'rent', 'field_name', 0.95),
    ('rent_amount', 'monthly_rent', 'field_name', 0.95),
    ('rent_amount', 'base_rent', 'field_name', 0.9),
    ('rent_amount', 'rental', 'field_name', 0.85),
    ('security_deposit', 'security', 'field_name', 0.85),
    ('security_deposit', 'deposit', 'field_name', 0.8),
    ('security_deposit', 'sec_dep', 'field_name', 0.9),
    ('balance_due', 'balance', 'field_name', 0.85),
    ('balance_due', 'outstanding', 'field_name', 0.85),
    ('balance_due', 'owed', 'field_name', 0.8),
    ('balance_due', 'due', 'field_name', 0.7),
    ('late_fee', 'late', 'field_name', 0.8),
    ('late_fee', 'penalty', 'field_name', 0.7),
    ('late_fee', 'late_charge', 'field_name', 0.9),
    
    -- Date patterns
    ('lease_start', 'lease_start', 'field_name', 0.95),
    ('lease_start', 'start_date', 'field_name', 0.85),
    ('lease_start', 'move_in', 'field_name', 0.8),
    ('lease_start', 'movein', 'field_name', 0.8),
    ('lease_start', 'begin', 'field_name', 0.7),
    ('lease_end', 'lease_end', 'field_name', 0.95),
    ('lease_end', 'end_date', 'field_name', 0.85),
    ('lease_end', 'expir', 'field_name', 0.8),
    ('lease_end', 'move_out', 'field_name', 0.8),
    ('lease_end', 'moveout', 'field_name', 0.8),
    
    -- Status patterns
    ('unit_status', 'status', 'field_name', 0.7),
    ('unit_status', 'occupied', 'field_name', 0.8),
    ('unit_status', 'vacant', 'field_name', 0.8),
    ('unit_status', 'available', 'field_name', 0.75),
    ('lease_status', 'lease_status', 'field_name', 0.9),
    ('lease_status', 'active', 'field_name', 0.7),
    ('payment_status', 'payment_status', 'field_name', 0.9),
    ('payment_status', 'paid', 'field_name', 0.75),
    
    -- Property details
    ('bedrooms', 'bedroom', 'field_name', 0.95),
    ('bedrooms', 'bed', 'field_name', 0.85),
    ('bedrooms', 'br', 'field_name', 0.9),
    ('bedrooms', 'bdrm', 'field_name', 0.9),
    ('bathrooms', 'bathroom', 'field_name', 0.95),
    ('bathrooms', 'bath', 'field_name', 0.85),
    ('bathrooms', 'ba', 'field_name', 0.9),
    ('bathrooms', 'bthrm', 'field_name', 0.9),
    ('square_feet', 'sqft', 'field_name', 0.95),
    ('square_feet', 'sq_ft', 'field_name', 0.95),
    ('square_feet', 'square', 'field_name', 0.8),
    ('square_feet', 'area', 'field_name', 0.6),
    ('square_feet', 'size', 'field_name', 0.5),
    
    -- Payment patterns
    ('payment_date', 'payment_date', 'field_name', 0.95),
    ('payment_date', 'paid_date', 'field_name', 0.9),
    ('payment_date', 'date_paid', 'field_name', 0.9),
    ('payment_date', 'received', 'field_name', 0.7),
    ('payment_amount', 'payment', 'field_name', 0.8),
    ('payment_amount', 'amount', 'field_name', 0.6),
    ('payment_amount', 'paid', 'field_name', 0.7),
    
    -- Owner patterns
    ('owner_name', 'owner', 'field_name', 0.9),
    ('owner_name', 'landlord', 'field_name', 0.85),
    ('owner_name', 'lessor', 'field_name', 0.8),
    ('owner_email', 'owner_email', 'field_name', 0.95),
    ('owner_email', 'landlord_email', 'field_name', 0.9)
ON CONFLICT (field_type, pattern, pattern_type) DO UPDATE
    SET confidence = GREATEST(field_patterns.confidence, EXCLUDED.confidence),
        occurrence_count = field_patterns.occurrence_count + 1;

-- ============================================
-- STEP 13: ENABLE ROW LEVEL SECURITY
-- ============================================

-- Enable RLS on all tables
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE field_mappings ENABLE ROW LEVEL SECURITY;
ALTER TABLE captured_pages ENABLE ROW LEVEL SECURITY;
ALTER TABLE company_calculations ENABLE ROW LEVEL SECURITY;
ALTER TABLE company_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE captured_entities ENABLE ROW LEVEL SECURITY;
-- Note: field_patterns is shared across all companies, so no RLS

-- Create basic policies (adjust based on your auth system)
-- These are examples - modify based on your actual auth setup

-- Companies can only see their own data
CREATE POLICY "Companies select own" ON companies
    FOR SELECT USING (true);  -- Adjust based on auth

CREATE POLICY "Companies insert own" ON companies
    FOR INSERT WITH CHECK (true);  -- Adjust based on auth

CREATE POLICY "Companies update own" ON companies
    FOR UPDATE USING (true);  -- Adjust based on auth

-- Field mappings belong to company
CREATE POLICY "Field mappings company isolation" ON field_mappings
    FOR ALL USING (true);  -- Adjust to check company_id against auth

-- Captured pages belong to company
CREATE POLICY "Captured pages company isolation" ON captured_pages
    FOR ALL USING (true);  -- Adjust to check company_id against auth

-- Entities belong to company
CREATE POLICY "Entities company isolation" ON captured_entities
    FOR ALL USING (true);  -- Adjust to check company_id against auth

-- Calculations belong to company
CREATE POLICY "Calculations company isolation" ON company_calculations
    FOR ALL USING (true);  -- Adjust to check company_id against auth

-- Templates belong to company
CREATE POLICY "Templates company isolation" ON company_templates
    FOR ALL USING (true);  -- Adjust to check company_id against auth

-- ============================================
-- STEP 14: CREATE TRIGGERS FOR UPDATED_AT
-- ============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add triggers to tables with updated_at
CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_company_templates_updated_at BEFORE UPDATE ON company_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_captured_entities_updated_at BEFORE UPDATE ON captured_entities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- STEP 15: INSERT DEMO COMPANY (Optional)
-- ============================================

-- Uncomment to create a demo company
/*
INSERT INTO companies (name, domain, base_url, subscription_tier, settings)
VALUES (
    'Demo Property Management',
    'demo.example.com',
    'https://demo.example.com',
    'trial',
    '{"auto_detect_fields": true, "capture_api_responses": true}'::jsonb
);
*/

-- ============================================
-- SUCCESS MESSAGE
-- ============================================

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
    RAISE NOTICE '✅ AIVIIZN DATABASE SETUP COMPLETE!';
    RAISE NOTICE '========================================';
    RAISE NOTICE '';
    RAISE NOTICE 'Created tables:';
    RAISE NOTICE '  • companies (multi-tenant core)';
    RAISE NOTICE '  • field_mappings (intelligent field recognition)';
    RAISE NOTICE '  • captured_pages (page storage)';
    RAISE NOTICE '  • captured_entities (tenants, units, properties)';
    RAISE NOTICE '  • company_calculations (formulas)';
    RAISE NOTICE '  • company_templates (generated pages)';
    RAISE NOTICE '  • field_patterns (machine learning)';
    RAISE NOTICE '';
    RAISE NOTICE 'Created views:';
    RAISE NOTICE '  • company_dashboard';
    RAISE NOTICE '  • entity_summary';
    RAISE NOTICE '';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '  1. Run: python3 aiviizn_real_agent_saas.py';
    RAISE NOTICE '  2. Create your first company';
    RAISE NOTICE '  3. Start capturing with field mapping!';
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
END $$;
