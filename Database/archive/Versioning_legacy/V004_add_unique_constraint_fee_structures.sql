-- =====================================================
-- Migration: V004_add_unique_constraint_fee_structures.sql
-- Description: Add unique constraint on (class_id, session_year_id) to fee_structures table
-- Date: 2025-10-10
-- Dependencies: fee_structures table must exist
-- =====================================================

-- Set search path
SET search_path TO sunrise, public;

-- Start transaction
BEGIN;

-- Check if constraint already exists
DO $$
BEGIN
    -- Add unique constraint if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fee_structures_class_session_unique' 
        AND table_name = 'fee_structures'
        AND table_schema = 'sunrise'
    ) THEN
        -- Remove any duplicate records first (keep the one with the highest ID)
        DELETE FROM fee_structures 
        WHERE id NOT IN (
            SELECT MAX(id) 
            FROM fee_structures 
            GROUP BY class_id, session_year_id
        );
        
        -- Add the unique constraint
        ALTER TABLE fee_structures 
        ADD CONSTRAINT fee_structures_class_session_unique 
        UNIQUE (class_id, session_year_id);
        
        RAISE NOTICE 'Added unique constraint fee_structures_class_session_unique';
    ELSE
        RAISE NOTICE 'Unique constraint fee_structures_class_session_unique already exists';
    END IF;
END $$;

-- Commit transaction
COMMIT;

-- Verify the constraint was added
SELECT 
    constraint_name,
    constraint_type,
    table_name
FROM information_schema.table_constraints 
WHERE table_name = 'fee_structures' 
AND table_schema = 'sunrise'
AND constraint_type = 'UNIQUE';
