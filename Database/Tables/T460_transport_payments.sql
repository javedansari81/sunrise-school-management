-- =====================================================
-- Table: transport_payments
-- Description: Records transport fee payment transactions
-- Dependencies: student_transport_enrollment, students, payment_methods
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS transport_payments CASCADE;

-- Create table
CREATE TABLE transport_payments (
    id SERIAL PRIMARY KEY,
    enrollment_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,

    -- Payment Details
    amount DECIMAL(10,2) NOT NULL,
    payment_method_id INTEGER NOT NULL,
    payment_date DATE NOT NULL,
    transaction_id VARCHAR(100),

    -- Reversal tracking columns (from V012)
    is_reversal BOOLEAN DEFAULT FALSE NOT NULL,
    reverses_payment_id INTEGER,
    reversed_by_payment_id INTEGER,
    reversal_reason_id INTEGER,
    reversal_type VARCHAR(20),

    -- Additional Info
    remarks TEXT,
    receipt_number VARCHAR(50),

    -- Receipt Details (Phase 1: Receipt Generation)
    receipt_url TEXT,
    receipt_cloudinary_public_id VARCHAR(255),
    receipt_generated_at TIMESTAMP WITH TIME ZONE,

    -- Audit
    created_by INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Foreign Key Constraints
    FOREIGN KEY (enrollment_id) REFERENCES student_transport_enrollment(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (payment_method_id) REFERENCES payment_methods(id),
    FOREIGN KEY (reverses_payment_id) REFERENCES transport_payments(id) ON DELETE SET NULL,
    FOREIGN KEY (reversed_by_payment_id) REFERENCES transport_payments(id) ON DELETE SET NULL,
    FOREIGN KEY (reversal_reason_id) REFERENCES reversal_reasons(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Add indexes
CREATE INDEX idx_transport_payments_enrollment ON transport_payments(enrollment_id);
CREATE INDEX idx_transport_payments_student ON transport_payments(student_id);
CREATE INDEX idx_transport_payments_date ON transport_payments(payment_date);
CREATE INDEX IF NOT EXISTS idx_transport_payments_is_reversal ON transport_payments(is_reversal);
CREATE INDEX IF NOT EXISTS idx_transport_payments_reverses_payment_id ON transport_payments(reverses_payment_id);
CREATE INDEX IF NOT EXISTS idx_transport_payments_reversed_by_payment_id ON transport_payments(reversed_by_payment_id);

-- Add comments
COMMENT ON TABLE transport_payments IS 'Transport fee payment transaction records';
COMMENT ON COLUMN transport_payments.enrollment_id IS 'Foreign key to student_transport_enrollment table';
COMMENT ON COLUMN transport_payments.student_id IS 'Foreign key to students table';
COMMENT ON COLUMN transport_payments.amount IS 'Payment amount';
COMMENT ON COLUMN transport_payments.payment_method_id IS 'Foreign key to payment_methods table';
COMMENT ON COLUMN transport_payments.payment_date IS 'Date of payment';
COMMENT ON COLUMN transport_payments.transaction_id IS 'Transaction reference ID';
COMMENT ON COLUMN transport_payments.is_reversal IS 'TRUE if this is a reversal payment (negative amount)';
COMMENT ON COLUMN transport_payments.reverses_payment_id IS 'References the original payment being reversed (for reversal payments)';
COMMENT ON COLUMN transport_payments.reversed_by_payment_id IS 'References the reversal payment (for original payments that have been reversed)';
COMMENT ON COLUMN transport_payments.reversal_reason_id IS 'Foreign key to reversal_reasons table';
COMMENT ON COLUMN transport_payments.reversal_type IS 'Type of reversal: FULL or PARTIAL';
COMMENT ON COLUMN transport_payments.created_by IS 'User who created this payment record';
COMMENT ON COLUMN transport_payments.receipt_number IS 'Receipt number for this payment';
COMMENT ON COLUMN transport_payments.receipt_url IS 'Cloudinary URL for the receipt PDF';
COMMENT ON COLUMN transport_payments.receipt_cloudinary_public_id IS 'Cloudinary public ID for receipt management';
COMMENT ON COLUMN transport_payments.receipt_generated_at IS 'Timestamp when receipt was generated';

