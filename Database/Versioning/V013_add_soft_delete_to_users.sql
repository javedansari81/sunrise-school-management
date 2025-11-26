-- =====================================================
-- Version: V013
-- Description: Add soft delete columns to users table
-- Date: 2025-01-23
-- Author: System
-- Dependencies: T300_users.sql
-- =====================================================

-- Add is_deleted column
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;

-- Add deleted_date column
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS deleted_date TIMESTAMP WITH TIME ZONE;

-- Create index on is_deleted for better query performance
CREATE INDEX IF NOT EXISTS idx_users_is_deleted ON users (is_deleted);

-- Add comments
COMMENT ON COLUMN users.is_deleted IS 'Soft delete flag - marks user as permanently deleted';
COMMENT ON COLUMN users.deleted_date IS 'Timestamp when user was soft deleted';

-- Verification
DO $$
DECLARE
    is_deleted_exists BOOLEAN;
    deleted_date_exists BOOLEAN;
    index_exists BOOLEAN;
BEGIN
    -- Check if is_deleted column exists
    SELECT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'users' 
        AND column_name = 'is_deleted'
    ) INTO is_deleted_exists;
    
    -- Check if deleted_date column exists
    SELECT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'users' 
        AND column_name = 'deleted_date'
    ) INTO deleted_date_exists;
    
    -- Check if index exists
    SELECT EXISTS (
        SELECT 1 
        FROM pg_indexes 
        WHERE tablename = 'users' 
        AND indexname = 'idx_users_is_deleted'
    ) INTO index_exists;
    
    -- Report results
    IF is_deleted_exists THEN
        RAISE NOTICE '✅ Column users.is_deleted created successfully';
    ELSE
        RAISE WARNING '❌ Column users.is_deleted was not created';
    END IF;
    
    IF deleted_date_exists THEN
        RAISE NOTICE '✅ Column users.deleted_date created successfully';
    ELSE
        RAISE WARNING '❌ Column users.deleted_date was not created';
    END IF;
    
    IF index_exists THEN
        RAISE NOTICE '✅ Index idx_users_is_deleted created successfully';
    ELSE
        RAISE WARNING '❌ Index idx_users_is_deleted was not created';
    END IF;
END $$;

