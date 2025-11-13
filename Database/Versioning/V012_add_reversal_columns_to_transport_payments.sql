-- =====================================================
-- Migration: V012_add_reversal_columns_to_transport_payments
-- Description: Add reversal-related columns to transport_payments table
-- Date: 2025-01-13
-- =====================================================

-- Add reversal columns to transport_payments table
ALTER TABLE transport_payments
ADD COLUMN IF NOT EXISTS is_reversal BOOLEAN DEFAULT FALSE NOT NULL,
ADD COLUMN IF NOT EXISTS reverses_payment_id INTEGER,
ADD COLUMN IF NOT EXISTS reversed_by_payment_id INTEGER,
ADD COLUMN IF NOT EXISTS reversal_reason_id INTEGER,
ADD COLUMN IF NOT EXISTS reversal_type VARCHAR(20),
ADD COLUMN IF NOT EXISTS created_by INTEGER;

-- Add foreign key constraints
DO $$
BEGIN
    -- Add FK for reverses_payment_id (self-reference)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_transport_payments_reverses_payment_id'
    ) THEN
        ALTER TABLE transport_payments
        ADD CONSTRAINT fk_transport_payments_reverses_payment_id
        FOREIGN KEY (reverses_payment_id) REFERENCES transport_payments(id) ON DELETE SET NULL;
    END IF;

    -- Add FK for reversed_by_payment_id (self-reference)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_transport_payments_reversed_by_payment_id'
    ) THEN
        ALTER TABLE transport_payments
        ADD CONSTRAINT fk_transport_payments_reversed_by_payment_id
        FOREIGN KEY (reversed_by_payment_id) REFERENCES transport_payments(id) ON DELETE SET NULL;
    END IF;

    -- Add FK for reversal_reason_id
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_transport_payments_reversal_reason_id'
    ) THEN
        ALTER TABLE transport_payments
        ADD CONSTRAINT fk_transport_payments_reversal_reason_id
        FOREIGN KEY (reversal_reason_id) REFERENCES reversal_reasons(id);
    END IF;

    -- Add FK for created_by
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_transport_payments_created_by'
    ) THEN
        ALTER TABLE transport_payments
        ADD CONSTRAINT fk_transport_payments_created_by
        FOREIGN KEY (created_by) REFERENCES users(id);
    END IF;
END $$;

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_transport_payments_is_reversal ON transport_payments(is_reversal);
CREATE INDEX IF NOT EXISTS idx_transport_payments_reverses_payment_id ON transport_payments(reverses_payment_id);
CREATE INDEX IF NOT EXISTS idx_transport_payments_reversed_by_payment_id ON transport_payments(reversed_by_payment_id);

-- Add comments
COMMENT ON COLUMN transport_payments.is_reversal IS 'TRUE if this is a reversal payment (negative amount)';
COMMENT ON COLUMN transport_payments.reverses_payment_id IS 'References the original payment being reversed (for reversal payments)';
COMMENT ON COLUMN transport_payments.reversed_by_payment_id IS 'References the reversal payment (for original payments that have been reversed)';
COMMENT ON COLUMN transport_payments.reversal_reason_id IS 'Foreign key to reversal_reasons table';
COMMENT ON COLUMN transport_payments.reversal_type IS 'Type of reversal: FULL or PARTIAL';
COMMENT ON COLUMN transport_payments.created_by IS 'User who created this payment record';

