-- =====================================================
-- Table: monthly_payment_allocations
-- Description: Stores payment allocations to monthly tracking records
-- Dependencies: monthly_fee_tracking
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS monthly_payment_allocations CASCADE;

-- Create table (matching SQLAlchemy model)
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

