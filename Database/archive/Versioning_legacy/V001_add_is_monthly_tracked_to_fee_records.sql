-- =====================================================
-- Migration: V001_add_is_monthly_tracked_to_fee_records
-- Description: Add is_monthly_tracked column to fee_records table
-- Date: 2025-01-10
-- Author: System Migration
-- =====================================================

-- Add is_monthly_tracked column to fee_records table
DO $$
BEGIN
    -- Check if column already exists
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'fee_records' 
        AND column_name = 'is_monthly_tracked'
    ) THEN
        -- Add the column
        ALTER TABLE fee_records 
        ADD COLUMN is_monthly_tracked BOOLEAN DEFAULT FALSE;
        
        -- Add comment
        COMMENT ON COLUMN fee_records.is_monthly_tracked IS 'Whether this fee record uses monthly tracking system';
        
        -- Create index for better performance
        CREATE INDEX IF NOT EXISTS idx_fee_records_monthly_tracked 
        ON fee_records(is_monthly_tracked) 
        WHERE is_monthly_tracked = TRUE;
        
        RAISE NOTICE 'Added is_monthly_tracked column to fee_records table';
    ELSE
        RAISE NOTICE 'Column is_monthly_tracked already exists in fee_records table';
    END IF;
END $$;

-- Update existing records that have monthly_fee_tracking entries to set is_monthly_tracked = TRUE
DO $$
DECLARE
    v_count INTEGER;
BEGIN
    UPDATE fee_records
    SET is_monthly_tracked = TRUE,
        updated_at = NOW()
    WHERE id IN (
        SELECT DISTINCT fee_record_id
        FROM monthly_fee_tracking
        WHERE fee_record_id IS NOT NULL
    );

    GET DIAGNOSTICS v_count = ROW_COUNT;
    RAISE NOTICE 'Updated % existing fee records to enable monthly tracking', v_count;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error updating existing records: %', SQLERRM;
END $$;
