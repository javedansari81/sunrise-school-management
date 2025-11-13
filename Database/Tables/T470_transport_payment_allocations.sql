-- =====================================================
-- Table: transport_payment_allocations
-- Description: Tracks month-wise allocation of transport payments with reversal support
-- Dependencies: transport_payments, transport_monthly_tracking, users
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS transport_payment_allocations CASCADE;

-- Create table
CREATE TABLE transport_payment_allocations (
    id SERIAL PRIMARY KEY,
    transport_payment_id INTEGER NOT NULL,
    monthly_tracking_id INTEGER NOT NULL,
    allocated_amount DECIMAL(10,2) NOT NULL,
    
    -- Reversal Fields
    is_reversal BOOLEAN DEFAULT FALSE NOT NULL,
    reverses_allocation_id INTEGER,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by INTEGER,
    
    -- Foreign Key Constraints
    FOREIGN KEY (transport_payment_id) REFERENCES transport_payments(id) ON DELETE CASCADE,
    FOREIGN KEY (monthly_tracking_id) REFERENCES transport_monthly_tracking(id) ON DELETE CASCADE,
    FOREIGN KEY (reverses_allocation_id) REFERENCES transport_payment_allocations(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Create indexes
CREATE INDEX idx_transport_payment_allocations_payment_id ON transport_payment_allocations(transport_payment_id);
CREATE INDEX idx_transport_payment_allocations_monthly_tracking_id ON transport_payment_allocations(monthly_tracking_id);
CREATE INDEX idx_transport_payment_allocations_reverses_allocation_id ON transport_payment_allocations(reverses_allocation_id);

-- Add comments
COMMENT ON TABLE transport_payment_allocations IS 'Month-wise allocation of transport payments with reversal tracking';
COMMENT ON COLUMN transport_payment_allocations.transport_payment_id IS 'Foreign key to transport_payments table';
COMMENT ON COLUMN transport_payment_allocations.monthly_tracking_id IS 'Foreign key to transport_monthly_tracking table';
COMMENT ON COLUMN transport_payment_allocations.allocated_amount IS 'Amount allocated to this month (can be negative for reversals)';
COMMENT ON COLUMN transport_payment_allocations.is_reversal IS 'TRUE if this is a reversal allocation';
COMMENT ON COLUMN transport_payment_allocations.reverses_allocation_id IS 'References the original allocation being reversed (for reversal records)';

