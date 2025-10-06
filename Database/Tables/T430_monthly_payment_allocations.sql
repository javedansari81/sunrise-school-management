-- =====================================================
-- Table: monthly_payment_allocations
-- Description: Stores payment allocations to monthly tracking records
-- Dependencies: monthly_fee_tracking
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS monthly_payment_allocations CASCADE;

-- Create table
CREATE TABLE monthly_payment_allocations (
    id SERIAL PRIMARY KEY,
    payment_id INTEGER NOT NULL,
    monthly_tracking_id INTEGER NOT NULL,
    allocated_amount DECIMAL(10,2) NOT NULL,
    allocation_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (monthly_tracking_id) REFERENCES monthly_fee_tracking(id)
);

-- Add comments
COMMENT ON TABLE monthly_payment_allocations IS 'Payment allocations to monthly tracking records';
COMMENT ON COLUMN monthly_payment_allocations.payment_id IS 'Reference to payment transaction';
COMMENT ON COLUMN monthly_payment_allocations.monthly_tracking_id IS 'Foreign key to monthly_fee_tracking table';
COMMENT ON COLUMN monthly_payment_allocations.allocated_amount IS 'Amount allocated to this month';

