-- =====================================================
-- Version: V015
-- Description: Replace UNIQUE constraints with partial unique indexes on teachers table
--              to support soft delete (allow reusing employee IDs after soft delete)
-- Date: 2025-01-23
-- Author: System
-- Dependencies: T320_teachers.sql
-- =====================================================

-- Drop existing unique constraint on employee_id
DO $$ 
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'teachers_employee_id_key'
    ) THEN
        ALTER TABLE teachers DROP CONSTRAINT teachers_employee_id_key;
        RAISE NOTICE '✅ Dropped constraint: teachers_employee_id_key';
    ELSE
        RAISE NOTICE 'ℹ️ Constraint teachers_employee_id_key does not exist (already dropped)';
    END IF;
END $$;

-- Create partial unique index on employee_id (only for non-deleted records)
CREATE UNIQUE INDEX IF NOT EXISTS teachers_employee_id_active_unique
ON teachers (employee_id)
WHERE (is_deleted = FALSE OR is_deleted IS NULL);

-- Drop existing unique constraint on email (if exists)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'teachers_email_key'
    ) THEN
        ALTER TABLE teachers DROP CONSTRAINT teachers_email_key;
        RAISE NOTICE '✅ Dropped constraint: teachers_email_key';
    ELSE
        RAISE NOTICE 'ℹ️ Constraint teachers_email_key does not exist (already dropped or never existed)';
    END IF;
END $$;

-- Create partial unique index on email (only for non-deleted, non-null records)
CREATE UNIQUE INDEX IF NOT EXISTS teachers_email_active_unique
ON teachers (email)
WHERE (is_deleted = FALSE OR is_deleted IS NULL) AND email IS NOT NULL;

-- Verification
DO $$
DECLARE
    employee_index_exists BOOLEAN;
    email_index_exists BOOLEAN;
BEGIN
    -- Check if employee_id index exists
    SELECT EXISTS (
        SELECT 1 
        FROM pg_indexes 
        WHERE tablename = 'teachers' 
        AND indexname = 'teachers_employee_id_active_unique'
    ) INTO employee_index_exists;
    
    -- Check if email index exists
    SELECT EXISTS (
        SELECT 1 
        FROM pg_indexes 
        WHERE tablename = 'teachers' 
        AND indexname = 'teachers_email_active_unique'
    ) INTO email_index_exists;
    
    -- Report results
    IF employee_index_exists THEN
        RAISE NOTICE '✅ Verification: teachers_employee_id_active_unique exists';
    ELSE
        RAISE WARNING '❌ Verification failed: teachers_employee_id_active_unique not found';
    END IF;
    
    IF email_index_exists THEN
        RAISE NOTICE '✅ Verification: teachers_email_active_unique exists';
    ELSE
        RAISE WARNING '❌ Verification failed: teachers_email_active_unique not found';
    END IF;
END $$;

-- Add comment
COMMENT ON INDEX teachers_employee_id_active_unique IS 'Partial unique index: ensures employee_id is unique only for non-deleted teachers';
COMMENT ON INDEX teachers_email_active_unique IS 'Partial unique index: ensures email is unique only for non-deleted teachers';

