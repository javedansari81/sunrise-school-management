-- =====================================================
-- Version: V016
-- Description: Replace UNIQUE constraint with partial unique index on users table
--              to support soft delete (allow reusing emails after soft delete)
-- Date: 2025-01-23
-- Author: System
-- Dependencies: T300_users.sql, V013_add_soft_delete_to_users.sql
-- =====================================================

-- Drop existing unique constraint on email
DO $$ 
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'users_email_key'
    ) THEN
        ALTER TABLE users DROP CONSTRAINT users_email_key;
        RAISE NOTICE '✅ Dropped constraint: users_email_key';
    ELSE
        RAISE NOTICE 'ℹ️ Constraint users_email_key does not exist (already dropped)';
    END IF;
END $$;

-- Create partial unique index on email (only for non-deleted records)
CREATE UNIQUE INDEX IF NOT EXISTS users_email_active_unique
ON users (email)
WHERE (is_deleted = FALSE OR is_deleted IS NULL);

-- Verification
DO $$
DECLARE
    index_exists BOOLEAN;
    constraint_exists BOOLEAN;
BEGIN
    -- Check if index exists
    SELECT EXISTS (
        SELECT 1 
        FROM pg_indexes 
        WHERE tablename = 'users' 
        AND indexname = 'users_email_active_unique'
    ) INTO index_exists;
    
    -- Check if old constraint still exists (should not)
    SELECT EXISTS (
        SELECT 1 
        FROM pg_constraint 
        WHERE conname = 'users_email_key'
    ) INTO constraint_exists;
    
    -- Report results
    IF index_exists THEN
        RAISE NOTICE '✅ Verification: users_email_active_unique exists';
    ELSE
        RAISE WARNING '❌ Verification failed: users_email_active_unique not found';
    END IF;
    
    IF NOT constraint_exists THEN
        RAISE NOTICE '✅ Verification: Old constraint users_email_key removed';
    ELSE
        RAISE WARNING '⚠️ Warning: Old constraint users_email_key still exists';
    END IF;
END $$;

-- Add comment
COMMENT ON INDEX users_email_active_unique IS 'Partial unique index: ensures email is unique only for non-deleted users';

