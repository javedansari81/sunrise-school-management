-- =====================================================
-- Table: fee_payments
-- Description: Stores individual fee payment transactions
-- Dependencies: fee_records, payment_methods
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS fee_payments CASCADE;

-- Create table
CREATE TABLE fee_payments (
    id SERIAL PRIMARY KEY,
    fee_record_id INTEGER NOT NULL,
    
    -- Payment Details
    amount DECIMAL(10,2) NOT NULL,
    payment_method_id INTEGER NOT NULL,
    payment_date DATE NOT NULL,
    transaction_id VARCHAR(100),
    
    -- Additional Info
    remarks TEXT,
    receipt_number VARCHAR(50),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Foreign Keys
    FOREIGN KEY (fee_record_id) REFERENCES fee_records(id) ON DELETE CASCADE,
    FOREIGN KEY (payment_method_id) REFERENCES payment_methods(id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_fee_payments_fee_record ON fee_payments(fee_record_id);
CREATE INDEX IF NOT EXISTS idx_fee_payments_payment_date ON fee_payments(payment_date);

-- Add comments
COMMENT ON TABLE fee_payments IS 'Individual fee payment transactions';
COMMENT ON COLUMN fee_payments.fee_record_id IS 'Foreign key to fee_records table';
COMMENT ON COLUMN fee_payments.amount IS 'Payment amount';
COMMENT ON COLUMN fee_payments.payment_method_id IS 'Foreign key to payment_methods table';
COMMENT ON COLUMN fee_payments.payment_date IS 'Date when payment was made';
COMMENT ON COLUMN fee_payments.transaction_id IS 'Transaction ID from payment gateway';
COMMENT ON COLUMN fee_payments.receipt_number IS 'Receipt number for this payment';

