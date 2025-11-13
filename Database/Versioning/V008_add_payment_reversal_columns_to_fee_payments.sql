-- =====================================================
-- Migration: V008 - Add Payment Reversal Columns to fee_payments
-- Description: Adds columns to support payment reversal functionality
-- Date: 2025-01-12
-- Dependencies: fee_payments, users
-- =====================================================

-- Add new columns to fee_payments table
ALTER TABLE fee_payments 
ADD COLUMN IF NOT EXISTS is_reversal BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS reverses_payment_id INTEGER,
ADD COLUMN IF NOT EXISTS reversed_by_payment_id INTEGER,
ADD COLUMN IF NOT EXISTS reversal_reason TEXT,
ADD COLUMN IF NOT EXISTS reversal_type VARCHAR(20),
ADD COLUMN IF NOT EXISTS created_by INTEGER;

-- Add foreign key constraints
ALTER TABLE fee_payments 
ADD CONSTRAINT fk_fee_payments_reverses 
FOREIGN KEY (reverses_payment_id) REFERENCES fee_payments(id) ON DELETE SET NULL;

ALTER TABLE fee_payments 
ADD CONSTRAINT fk_fee_payments_reversed_by 
FOREIGN KEY (reversed_by_payment_id) REFERENCES fee_payments(id) ON DELETE SET NULL;

ALTER TABLE fee_payments 
ADD CONSTRAINT fk_fee_payments_created_by 
FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL;

-- Add check constraint for reversal_type
ALTER TABLE fee_payments 
ADD CONSTRAINT chk_fee_payments_reversal_type 
CHECK (reversal_type IS NULL OR reversal_type IN ('FULL', 'PARTIAL'));

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_fee_payments_is_reversal ON fee_payments(is_reversal);
CREATE INDEX IF NOT EXISTS idx_fee_payments_reverses_payment_id ON fee_payments(reverses_payment_id);
CREATE INDEX IF NOT EXISTS idx_fee_payments_reversed_by_payment_id ON fee_payments(reversed_by_payment_id);
CREATE INDEX IF NOT EXISTS idx_fee_payments_created_by ON fee_payments(created_by);

-- Add comments
COMMENT ON COLUMN fee_payments.is_reversal IS 'TRUE if this is a reversal payment (negative amount)';
COMMENT ON COLUMN fee_payments.reverses_payment_id IS 'ID of the payment being reversed (for reversal payments)';
COMMENT ON COLUMN fee_payments.reversed_by_payment_id IS 'ID of the reversal payment (for original payments that have been reversed)';
COMMENT ON COLUMN fee_payments.reversal_reason IS 'Reason for the reversal (required for reversal payments)';
COMMENT ON COLUMN fee_payments.reversal_type IS 'Type of reversal: FULL (entire payment) or PARTIAL (specific months only)';
COMMENT ON COLUMN fee_payments.created_by IS 'User who created this payment record';

-- Add validation constraint: reversal payments must have reversal_reason
ALTER TABLE fee_payments 
ADD CONSTRAINT chk_fee_payments_reversal_reason 
CHECK (
    (is_reversal = FALSE) OR 
    (is_reversal = TRUE AND reversal_reason IS NOT NULL AND LENGTH(TRIM(reversal_reason)) > 0)
);

-- Add validation constraint: reversal payments must have reverses_payment_id
ALTER TABLE fee_payments 
ADD CONSTRAINT chk_fee_payments_reversal_link 
CHECK (
    (is_reversal = FALSE) OR 
    (is_reversal = TRUE AND reverses_payment_id IS NOT NULL)
);

-- Add validation constraint: reversal payments must have reversal_type
ALTER TABLE fee_payments 
ADD CONSTRAINT chk_fee_payments_reversal_type_required 
CHECK (
    (is_reversal = FALSE) OR 
    (is_reversal = TRUE AND reversal_type IS NOT NULL)
);

-- Add validation constraint: non-reversal payments should not have reverses_payment_id
ALTER TABLE fee_payments 
ADD CONSTRAINT chk_fee_payments_non_reversal_no_link 
CHECK (
    (is_reversal = TRUE) OR 
    (is_reversal = FALSE AND reverses_payment_id IS NULL AND reversal_type IS NULL)
);

