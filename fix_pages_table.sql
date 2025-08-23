-- Add missing columns to pages table
ALTER TABLE pages 
ADD COLUMN IF NOT EXISTS calculations JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS api_responses JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS field_mappings JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS field_statistics JSONB DEFAULT '{}'::jsonb;