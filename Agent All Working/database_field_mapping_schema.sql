-- AIVIIZN Complete Database Schema with Field Mapping & Duplicate Prevention
-- Run this in your Supabase SQL editor

-- 1. Add checksum column to pages table if it doesn't exist
ALTER TABLE pages 
ADD COLUMN IF NOT EXISTS content_checksum VARCHAR(64),
ADD COLUMN IF NOT EXISTS normalized_url TEXT;

-- Create index for faster duplicate detection
CREATE INDEX IF NOT EXISTS idx_pages_checksum ON pages(content_checksum);
CREATE INDEX IF NOT EXISTS idx_pages_normalized_url ON pages(normalized_url);
CREATE UNIQUE INDEX IF NOT EXISTS idx_pages_unique_content ON pages(company_id, content_checksum);

-- 2. Create field_mappings table for intelligent field identification
CREATE TABLE IF NOT EXISTS field_mappings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    page_url TEXT NOT NULL,
    form_id VARCHAR(255),
    form_name VARCHAR(255),
    field_name VARCHAR(255) NOT NULL,
    field_type VARCHAR(50), -- HTML input type (text, email, select, etc.)
    semantic_type VARCHAR(100), -- Identified type (tenant_name, unit_number, rent_amount, etc.)
    field_attributes JSONB, -- All HTML attributes
    confidence NUMERIC(3,2), -- Confidence score 0.00 to 1.00
    signature VARCHAR(64) UNIQUE, -- Unique signature for duplicate prevention
    examples JSONB, -- Example values seen
    validation_rules JSONB, -- Validation patterns
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(company_id, signature)
);

-- Indexes for field_mappings
CREATE INDEX IF NOT EXISTS idx_field_mappings_company ON field_mappings(company_id);
CREATE INDEX IF NOT EXISTS idx_field_mappings_semantic ON field_mappings(semantic_type);
CREATE INDEX IF NOT EXISTS idx_field_mappings_signature ON field_mappings(signature);
CREATE INDEX IF NOT EXISTS idx_field_mappings_page_url ON field_mappings(page_url);

-- 3. Create duplicate_prevention_log table for tracking
CREATE TABLE IF NOT EXISTS duplicate_prevention_log (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    normalized_url TEXT NOT NULL,
    checksum VARCHAR(64) NOT NULL,
    duplicate_of_page_id UUID REFERENCES pages(id),
    prevented_at TIMESTAMPTZ DEFAULT NOW(),
    reason TEXT
);

-- Index for duplicate prevention log
CREATE INDEX IF NOT EXISTS idx_dup_log_company ON duplicate_prevention_log(company_id);
CREATE INDEX IF NOT EXISTS idx_dup_log_checksum ON duplicate_prevention_log(checksum);

-- 4. Create field_mapping_patterns table for pattern matching
CREATE TABLE IF NOT EXISTS field_mapping_patterns (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    semantic_type VARCHAR(100) NOT NULL,
    pattern TEXT NOT NULL,
    priority INTEGER DEFAULT 0,
    confidence_boost NUMERIC(3,2) DEFAULT 0.00,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert default patterns for property management fields
INSERT INTO field_mapping_patterns (semantic_type, pattern, priority, confidence_boost) VALUES
-- Tenant fields
('tenant_name', 'tenant.*name', 10, 0.90),
('tenant_name', 'resident.*name', 9, 0.85),
('tenant_name', 'lessee', 8, 0.80),
('tenant_name', 'occupant', 7, 0.75),

-- Unit fields
('unit_number', 'unit.*num', 10, 0.90),
('unit_number', 'apt.*num', 9, 0.85),
('unit_number', 'apartment', 8, 0.80),
('unit_number', 'suite', 7, 0.75),

-- Property fields
('property_name', 'property.*name', 10, 0.90),
('property_name', 'building.*name', 9, 0.85),
('property_name', 'complex', 8, 0.80),

-- Financial fields
('rent_amount', 'rent.*amount', 10, 0.95),
('rent_amount', 'monthly.*rent', 10, 0.95),
('rent_amount', 'base.*rent', 9, 0.90),
('balance', 'balance', 10, 0.95),
('balance', 'amount.*due', 9, 0.90),
('balance', 'outstanding', 8, 0.85),

-- Date fields
('lease_start', 'lease.*start', 10, 0.90),
('lease_start', 'move.*in.*date', 10, 0.90),
('lease_start', 'start.*date', 8, 0.80),
('lease_end', 'lease.*end', 10, 0.90),
('lease_end', 'move.*out.*date', 10, 0.90),
('lease_end', 'expir', 9, 0.85),

-- Contact fields
('email', 'email', 10, 1.00),
('email', 'e-mail', 10, 1.00),
('phone', 'phone', 10, 0.95),
('phone', 'telephone', 10, 0.95),
('phone', 'mobile', 9, 0.90),
('phone', 'cell', 9, 0.90),

-- Address fields
('address', 'address', 10, 0.90),
('address', 'street', 9, 0.85),
('address_city', 'city', 10, 0.95),
('address_state', 'state', 10, 0.95),
('address_zip', 'zip', 10, 0.95),
('address_zip', 'postal', 9, 0.90),

-- Status fields
('status', 'status', 10, 0.90),
('status', 'state', 7, 0.70),
('payment_status', 'payment.*status', 10, 0.95),
('lease_status', 'lease.*status', 10, 0.95),

-- Other common fields
('notes', 'notes', 10, 0.90),
('notes', 'comments', 9, 0.85),
('notes', 'remarks', 8, 0.80),
('description', 'description', 10, 0.90),
('description', 'memo', 8, 0.75)
ON CONFLICT DO NOTHING;

-- 5. Create field_value_examples table to store example values
CREATE TABLE IF NOT EXISTS field_value_examples (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    field_mapping_id UUID REFERENCES field_mappings(id) ON DELETE CASCADE,
    value TEXT,
    frequency INTEGER DEFAULT 1,
    first_seen TIMESTAMPTZ DEFAULT NOW(),
    last_seen TIMESTAMPTZ DEFAULT NOW()
);

-- Index for field value examples
CREATE INDEX IF NOT EXISTS idx_field_values_mapping ON field_value_examples(field_mapping_id);

-- 6. Function to check for duplicate pages
CREATE OR REPLACE FUNCTION check_page_duplicate(
    p_company_id UUID,
    p_url TEXT,
    p_checksum VARCHAR(64)
)
RETURNS TABLE(is_duplicate BOOLEAN, existing_page_id UUID) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        CASE WHEN COUNT(*) > 0 THEN TRUE ELSE FALSE END as is_duplicate,
        MAX(id) as existing_page_id
    FROM pages
    WHERE company_id = p_company_id
    AND (normalized_url = p_url OR content_checksum = p_checksum);
END;
$$ LANGUAGE plpgsql;

-- 7. Function to get field mapping statistics
CREATE OR REPLACE FUNCTION get_field_mapping_stats(p_company_id UUID)
RETURNS TABLE(
    semantic_type VARCHAR(100),
    field_count BIGINT,
    avg_confidence NUMERIC,
    example_values TEXT[]
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        fm.semantic_type,
        COUNT(DISTINCT fm.id) as field_count,
        AVG(fm.confidence) as avg_confidence,
        ARRAY_AGG(DISTINCT fve.value ORDER BY fve.frequency DESC LIMIT 5) as example_values
    FROM field_mappings fm
    LEFT JOIN field_value_examples fve ON fm.id = fve.field_mapping_id
    WHERE fm.company_id = p_company_id
    GROUP BY fm.semantic_type
    ORDER BY field_count DESC;
END;
$$ LANGUAGE plpgsql;

-- 8. Trigger to update normalized_url automatically
CREATE OR REPLACE FUNCTION normalize_url()
RETURNS TRIGGER AS $$
BEGIN
    -- Remove common query parameters and normalize URL
    NEW.normalized_url := regexp_replace(
        regexp_replace(
            split_part(NEW.url, '?', 1),
            'https?://',
            ''
        ),
        '/$',
        ''
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER pages_normalize_url
    BEFORE INSERT OR UPDATE ON pages
    FOR EACH ROW
    EXECUTE FUNCTION normalize_url();

-- 9. View for duplicate analysis
CREATE OR REPLACE VIEW duplicate_analysis AS
SELECT 
    p1.company_id,
    p1.url as original_url,
    p2.url as duplicate_url,
    p1.content_checksum,
    p1.captured_at as original_captured,
    p2.captured_at as duplicate_captured,
    p2.captured_at - p1.captured_at as time_difference
FROM pages p1
JOIN pages p2 ON p1.content_checksum = p2.content_checksum
    AND p1.company_id = p2.company_id
    AND p1.id < p2.id
ORDER BY p1.captured_at DESC;

-- 10. View for field mapping overview
CREATE OR REPLACE VIEW field_mapping_overview AS
SELECT 
    c.name as company_name,
    fm.semantic_type,
    COUNT(DISTINCT fm.id) as total_fields,
    COUNT(DISTINCT fm.page_url) as pages_with_field,
    AVG(fm.confidence) as avg_confidence,
    MIN(fm.confidence) as min_confidence,
    MAX(fm.confidence) as max_confidence,
    COUNT(DISTINCT fm.form_id) as unique_forms
FROM field_mappings fm
JOIN companies c ON fm.company_id = c.id
GROUP BY c.name, fm.semantic_type
ORDER BY c.name, total_fields DESC;

-- Grant permissions (adjust based on your needs)
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO authenticated;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Database schema with field mapping and duplicate prevention created successfully!';
    RAISE NOTICE 'Tables created:';
    RAISE NOTICE '  - field_mappings: Stores identified fields and their semantic types';
    RAISE NOTICE '  - field_mapping_patterns: Pattern matching rules';
    RAISE NOTICE '  - field_value_examples: Example values for fields';
    RAISE NOTICE '  - duplicate_prevention_log: Tracks prevented duplicates';
    RAISE NOTICE 'Functions created:';
    RAISE NOTICE '  - check_page_duplicate(): Check if a page is duplicate';
    RAISE NOTICE '  - get_field_mapping_stats(): Get field statistics';
    RAISE NOTICE 'Views created:';
    RAISE NOTICE '  - duplicate_analysis: Analyze duplicate pages';
    RAISE NOTICE '  - field_mapping_overview: Overview of field mappings';
END $$;
