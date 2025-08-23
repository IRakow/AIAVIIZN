-- =====================================================
-- SUPABASE STORAGE BUCKET SETUP
-- =====================================================
-- Run this AFTER the main database setup
-- This creates the storage bucket for HTML content

-- Note: Storage buckets must be created via Supabase Dashboard
-- These are the SQL policies for the bucket after creation

-- 1. First create the bucket in Supabase Dashboard:
--    Go to: Storage → New Bucket
--    Name: page-content
--    Public: No (keep private)
--    File size limit: 50MB
--    Allowed MIME types: application/gzip, text/html, application/json

-- 2. Then run these policies for access control:

-- Allow service role to upload/read/delete
INSERT INTO storage.policies (name, bucket_id, operation, definition)
VALUES 
    ('Service role can upload to page-content', 'page-content', 'INSERT', 
     '{"role": "service_role"}'::jsonb),
    ('Service role can read from page-content', 'page-content', 'SELECT',
     '{"role": "service_role"}'::jsonb),
    ('Service role can update in page-content', 'page-content', 'UPDATE',
     '{"role": "service_role"}'::jsonb),
    ('Service role can delete from page-content', 'page-content', 'DELETE',
     '{"role": "service_role"}'::jsonb)
ON CONFLICT (bucket_id, name) DO NOTHING;

-- 3. Verify bucket exists
SELECT * FROM storage.buckets WHERE id = 'page-content';

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ Storage Bucket Configuration Complete!';
    RAISE NOTICE '   Remember to create the bucket in the Dashboard first:';
    RAISE NOTICE '   1. Go to Storage section';
    RAISE NOTICE '   2. Click New Bucket';
    RAISE NOTICE '   3. Name: page-content';
    RAISE NOTICE '   4. Keep it private';
    RAISE NOTICE '   5. Set 50MB file limit';
END $$;
