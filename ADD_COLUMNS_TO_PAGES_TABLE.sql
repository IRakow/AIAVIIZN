-- SQL to add missing columns to pages table in Supabase
-- Run this in your Supabase SQL editor at:
-- https://supabase.com/dashboard/project/sejebqdhcilwcpjpznep/sql/new

-- Add the missing columns
ALTER TABLE pages 
ADD COLUMN IF NOT EXISTS calculations JSONB DEFAULT '[]'::jsonb;

ALTER TABLE pages 
ADD COLUMN IF NOT EXISTS api_responses JSONB DEFAULT '[]'::jsonb;

ALTER TABLE pages 
ADD COLUMN IF NOT EXISTS field_mappings JSONB DEFAULT '[]'::jsonb;

ALTER TABLE pages 
ADD COLUMN IF NOT EXISTS field_statistics JSONB DEFAULT '{}'::jsonb;

-- Verify columns were added
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'pages' 
AND column_name IN ('calculations', 'api_responses', 'field_mappings', 'field_statistics');
