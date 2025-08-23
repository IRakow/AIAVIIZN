-- DUPLICATE PREVENTION FOR AIVIIZN AGENT
-- Run this in Supabase SQL Editor to prevent duplicate pages

-- 1. Add unique constraint to pages table
-- This prevents duplicate URLs for the same company
ALTER TABLE pages 
ADD CONSTRAINT unique_company_url 
UNIQUE (company_id, url);

-- 2. Add unique constraint to calculations table  
-- This prevents duplicate calculations for the same page
ALTER TABLE calculations
ADD CONSTRAINT unique_company_page_calc
UNIQUE (company_id, page_url, name);

-- 3. Add unique constraint to api_responses
-- This prevents duplicate API responses for the same endpoint
ALTER TABLE api_responses
ADD CONSTRAINT unique_page_endpoint
UNIQUE (page_url, endpoint);

-- 4. Add updated_at column if missing
ALTER TABLE pages 
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();

-- 5. Create index for faster duplicate checks
CREATE INDEX IF NOT EXISTS idx_pages_company_url 
ON pages(company_id, url);

CREATE INDEX IF NOT EXISTS idx_calculations_company_page 
ON calculations(company_id, page_url);

-- 6. Create a function to auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 7. Create trigger to auto-update updated_at
CREATE TRIGGER update_pages_updated_at 
BEFORE UPDATE ON pages 
FOR EACH ROW 
EXECUTE FUNCTION update_updated_at_column();

-- 8. Optional: Create view to see duplicate issues before constraints
CREATE OR REPLACE VIEW duplicate_pages AS
SELECT company_id, url, COUNT(*) as duplicate_count
FROM pages
GROUP BY company_id, url
HAVING COUNT(*) > 1;

-- Check for existing duplicates before applying constraints
SELECT * FROM duplicate_pages;

-- If duplicates exist, clean them up first:
-- DELETE FROM pages WHERE id NOT IN (
--   SELECT MIN(id) FROM pages GROUP BY company_id, url
-- );
