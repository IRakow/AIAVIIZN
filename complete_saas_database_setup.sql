-- =====================================================
-- AIVIIZN SAAS DATABASE SETUP - COMPLETE FROM SCRATCH
-- =====================================================
-- Run this entire script in Supabase SQL Editor
-- This creates a proper SaaS multi-tenant structure with duplicate prevention

-- 1. DROP EXISTING TABLES (if they exist)
-- =====================================================
DROP TABLE IF EXISTS page_errors CASCADE;
DROP TABLE IF EXISTS api_responses CASCADE;
DROP TABLE IF EXISTS calculations CASCADE;
DROP TABLE IF EXISTS pages CASCADE;
DROP TABLE IF EXISTS companies CASCADE;

-- 2. CREATE COMPANIES TABLE (SaaS Multi-tenancy)
-- =====================================================
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

-- Insert AIVIIZN company
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

-- 3. CREATE PAGES TABLE WITH DUPLICATE PREVENTION
-- =====================================================
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
    html_storage_path TEXT, -- Path to compressed HTML in Storage
    html_preview TEXT, -- First 500 chars for quick preview
    meta_data JSONB DEFAULT '{}'::jsonb,
    api_responses JSONB DEFAULT '[]'::jsonb,
    captured_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    
    -- DUPLICATE PREVENTION: Unique constraint
    CONSTRAINT unique_company_url UNIQUE (company_id, url)
);

-- Create indexes for performance
CREATE INDEX idx_pages_company_id ON pages(company_id);
CREATE INDEX idx_pages_url ON pages(url);
CREATE INDEX idx_pages_source_domain ON pages(source_domain);
CREATE INDEX idx_pages_updated_at ON pages(updated_at DESC);

-- 4. CREATE CALCULATIONS TABLE WITH DUPLICATE PREVENTION
-- =====================================================
CREATE TABLE calculations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    page_id UUID REFERENCES pages(id) ON DELETE CASCADE,
    page_url TEXT NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    formula TEXT,
    formula_type VARCHAR(50), -- 'excel', 'gpt4', 'claude', 'reverse_engineered'
    javascript TEXT,
    variables JSONB DEFAULT '[]'::jsonb,
    sample_data JSONB,
    confidence_score DECIMAL(3,2), -- 0.00 to 1.00
    verified BOOLEAN DEFAULT false,
    verified_by VARCHAR(50), -- 'user', 'ai', 'test'
    source VARCHAR(50), -- 'excel', 'api', 'gpt4', 'claude', 'manual'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- DUPLICATE PREVENTION: Unique constraint
    CONSTRAINT unique_company_page_calc UNIQUE (company_id, page_url, name)
);

-- Create indexes
CREATE INDEX idx_calculations_company_id ON calculations(company_id);
CREATE INDEX idx_calculations_page_id ON calculations(page_id);
CREATE INDEX idx_calculations_page_url ON calculations(page_url);
CREATE INDEX idx_calculations_verified ON calculations(verified);

-- 5. CREATE API_RESPONSES TABLE (For captured API data)
-- =====================================================
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
    
    -- DUPLICATE PREVENTION: Unique per endpoint per page
    CONSTRAINT unique_page_endpoint UNIQUE (page_url, endpoint, method)
);

-- Create indexes
CREATE INDEX idx_api_responses_page_url ON api_responses(page_url);
CREATE INDEX idx_api_responses_endpoint ON api_responses(endpoint);
CREATE INDEX idx_api_responses_captured_at ON api_responses(captured_at DESC);

-- 6. CREATE PAGE_ERRORS TABLE (For error tracking)
-- =====================================================
CREATE TABLE page_errors (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    error_type VARCHAR(50), -- 'capture', 'parse', 'storage', 'api'
    error_message TEXT,
    error_details JSONB,
    retry_count INTEGER DEFAULT 0,
    resolved BOOLEAN DEFAULT false,
    resolved_at TIMESTAMPTZ,
    occurred_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Index for finding unresolved errors
    CONSTRAINT idx_unresolved_errors UNIQUE (company_id, url, resolved) WHERE resolved = false
);

-- Create indexes
CREATE INDEX idx_page_errors_company_url ON page_errors(company_id, url);
CREATE INDEX idx_page_errors_unresolved ON page_errors(resolved) WHERE resolved = false;

-- 7. CREATE PAGE_LINKS TABLE (For tracking discovered links)
-- =====================================================
CREATE TABLE page_links (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    source_page_id UUID REFERENCES pages(id) ON DELETE CASCADE,
    source_url TEXT NOT NULL,
    target_url TEXT NOT NULL,
    link_text TEXT,
    link_type VARCHAR(50), -- 'navigation', 'action', 'report', 'external'
    is_processed BOOLEAN DEFAULT false,
    discovered_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ,
    
    -- Prevent duplicate link discoveries
    CONSTRAINT unique_company_link UNIQUE (company_id, source_url, target_url)
);

-- Create indexes
CREATE INDEX idx_page_links_unprocessed ON page_links(company_id, is_processed) WHERE is_processed = false;
CREATE INDEX idx_page_links_target ON page_links(target_url);

-- 8. CREATE FUNCTIONS FOR AUTO-UPDATING TIMESTAMPS
-- =====================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    -- Increment version if it's an update to pages table
    IF TG_TABLE_NAME = 'pages' AND TG_OP = 'UPDATE' THEN
        NEW.version = OLD.version + 1;
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 9. CREATE TRIGGERS FOR AUTO-UPDATING
-- =====================================================
CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_pages_updated_at BEFORE UPDATE ON pages
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_calculations_updated_at BEFORE UPDATE ON calculations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 10. CREATE USEFUL VIEWS FOR SAAS DASHBOARD
-- =====================================================

-- View: Company usage statistics
CREATE OR REPLACE VIEW company_usage_stats AS
SELECT 
    c.id,
    c.name,
    c.subscription_tier,
    COUNT(DISTINCT p.id) as total_pages,
    COUNT(DISTINCT calc.id) as total_calculations,
    COUNT(DISTINCT api.id) as total_api_calls,
    COUNT(DISTINCT pe.id) FILTER (WHERE pe.resolved = false) as unresolved_errors,
    MAX(p.updated_at) as last_activity,
    c.created_at
FROM companies c
LEFT JOIN pages p ON c.id = p.company_id
LEFT JOIN calculations calc ON c.id = calc.company_id
LEFT JOIN api_responses api ON c.id = api.company_id
LEFT JOIN page_errors pe ON c.id = pe.company_id
GROUP BY c.id, c.name, c.subscription_tier, c.created_at;

-- View: Recent activity per company
CREATE OR REPLACE VIEW recent_activity AS
SELECT 
    company_id,
    'page' as activity_type,
    url as details,
    updated_at as activity_time
FROM pages
WHERE updated_at > NOW() - INTERVAL '7 days'
UNION ALL
SELECT 
    company_id,
    'error' as activity_type,
    url as details,
    occurred_at as activity_time
FROM page_errors
WHERE occurred_at > NOW() - INTERVAL '7 days'
ORDER BY activity_time DESC;

-- View: Duplicate check (should be empty if constraints work)
CREATE OR REPLACE VIEW duplicate_check AS
SELECT 
    'pages' as table_name,
    company_id, 
    url as identifier, 
    COUNT(*) as duplicate_count
FROM pages
GROUP BY company_id, url
HAVING COUNT(*) > 1
UNION ALL
SELECT 
    'calculations' as table_name,
    company_id, 
    page_url || '::' || name as identifier, 
    COUNT(*) as duplicate_count
FROM calculations
GROUP BY company_id, page_url, name
HAVING COUNT(*) > 1;

-- 11. CREATE ROW LEVEL SECURITY (RLS) POLICIES
-- =====================================================
-- Enable RLS on all tables
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE pages ENABLE ROW LEVEL SECURITY;
ALTER TABLE calculations ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE page_errors ENABLE ROW LEVEL SECURITY;
ALTER TABLE page_links ENABLE ROW LEVEL SECURITY;

-- Service role has full access (for your Python agent)
CREATE POLICY "Service role has full access to companies" ON companies
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role has full access to pages" ON pages
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role has full access to calculations" ON calculations
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role has full access to api_responses" ON api_responses
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role has full access to page_errors" ON page_errors
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role has full access to page_links" ON page_links
    FOR ALL USING (auth.role() = 'service_role');

-- 12. CREATE HELPER FUNCTIONS FOR THE AGENT
-- =====================================================

-- Function: Upsert page (insert or update)
CREATE OR REPLACE FUNCTION upsert_page(
    p_company_id UUID,
    p_url TEXT,
    p_title TEXT,
    p_template_path TEXT,
    p_html_storage_path TEXT,
    p_html_preview TEXT,
    p_api_responses JSONB
) RETURNS UUID AS $$
DECLARE
    v_page_id UUID;
BEGIN
    INSERT INTO pages (company_id, url, title, template_path, html_storage_path, html_preview, api_responses)
    VALUES (p_company_id, p_url, p_title, p_template_path, p_html_storage_path, p_html_preview, p_api_responses)
    ON CONFLICT (company_id, url) DO UPDATE SET
        title = EXCLUDED.title,
        template_path = EXCLUDED.template_path,
        html_storage_path = EXCLUDED.html_storage_path,
        html_preview = EXCLUDED.html_preview,
        api_responses = EXCLUDED.api_responses,
        updated_at = NOW(),
        version = pages.version + 1
    RETURNING id INTO v_page_id;
    
    RETURN v_page_id;
END;
$$ LANGUAGE plpgsql;

-- Function: Get company stats
CREATE OR REPLACE FUNCTION get_company_stats(p_company_id UUID)
RETURNS TABLE (
    total_pages BIGINT,
    total_calculations BIGINT,
    total_api_calls BIGINT,
    unresolved_errors BIGINT,
    last_activity TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(DISTINCT p.id),
        COUNT(DISTINCT c.id),
        COUNT(DISTINCT a.id),
        COUNT(DISTINCT e.id) FILTER (WHERE e.resolved = false),
        MAX(p.updated_at)
    FROM pages p
    LEFT JOIN calculations c ON p.company_id = c.company_id
    LEFT JOIN api_responses a ON p.company_id = a.company_id
    LEFT JOIN page_errors e ON p.company_id = e.company_id
    WHERE p.company_id = p_company_id;
END;
$$ LANGUAGE plpgsql;

-- 13. VERIFY SETUP
-- =====================================================
-- Run these queries to verify everything is set up correctly:

-- Check companies
SELECT * FROM companies;

-- Check for any duplicates (should be empty)
SELECT * FROM duplicate_check;

-- Check company usage
SELECT * FROM company_usage_stats;

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ AIVIIZN SaaS Database Setup Complete!';
    RAISE NOTICE '   - Multi-tenant structure created';
    RAISE NOTICE '   - Duplicate prevention enabled';
    RAISE NOTICE '   - Auto-updating timestamps active';
    RAISE NOTICE '   - Row Level Security configured';
    RAISE NOTICE '   - Helper functions ready';
    RAISE NOTICE '   - AIVIIZN company created';
END $$;
