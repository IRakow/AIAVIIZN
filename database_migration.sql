-- MIGRATION SCRIPT: Convert existing single-tenant data to multi-tenant structure
-- Run this AFTER creating the new schema if you have existing data to preserve

-- Create a default company for existing data
INSERT INTO companies (id, name, domain, base_url, subscription_tier)
VALUES (
    '00000000-0000-0000-0000-000000000001'::uuid,
    'Celtic Property Management (Migrated)',
    'celticprop.appfolio.com',
    'https://celticprop.appfolio.com',
    'migrated'
) ON CONFLICT DO NOTHING;

-- Migrate existing pages to captured_pages
INSERT INTO captured_pages (company_id, url, title, html_content, captured_at)
SELECT 
    '00000000-0000-0000-0000-000000000001'::uuid,
    url,
    title,
    content,
    created_at
FROM pages
WHERE EXISTS (SELECT 1 FROM pages LIMIT 1);

-- Migrate existing calculations to company_calculations
INSERT INTO company_calculations (
    company_id,
    name,
    description,
    formula,
    javascript_function,
    created_at
)
SELECT 
    '00000000-0000-0000-0000-000000000001'::uuid,
    name,
    description,
    formula,
    javascript,
    created_at
FROM calculations
WHERE EXISTS (SELECT 1 FROM calculations LIMIT 1);

-- Migrate API responses if they exist
INSERT INTO captured_pages (company_id, url, api_responses, captured_at)
SELECT 
    '00000000-0000-0000-0000-000000000001'::uuid,
    page_url,
    jsonb_build_object(
        'endpoint', endpoint,
        'data', response_data,
        'formulas', extracted_formulas
    ),
    captured_at
FROM api_responses
WHERE EXISTS (SELECT 1 FROM api_responses LIMIT 1)
ON CONFLICT (company_id, url) DO UPDATE
SET api_responses = EXCLUDED.api_responses;

-- Message
DO $$
DECLARE
    pages_count INTEGER;
    calc_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO pages_count FROM pages;
    SELECT COUNT(*) INTO calc_count FROM calculations;
    
    IF pages_count > 0 OR calc_count > 0 THEN
        RAISE NOTICE 'Migration complete! Migrated % pages and % calculations', pages_count, calc_count;
        RAISE NOTICE 'Old data preserved under company: Celtic Property Management (Migrated)';
    ELSE
        RAISE NOTICE 'No existing data to migrate';
    END IF;
END $$;
