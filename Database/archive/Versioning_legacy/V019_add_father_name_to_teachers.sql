-- =====================================================
-- Version: V019
-- Description: Add father_name column to teachers table
-- Date: 2025-12-07
-- Author: System
-- Dependencies: T320_teachers.sql
-- =====================================================

-- Add father_name column to teachers table if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'sunrise'
        AND table_name = 'teachers'
        AND column_name = 'father_name'
    ) THEN
        ALTER TABLE sunrise.teachers
        ADD COLUMN father_name VARCHAR(200);
        
        RAISE NOTICE '✅ Added column: father_name to teachers table';
    ELSE
        RAISE NOTICE 'ℹ️ Column father_name already exists in teachers table';
    END IF;
END $$;

-- Add comment for the new column
COMMENT ON COLUMN sunrise.teachers.father_name IS 'Father name of the teacher';

-- Verification
DO $$
DECLARE
    column_exists BOOLEAN;
BEGIN
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'sunrise'
        AND table_name = 'teachers'
        AND column_name = 'father_name'
    ) INTO column_exists;
    
    IF column_exists THEN
        RAISE NOTICE '✅ Verification: father_name column exists in teachers table';
    ELSE
        RAISE WARNING '❌ Verification failed: father_name column not found in teachers table';
    END IF;
END $$;

