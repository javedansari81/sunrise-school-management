-- =====================================================
-- Migration: V003_sync_fee_structures_schema.sql
-- Description: Sync fee_structures table schema with SQLAlchemy model
-- Date: 2025-10-10
-- =====================================================
-- This migration updates the fee_structures table to match the SQLAlchemy model
-- which expects individual fee component columns instead of generic fee_type/amount

BEGIN;

-- =====================================================
-- Step 1: Backup existing data (if any)
-- =====================================================
-- Create temporary table to backup existing data
CREATE TEMP TABLE fee_structures_backup AS 
SELECT * FROM fee_structures;

-- =====================================================
-- Step 2: Drop and recreate table with new schema
-- =====================================================
-- Drop existing table
DROP TABLE IF EXISTS fee_structures CASCADE;

-- Create table with new schema matching SQLAlchemy model
CREATE TABLE fee_structures (
    id SERIAL PRIMARY KEY,
    
    -- Foreign keys to metadata tables
    class_id INTEGER NOT NULL,
    session_year_id INTEGER NOT NULL,
    
    -- Fee Components (matching SQLAlchemy model)
    tuition_fee DECIMAL(10,2) DEFAULT 0.0,
    admission_fee DECIMAL(10,2) DEFAULT 0.0,
    development_fee DECIMAL(10,2) DEFAULT 0.0,
    activity_fee DECIMAL(10,2) DEFAULT 0.0,
    transport_fee DECIMAL(10,2) DEFAULT 0.0,
    library_fee DECIMAL(10,2) DEFAULT 0.0,
    lab_fee DECIMAL(10,2) DEFAULT 0.0,
    exam_fee DECIMAL(10,2) DEFAULT 0.0,
    other_fee DECIMAL(10,2) DEFAULT 0.0,
    
    -- Total (required field)
    total_annual_fee DECIMAL(10,2) NOT NULL DEFAULT 0.0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    
    -- Foreign Key Constraints
    FOREIGN KEY (class_id) REFERENCES classes(id),
    FOREIGN KEY (session_year_id) REFERENCES session_years(id)
);

-- =====================================================
-- Step 3: Add indexes for performance
-- =====================================================
CREATE INDEX idx_fee_structures_class_session ON fee_structures(class_id, session_year_id);
CREATE INDEX idx_fee_structures_class_id ON fee_structures(class_id);
CREATE INDEX idx_fee_structures_session_year_id ON fee_structures(session_year_id);

-- =====================================================
-- Step 4: Add comments
-- =====================================================
COMMENT ON TABLE fee_structures IS 'Fee structure definitions by class and session with detailed fee components';
COMMENT ON COLUMN fee_structures.class_id IS 'Foreign key to classes table';
COMMENT ON COLUMN fee_structures.session_year_id IS 'Foreign key to session_years table';
COMMENT ON COLUMN fee_structures.tuition_fee IS 'Tuition fee amount';
COMMENT ON COLUMN fee_structures.admission_fee IS 'Admission fee amount';
COMMENT ON COLUMN fee_structures.development_fee IS 'Development fee amount';
COMMENT ON COLUMN fee_structures.activity_fee IS 'Activity fee amount';
COMMENT ON COLUMN fee_structures.transport_fee IS 'Transport fee amount';
COMMENT ON COLUMN fee_structures.library_fee IS 'Library fee amount';
COMMENT ON COLUMN fee_structures.lab_fee IS 'Lab fee amount';
COMMENT ON COLUMN fee_structures.exam_fee IS 'Exam fee amount';
COMMENT ON COLUMN fee_structures.other_fee IS 'Other miscellaneous fees';
COMMENT ON COLUMN fee_structures.total_annual_fee IS 'Total annual fee (sum of all components)';

-- =====================================================
-- Step 5: Insert sample data for testing
-- =====================================================
-- Insert sample fee structures for different classes and current session (2025-26)
INSERT INTO fee_structures (
    class_id, 
    session_year_id, 
    tuition_fee, 
    admission_fee, 
    development_fee, 
    activity_fee, 
    transport_fee, 
    library_fee, 
    lab_fee, 
    exam_fee, 
    other_fee, 
    total_annual_fee
) VALUES 
-- Class 7 (CLASS_7) for session 2025-26
(
    (SELECT id FROM classes WHERE name = 'CLASS_7' LIMIT 1),
    (SELECT id FROM session_years WHERE name = '2025-26' LIMIT 1),
    8000.00,  -- tuition_fee
    1000.00,  -- admission_fee
    500.00,   -- development_fee
    300.00,   -- activity_fee
    1200.00,  -- transport_fee
    200.00,   -- library_fee
    300.00,   -- lab_fee
    400.00,   -- exam_fee
    100.00,   -- other_fee
    12000.00  -- total_annual_fee
),
-- Class 8 (CLASS_8) for session 2025-26
(
    (SELECT id FROM classes WHERE name = 'CLASS_8' LIMIT 1),
    (SELECT id FROM session_years WHERE name = '2025-26' LIMIT 1),
    8500.00,  -- tuition_fee
    1000.00,  -- admission_fee
    500.00,   -- development_fee
    300.00,   -- activity_fee
    1200.00,  -- transport_fee
    200.00,   -- library_fee
    400.00,   -- lab_fee
    500.00,   -- exam_fee
    100.00,   -- other_fee
    12700.00  -- total_annual_fee
),
-- Class 9 (CLASS_9) for session 2025-26
(
    (SELECT id FROM classes WHERE name = 'CLASS_9' LIMIT 1),
    (SELECT id FROM session_years WHERE name = '2025-26' LIMIT 1),
    9000.00,  -- tuition_fee
    1000.00,  -- admission_fee
    600.00,   -- development_fee
    400.00,   -- activity_fee
    1200.00,  -- transport_fee
    250.00,   -- library_fee
    500.00,   -- lab_fee
    600.00,   -- exam_fee
    150.00,   -- other_fee
    13700.00  -- total_annual_fee
),
-- Class 10 (CLASS_10) for session 2025-26
(
    (SELECT id FROM classes WHERE name = 'CLASS_10' LIMIT 1),
    (SELECT id FROM session_years WHERE name = '2025-26' LIMIT 1),
    10000.00, -- tuition_fee
    1000.00,  -- admission_fee
    700.00,   -- development_fee
    500.00,   -- activity_fee
    1200.00,  -- transport_fee
    300.00,   -- library_fee
    600.00,   -- lab_fee
    700.00,   -- exam_fee
    200.00,   -- other_fee
    15200.00  -- total_annual_fee
);

-- =====================================================
-- Step 6: Verification
-- =====================================================
-- Verify the new table structure
DO $$
DECLARE
    column_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO column_count
    FROM information_schema.columns 
    WHERE table_schema = 'sunrise'
    AND table_name = 'fee_structures'
    AND column_name IN ('tuition_fee', 'admission_fee', 'development_fee', 'activity_fee', 
                       'transport_fee', 'library_fee', 'lab_fee', 'exam_fee', 'other_fee', 'total_annual_fee');
    
    IF column_count = 10 THEN
        RAISE NOTICE 'SUCCESS: All 10 fee component columns added to fee_structures table';
    ELSE
        RAISE EXCEPTION 'ERROR: Expected 10 fee component columns, found %', column_count;
    END IF;
END $$;

COMMIT;

-- =====================================================
-- Success Message (using RAISE NOTICE for asyncpg compatibility)
-- =====================================================
DO $$
BEGIN
    RAISE NOTICE '==========================================';
    RAISE NOTICE 'MIGRATION V003 COMPLETED SUCCESSFULLY!';
    RAISE NOTICE '==========================================';
    RAISE NOTICE 'Changes made:';
    RAISE NOTICE '1. Recreated fee_structures table with detailed fee components';
    RAISE NOTICE '2. Added 10 fee component columns matching SQLAlchemy model';
    RAISE NOTICE '3. Added sample fee structures for classes 7-10';
    RAISE NOTICE '4. Added proper indexes and constraints';
    RAISE NOTICE '5. Added comprehensive comments';
    RAISE NOTICE '';
    RAISE NOTICE 'The fee_structures table now matches the SQLAlchemy model!';
    RAISE NOTICE '==========================================';
END $$;
