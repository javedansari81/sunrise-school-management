-- =====================================================
-- Migration: V005_sync_monthly_payment_allocations_schema.sql
-- Description: Sync monthly_payment_allocations table schema with SQLAlchemy model
-- Date: 2025-10-10
-- Dependencies: monthly_payment_allocations table must exist
-- =====================================================

-- Set search path
SET search_path TO sunrise, public;

-- Start transaction
BEGIN;

-- Check if the table exists and needs updating
DO $$
BEGIN
    -- Check if fee_payment_id column exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'sunrise' 
        AND table_name = 'monthly_payment_allocations' 
        AND column_name = 'fee_payment_id'
    ) THEN
        RAISE NOTICE 'Updating monthly_payment_allocations table schema...';
        
        -- Drop existing table and recreate with correct schema
        DROP TABLE IF EXISTS monthly_payment_allocations CASCADE;
        
        -- Create table with correct schema (matching SQLAlchemy model)
        CREATE TABLE monthly_payment_allocations (
            id SERIAL PRIMARY KEY,
            fee_payment_id INTEGER NOT NULL,
            monthly_tracking_id INTEGER NOT NULL,
            allocated_amount DECIMAL(10,2) NOT NULL,
            
            -- Metadata
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            created_by INTEGER,
            
            -- Foreign Key Constraints
            FOREIGN KEY (fee_payment_id) REFERENCES fee_payments(id) ON DELETE CASCADE,
            FOREIGN KEY (monthly_tracking_id) REFERENCES monthly_fee_tracking(id) ON DELETE CASCADE,
            FOREIGN KEY (created_by) REFERENCES users(id)
        );
        
        -- Add indexes for performance
        CREATE INDEX idx_monthly_payment_allocations_fee_payment ON monthly_payment_allocations(fee_payment_id);
        CREATE INDEX idx_monthly_payment_allocations_monthly_tracking ON monthly_payment_allocations(monthly_tracking_id);
        
        -- Add comments
        COMMENT ON TABLE monthly_payment_allocations IS 'Payment allocations to monthly tracking records';
        COMMENT ON COLUMN monthly_payment_allocations.fee_payment_id IS 'Foreign key to fee_payments table';
        COMMENT ON COLUMN monthly_payment_allocations.monthly_tracking_id IS 'Foreign key to monthly_fee_tracking table';
        COMMENT ON COLUMN monthly_payment_allocations.allocated_amount IS 'Amount allocated to this month';
        COMMENT ON COLUMN monthly_payment_allocations.created_by IS 'User who created this allocation';
        
        RAISE NOTICE 'monthly_payment_allocations table schema updated successfully';
    ELSE
        RAISE NOTICE 'monthly_payment_allocations table schema is already up to date';
    END IF;
END $$;

-- Commit transaction
COMMIT;

-- Verify the table structure
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_schema = 'sunrise' 
AND table_name = 'monthly_payment_allocations'
ORDER BY ordinal_position;
