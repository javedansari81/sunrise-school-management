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

    -- Reversal tracking columns (from V008 and V011)
    is_reversal BOOLEAN DEFAULT FALSE,
    reverses_payment_id INTEGER,
    reversed_by_payment_id INTEGER,
    reversal_reason_id INTEGER,
    reversal_type VARCHAR(20),

    -- Additional Info
    remarks TEXT,
    receipt_number VARCHAR(50),

    -- Receipt Details (Phase 1: Receipt Generation)
    receipt_cloudinary_url TEXT,
    receipt_cloudinary_id VARCHAR(255),

    -- Audit
    created_by INTEGER,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Foreign Keys
    FOREIGN KEY (fee_record_id) REFERENCES fee_records(id) ON DELETE CASCADE,
    FOREIGN KEY (payment_method_id) REFERENCES payment_methods(id),
    FOREIGN KEY (reverses_payment_id) REFERENCES fee_payments(id) ON DELETE SET NULL,
    FOREIGN KEY (reversed_by_payment_id) REFERENCES fee_payments(id) ON DELETE SET NULL,
    FOREIGN KEY (reversal_reason_id) REFERENCES reversal_reasons(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,

    -- Check constraints for reversal logic
    CHECK (reversal_type IS NULL OR reversal_type IN ('FULL', 'PARTIAL')),
    CHECK (
        (is_reversal = FALSE) OR
        (is_reversal = TRUE AND reversal_reason_id IS NOT NULL)
    ),
    CHECK (
        (is_reversal = FALSE) OR
        (is_reversal = TRUE AND reverses_payment_id IS NOT NULL)
    ),
    CHECK (
        (is_reversal = FALSE) OR
        (is_reversal = TRUE AND reversal_type IS NOT NULL)
    ),
    CHECK (
        (is_reversal = TRUE) OR
        (is_reversal = FALSE AND reverses_payment_id IS NULL AND reversal_type IS NULL)
    )
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_fee_payments_fee_record ON fee_payments(fee_record_id);
CREATE INDEX IF NOT EXISTS idx_fee_payments_payment_date ON fee_payments(payment_date);
CREATE INDEX IF NOT EXISTS idx_fee_payments_is_reversal ON fee_payments(is_reversal);
CREATE INDEX IF NOT EXISTS idx_fee_payments_reverses_payment_id ON fee_payments(reverses_payment_id);
CREATE INDEX IF NOT EXISTS idx_fee_payments_reversed_by_payment_id ON fee_payments(reversed_by_payment_id);
CREATE INDEX IF NOT EXISTS idx_fee_payments_created_by ON fee_payments(created_by);
CREATE INDEX IF NOT EXISTS idx_fee_payments_reversal_reason_id ON fee_payments(reversal_reason_id);

-- Add comments
COMMENT ON TABLE fee_payments IS 'Individual fee payment transactions';
COMMENT ON COLUMN fee_payments.fee_record_id IS 'Foreign key to fee_records table';
COMMENT ON COLUMN fee_payments.amount IS 'Payment amount';
COMMENT ON COLUMN fee_payments.payment_method_id IS 'Foreign key to payment_methods table';
COMMENT ON COLUMN fee_payments.payment_date IS 'Date when payment was made';
COMMENT ON COLUMN fee_payments.transaction_id IS 'Transaction ID from payment gateway';
COMMENT ON COLUMN fee_payments.is_reversal IS 'TRUE if this is a reversal payment (negative amount)';
COMMENT ON COLUMN fee_payments.reverses_payment_id IS 'ID of the payment being reversed (for reversal payments)';
COMMENT ON COLUMN fee_payments.reversed_by_payment_id IS 'ID of the reversal payment (for original payments that have been reversed)';
COMMENT ON COLUMN fee_payments.reversal_reason_id IS 'Foreign key to reversal_reasons table';
COMMENT ON COLUMN fee_payments.reversal_type IS 'Type of reversal: FULL (entire payment) or PARTIAL (specific months only)';
COMMENT ON COLUMN fee_payments.created_by IS 'User who created this payment record';
COMMENT ON COLUMN fee_payments.receipt_number IS 'Receipt number for this payment';
COMMENT ON COLUMN fee_payments.receipt_cloudinary_url IS 'Cloudinary URL for the receipt PDF';
COMMENT ON COLUMN fee_payments.receipt_cloudinary_id IS 'Cloudinary public ID for receipt management';

