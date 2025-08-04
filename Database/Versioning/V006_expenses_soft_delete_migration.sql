-- =====================================================
-- V006: Expenses Soft Delete Migration
-- =====================================================
-- This script adds soft delete functionality to the expenses table
-- Run this script manually in your PostgreSQL database

-- Start transaction for atomic operation
BEGIN;

-- Add soft delete columns to expenses table with proper error handling
DO $$
DECLARE
    column_exists BOOLEAN;
BEGIN
    -- Check and add is_deleted column
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'expenses' 
        AND column_name = 'is_deleted'
    ) INTO column_exists;
    
    IF NOT column_exists THEN
        ALTER TABLE expenses ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE;
        RAISE NOTICE 'Added is_deleted column to expenses table';
    ELSE
        RAISE NOTICE 'is_deleted column already exists in expenses table';
    END IF;

    -- Check and add deleted_date column
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'expenses' 
        AND column_name = 'deleted_date'
    ) INTO column_exists;
    
    IF NOT column_exists THEN
        ALTER TABLE expenses ADD COLUMN deleted_date TIMESTAMP WITH TIME ZONE NULL;
        RAISE NOTICE 'Added deleted_date column to expenses table';
    ELSE
        RAISE NOTICE 'deleted_date column already exists in expenses table';
    END IF;
END
$$;

-- Update existing records to have proper soft delete values
UPDATE expenses 
SET is_deleted = FALSE 
WHERE is_deleted IS NULL;

-- Add NOT NULL constraint to is_deleted after setting default values
ALTER TABLE expenses ALTER COLUMN is_deleted SET NOT NULL;
ALTER TABLE expenses ALTER COLUMN is_deleted SET DEFAULT FALSE;

-- Add column comments for documentation
COMMENT ON COLUMN expenses.is_deleted IS 'Soft delete flag - TRUE if record is deleted, FALSE if active';
COMMENT ON COLUMN expenses.deleted_date IS 'Timestamp when record was soft deleted, NULL if not deleted';

-- Create indexes for optimal query performance
CREATE INDEX IF NOT EXISTS idx_expenses_is_deleted ON expenses(is_deleted);
CREATE INDEX IF NOT EXISTS idx_expenses_deleted_date ON expenses(deleted_date);

-- Create composite index for common active record queries
CREATE INDEX IF NOT EXISTS idx_expenses_active_records ON expenses(id, is_deleted) 
WHERE is_deleted = FALSE;

-- Create composite index for expense list queries (active records with common filters)
CREATE INDEX IF NOT EXISTS idx_expenses_active_status_date ON expenses(is_deleted, expense_status_id, expense_date) 
WHERE is_deleted = FALSE;

-- Create composite index for statistics queries (active records by category and status)
CREATE INDEX IF NOT EXISTS idx_expenses_active_category_status ON expenses(is_deleted, expense_category_id, expense_status_id) 
WHERE is_deleted = FALSE;

-- Verify the migration was successful
DO $$
DECLARE
    is_deleted_exists BOOLEAN;
    deleted_date_exists BOOLEAN;
    total_expenses INTEGER;
    active_expenses INTEGER;
BEGIN
    -- Check if columns exist
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' AND table_name = 'expenses' AND column_name = 'is_deleted'
    ) INTO is_deleted_exists;
    
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' AND table_name = 'expenses' AND column_name = 'deleted_date'
    ) INTO deleted_date_exists;
    
    -- Get record counts
    SELECT COUNT(*) FROM expenses INTO total_expenses;
    SELECT COUNT(*) FROM expenses WHERE is_deleted = FALSE INTO active_expenses;
    
    -- Report results
    RAISE NOTICE '=== MIGRATION VERIFICATION ===';
    RAISE NOTICE 'is_deleted column exists: %', is_deleted_exists;
    RAISE NOTICE 'deleted_date column exists: %', deleted_date_exists;
    RAISE NOTICE 'Total expenses in database: %', total_expenses;
    RAISE NOTICE 'Active expenses (is_deleted = FALSE): %', active_expenses;
    
    IF is_deleted_exists AND deleted_date_exists THEN
        RAISE NOTICE '✅ Migration completed successfully!';
    ELSE
        RAISE EXCEPTION '❌ Migration failed - columns not created properly';
    END IF;
END
$$;

-- Display column information for verification
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default,
    character_maximum_length
FROM information_schema.columns 
WHERE table_schema = 'public' 
  AND table_name = 'expenses' 
  AND column_name IN ('is_deleted', 'deleted_date')
ORDER BY column_name;

-- Display index information
SELECT 
    indexname,
    indexdef
FROM pg_indexes 
WHERE tablename = 'expenses' 
  AND indexname LIKE '%deleted%'
ORDER BY indexname;

-- Commit the transaction
COMMIT;

RAISE NOTICE '=== SOFT DELETE MIGRATION COMPLETED ===';
RAISE NOTICE 'You can now restart your FastAPI application to use the new soft delete functionality.';
RAISE NOTICE 'All existing expense records have been marked as active (is_deleted = FALSE).';
RAISE NOTICE 'Future deletions will set is_deleted = TRUE and deleted_date = NOW().';
