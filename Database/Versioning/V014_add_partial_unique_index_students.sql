-- =====================================================
-- Version: V014
-- Description: Replace UNIQUE constraints with partial unique indexes on students table
--              to support soft delete (allow reusing admission numbers after soft delete)
-- Date: 2025-01-23
-- Author: System
-- Dependencies: T310_students.sql
-- =====================================================

-- Drop existing unique constraint on admission_number
DO $$ 
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'students_admission_number_key'
    ) THEN
        ALTER TABLE students DROP CONSTRAINT students_admission_number_key;
        RAISE NOTICE '✅ Dropped constraint: students_admission_number_key';
    ELSE
        RAISE NOTICE 'ℹ️ Constraint students_admission_number_key does not exist (already dropped)';
    END IF;
END $$;

-- Create partial unique index on admission_number (only for non-deleted records)
CREATE UNIQUE INDEX IF NOT EXISTS students_admission_number_active_unique
ON students (admission_number)
WHERE (is_deleted = FALSE OR is_deleted IS NULL);

-- Drop existing unique constraint on email (if exists)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'students_email_key'
    ) THEN
        ALTER TABLE students DROP CONSTRAINT students_email_key;
        RAISE NOTICE '✅ Dropped constraint: students_email_key';
    ELSE
        RAISE NOTICE 'ℹ️ Constraint students_email_key does not exist (already dropped or never existed)';
    END IF;
END $$;

-- Create partial unique index on email (only for non-deleted, non-null records)
CREATE UNIQUE INDEX IF NOT EXISTS students_email_active_unique
ON students (email)
WHERE (is_deleted = FALSE OR is_deleted IS NULL) AND email IS NOT NULL;

-- Verification
DO $$
DECLARE
    admission_index_exists BOOLEAN;
    email_index_exists BOOLEAN;
BEGIN
    -- Check if admission_number index exists
    SELECT EXISTS (
        SELECT 1 
        FROM pg_indexes 
        WHERE tablename = 'students' 
        AND indexname = 'students_admission_number_active_unique'
    ) INTO admission_index_exists;
    
    -- Check if email index exists
    SELECT EXISTS (
        SELECT 1 
        FROM pg_indexes 
        WHERE tablename = 'students' 
        AND indexname = 'students_email_active_unique'
    ) INTO email_index_exists;
    
    -- Report results
    IF admission_index_exists THEN
        RAISE NOTICE '✅ Verification: students_admission_number_active_unique exists';
    ELSE
        RAISE WARNING '❌ Verification failed: students_admission_number_active_unique not found';
    END IF;
    
    IF email_index_exists THEN
        RAISE NOTICE '✅ Verification: students_email_active_unique exists';
    ELSE
        RAISE WARNING '❌ Verification failed: students_email_active_unique not found';
    END IF;
END $$;

-- Add comment
COMMENT ON INDEX students_admission_number_active_unique IS 'Partial unique index: ensures admission_number is unique only for non-deleted students';
COMMENT ON INDEX students_email_active_unique IS 'Partial unique index: ensures email is unique only for non-deleted students';

