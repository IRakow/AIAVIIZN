-- Fix for missing 'pages' table and 'html_content' column
-- Run this in your Supabase SQL editor at:
-- https://supabase.com/dashboard/project/sejebqdhcilwcpjpznep/sql/new

-- Create the pages table if it doesn't exist
CREATE TABLE IF NOT EXISTS pages (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    title TEXT,
    html_content TEXT,  -- This is the missing column
    main_content TEXT,
    screenshot_path TEXT,
    field_data JSONB DEFAULT '{}'::jsonb,
    calculations JSONB DEFAULT '[]'::jsonb,
    api_responses JSONB DEFAULT '[]'::jsonb,
    field_mappings JSONB DEFAULT '[]'::jsonb,
    field_statistics JSONB DEFAULT '{}'::jsonb,
    captured_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(company_id, url)
);

-- Create index for better performance
CREATE INDEX IF NOT EXISTS idx_pages_company_id ON pages(company_id);
CREATE INDEX IF NOT EXISTS idx_pages_url ON pages(url);

-- Grant appropriate permissions
GRANT ALL ON pages TO authenticated;
GRANT ALL ON pages TO service_role;

-- If the table exists but is missing columns, add them
ALTER TABLE pages 
ADD COLUMN IF NOT EXISTS html_content TEXT;

ALTER TABLE pages 
ADD COLUMN IF NOT EXISTS calculations JSONB DEFAULT '[]'::jsonb;

ALTER TABLE pages 
ADD COLUMN IF NOT EXISTS api_responses JSONB DEFAULT '[]'::jsonb;

ALTER TABLE pages 
ADD COLUMN IF NOT EXISTS field_mappings JSONB DEFAULT '[]'::jsonb;

ALTER TABLE pages 
ADD COLUMN IF NOT EXISTS field_statistics JSONB DEFAULT '{}'::jsonb;

-- Verify the table structure
SELECT 
    column_name, 
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'pages' 
ORDER BY ordinal_position;
