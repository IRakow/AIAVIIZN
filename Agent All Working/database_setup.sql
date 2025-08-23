-- AIVIIZN Multi-Tenant SaaS Database Schema
-- Run this in Supabase SQL Editor to set up the complete structure

-- 1. DROP OLD TABLES (if they exist)
DROP TABLE IF EXISTS pages CASCADE;
DROP TABLE IF EXISTS calculations CASCADE;
DROP TABLE IF EXISTS api_responses CASCADE;

-- 2. COMPANIES TABLE (Core tenant table)
CREATE TABLE IF NOT EXISTS companies (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    domain TEXT UNIQUE,
    base_url TEXT,
    subscription_tier TEXT DEFAULT 'trial',
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. FIELD MAPPINGS (How each company's fields map to our standard)
CREATE TABLE IF NOT EXISTS field_mappings (
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

-- 4. CAPTURED PAGES (Page content with company isolation)
CREATE TABLE IF NOT EXISTS captured_pages (
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

-- 5. COMPANY CALCULATIONS (Extracted formulas per company)
CREATE TABLE IF NOT EXISTS company_calculations (
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

-- 6. COMPANY TEMPLATES (Generated templates per company)
CREATE TABLE IF NOT EXISTS company_templates (
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

-- 7. CAPTURED ENTITIES (Tenants, properties, units, etc.)
CREATE TABLE IF NOT EXISTS captured_entities (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    entity_type TEXT NOT NULL, -- 'tenant', 'unit', 'property', 'payment', 'lease'
    external_id TEXT, -- ID from their system
    field_values JSONB NOT NULL, -- Mapped to canonical fields
    raw_data JSONB, -- Original unmapped data
    page_url TEXT,
    captured_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(company_id, entity_type, external_id)
);

-- 8. FIELD PATTERNS (Learning patterns across all companies)
CREATE TABLE IF NOT EXISTS field_patterns (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    field_type TEXT NOT NULL,
    pattern TEXT NOT NULL,
    pattern_type TEXT, -- 'field_name', 'css_class', 'value_format'
    confidence FLOAT DEFAULT 0.5,
    occurrence_count INT DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(field_type, pattern, pattern_type)
);

-- 9. CREATE INDEXES FOR PERFORMANCE
CREATE INDEX IF NOT EXISTS idx_field_mappings_company 
    ON field_mappings(company_id);

CREATE INDEX IF NOT EXISTS idx_field_mappings_field_type 
    ON field_mappings(field_type);

CREATE INDEX IF NOT EXISTS idx_captured_pages_company 
    ON captured_pages(company_id);

CREATE INDEX IF NOT EXISTS idx_captured_entities_company 
    ON captured_entities(company_id, entity_type);

CREATE INDEX IF NOT EXISTS idx_captured_entities_external 
    ON captured_entities(company_id, external_id);

CREATE INDEX IF NOT EXISTS idx_field_patterns_type 
    ON field_patterns(field_type);

CREATE INDEX IF NOT EXISTS idx_company_calculations_company 
    ON company_calculations(company_id);

CREATE INDEX IF NOT EXISTS idx_company_templates_company_type 
    ON company_templates(company_id, page_type);

-- 10. ROW LEVEL SECURITY (RLS) - CRITICAL FOR SAAS!
-- Enable RLS on all tables
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE field_mappings ENABLE ROW LEVEL SECURITY;
ALTER TABLE captured_pages ENABLE ROW LEVEL SECURITY;
ALTER TABLE company_calculations ENABLE ROW LEVEL SECURITY;
ALTER TABLE company_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE captured_entities ENABLE ROW LEVEL SECURITY;

-- Note: You'll need to create policies based on your auth setup
-- Example policies (adjust based on your auth):

-- Companies can only see their own data
-- CREATE POLICY "Companies can view own data" ON companies
--     FOR ALL USING (auth.uid() = id);

-- CREATE POLICY "Entities belong to company" ON captured_entities
--     FOR ALL USING (company_id IN (
--         SELECT id FROM companies WHERE auth.uid() = id
--     ));

-- 11. HELPER FUNCTIONS

-- Function to get entity counts by type for a company
CREATE OR REPLACE FUNCTION get_entity_counts(p_company_id UUID)
RETURNS TABLE(entity_type TEXT, count BIGINT) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ce.entity_type,
        COUNT(*)::BIGINT as count
    FROM captured_entities ce
    WHERE ce.company_id = p_company_id
    GROUP BY ce.entity_type;
END;
$$ LANGUAGE plpgsql;

-- Function to get field mapping statistics for a company
CREATE OR REPLACE FUNCTION get_field_mapping_stats(p_company_id UUID)
RETURNS TABLE(
    total_fields BIGINT,
    high_confidence BIGINT,
    medium_confidence BIGINT,
    low_confidence BIGINT,
    verified BIGINT
) AS $$
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
$$ LANGUAGE plpgsql;

-- 12. SEED DATA FOR FIELD PATTERNS (Common patterns to start with)
INSERT INTO field_patterns (field_type, pattern, pattern_type, confidence) VALUES
    ('tenant_name', 'tenant', 'field_name', 0.9),
    ('tenant_name', 'resident', 'field_name', 0.9),
    ('tenant_name', 'lessee', 'field_name', 0.85),
    ('tenant_email', 'email', 'field_name', 0.95),
    ('tenant_phone', 'phone', 'field_name', 0.95),
    ('tenant_phone', 'tel', 'field_name', 0.9),
    ('property_name', 'property', 'field_name', 0.85),
    ('property_address', 'address', 'field_name', 0.9),
    ('unit_number', 'unit', 'field_name', 0.9),
    ('unit_number', 'apt', 'field_name', 0.85),
    ('unit_number', 'apartment', 'field_name', 0.85),
    ('rent_amount', 'rent', 'field_name', 0.95),
    ('rent_amount', 'monthly_rent', 'field_name', 0.95),
    ('security_deposit', 'security', 'field_name', 0.85),
    ('security_deposit', 'deposit', 'field_name', 0.8),
    ('balance_due', 'balance', 'field_name', 0.85),
    ('balance_due', 'outstanding', 'field_name', 0.85),
    ('lease_start', 'lease_start', 'field_name', 0.95),
    ('lease_end', 'lease_end', 'field_name', 0.95),
    ('unit_status', 'status', 'field_name', 0.7),
    ('bedrooms', 'bedroom', 'field_name', 0.95),
    ('bedrooms', 'bed', 'field_name', 0.85),
    ('bathrooms', 'bathroom', 'field_name', 0.95),
    ('bathrooms', 'bath', 'field_name', 0.85),
    ('square_feet', 'sqft', 'field_name', 0.95),
    ('square_feet', 'square', 'field_name', 0.8)
ON CONFLICT (field_type, pattern, pattern_type) DO UPDATE
    SET confidence = GREATEST(field_patterns.confidence, EXCLUDED.confidence),
        occurrence_count = field_patterns.occurrence_count + 1;

-- 13. CREATE VIEWS FOR EASIER QUERYING

-- View: Company dashboard summary
CREATE OR REPLACE VIEW company_dashboard AS
SELECT 
    c.id as company_id,
    c.name as company_name,
    c.subscription_tier,
    COUNT(DISTINCT cp.id) as pages_captured,
    COUNT(DISTINCT ce.id) as total_entities,
    COUNT(DISTINCT fm.id) as fields_mapped,
    COUNT(DISTINCT cc.id) as calculations_found,
    MAX(cp.captured_at) as last_capture
FROM companies c
LEFT JOIN captured_pages cp ON c.id = cp.company_id
LEFT JOIN captured_entities ce ON c.id = ce.company_id
LEFT JOIN field_mappings fm ON c.id = fm.company_id
LEFT JOIN company_calculations cc ON c.id = cc.company_id
GROUP BY c.id, c.name, c.subscription_tier;

-- View: Entity summary by company
CREATE OR REPLACE VIEW entity_summary AS
SELECT 
    company_id,
    entity_type,
    COUNT(*) as count,
    MAX(captured_at) as last_updated
FROM captured_entities
GROUP BY company_id, entity_type;

-- 14. GRANT PERMISSIONS (adjust based on your roles)
-- GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
-- GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;
-- GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO authenticated;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'AIVIIZN Multi-Tenant Database Schema created successfully!';
    RAISE NOTICE 'Tables created: companies, field_mappings, captured_pages, company_calculations, company_templates, captured_entities, field_patterns';
    RAISE NOTICE 'Remember to configure Row Level Security policies based on your authentication setup';
END $$;
