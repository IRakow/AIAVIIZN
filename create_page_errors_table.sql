-- Create page_errors table for error tracking
-- Run this in your Supabase SQL Editor

CREATE TABLE IF NOT EXISTS page_errors (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    url TEXT NOT NULL,
    error TEXT,
    company_id UUID,
    occurred_at TIMESTAMPTZ DEFAULT NOW(),
    resolved BOOLEAN DEFAULT FALSE
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_page_errors_company_url ON page_errors(company_id, url);

-- Create storage bucket for HTML content
-- NOTE: You need to create the storage bucket manually in Supabase Dashboard:
-- 1. Go to Storage section
-- 2. Click "New Bucket"
-- 3. Name: page-content
-- 4. Public: No (keep private)
-- 5. File size limit: 50MB
-- 6. Allowed MIME types: application/gzip, text/html

-- Optional: Grant permissions if needed
GRANT ALL ON page_errors TO authenticated;
GRANT ALL ON page_errors TO service_role;
