-- =====================================================
-- Migration: V002_sync_fee_records_schema
-- Description: Sync fee_records table schema with SQLAlchemy model
-- Date: 2025-01-10
-- Author: System Migration
-- =====================================================

-- Add missing columns to fee_records table to match SQLAlchemy model
DO $$
BEGIN
    -- Add payment_method_id column
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'sunrise'
        AND table_name = 'fee_records' 
        AND column_name = 'payment_method_id'
    ) THEN
        ALTER TABLE fee_records 
        ADD COLUMN payment_method_id INTEGER;
        
        -- Add foreign key constraint
        ALTER TABLE fee_records 
        ADD CONSTRAINT fk_fee_records_payment_method 
        FOREIGN KEY (payment_method_id) REFERENCES payment_methods(id);
        
        -- Add comment
        COMMENT ON COLUMN fee_records.payment_method_id IS 'Foreign key to payment_methods table';
        
        RAISE NOTICE 'Added payment_method_id column to fee_records table';
    ELSE
        RAISE NOTICE 'Column payment_method_id already exists in fee_records table';
    END IF;

    -- Add fee_structure_id column
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'sunrise'
        AND table_name = 'fee_records' 
        AND column_name = 'fee_structure_id'
    ) THEN
        ALTER TABLE fee_records 
        ADD COLUMN fee_structure_id INTEGER;
        
        -- Add foreign key constraint
        ALTER TABLE fee_records 
        ADD CONSTRAINT fk_fee_records_fee_structure 
        FOREIGN KEY (fee_structure_id) REFERENCES fee_structures(id);
        
        -- Add comment
        COMMENT ON COLUMN fee_records.fee_structure_id IS 'Foreign key to fee_structures table';
        
        RAISE NOTICE 'Added fee_structure_id column to fee_records table';
    ELSE
        RAISE NOTICE 'Column fee_structure_id already exists in fee_records table';
    END IF;

    -- Add academic_month column
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'sunrise'
        AND table_name = 'fee_records' 
        AND column_name = 'academic_month'
    ) THEN
        ALTER TABLE fee_records 
        ADD COLUMN academic_month INTEGER;
        
        -- Add comment
        COMMENT ON COLUMN fee_records.academic_month IS 'Academic month (1-12, where 4=April)';
        
        RAISE NOTICE 'Added academic_month column to fee_records table';
    ELSE
        RAISE NOTICE 'Column academic_month already exists in fee_records table';
    END IF;

    -- Add academic_year column
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'sunrise'
        AND table_name = 'fee_records' 
        AND column_name = 'academic_year'
    ) THEN
        ALTER TABLE fee_records 
        ADD COLUMN academic_year INTEGER;
        
        -- Add comment
        COMMENT ON COLUMN fee_records.academic_year IS 'Academic year (e.g., 2025)';
        
        RAISE NOTICE 'Added academic_year column to fee_records table';
    ELSE
        RAISE NOTICE 'Column academic_year already exists in fee_records table';
    END IF;

    -- Add transaction_id column
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'sunrise'
        AND table_name = 'fee_records' 
        AND column_name = 'transaction_id'
    ) THEN
        ALTER TABLE fee_records 
        ADD COLUMN transaction_id VARCHAR(100);
        
        -- Add comment
        COMMENT ON COLUMN fee_records.transaction_id IS 'Payment transaction ID';
        
        RAISE NOTICE 'Added transaction_id column to fee_records table';
    ELSE
        RAISE NOTICE 'Column transaction_id already exists in fee_records table';
    END IF;

    -- Add payment_date column
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'sunrise'
        AND table_name = 'fee_records' 
        AND column_name = 'payment_date'
    ) THEN
        ALTER TABLE fee_records 
        ADD COLUMN payment_date DATE;
        
        -- Add comment
        COMMENT ON COLUMN fee_records.payment_date IS 'Date of payment';
        
        RAISE NOTICE 'Added payment_date column to fee_records table';
    ELSE
        RAISE NOTICE 'Column payment_date already exists in fee_records table';
    END IF;

    -- Add remarks column
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'sunrise'
        AND table_name = 'fee_records' 
        AND column_name = 'remarks'
    ) THEN
        ALTER TABLE fee_records 
        ADD COLUMN remarks TEXT;
        
        -- Add comment
        COMMENT ON COLUMN fee_records.remarks IS 'Additional remarks or notes';
        
        RAISE NOTICE 'Added remarks column to fee_records table';
    ELSE
        RAISE NOTICE 'Column remarks already exists in fee_records table';
    END IF;

END $$;
