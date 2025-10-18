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
    
    -- Additional Info
    remarks TEXT,
    receipt_number VARCHAR(50),
    
    -- Audit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Foreign Key Constraints
    FOREIGN KEY (enrollment_id) REFERENCES student_transport_enrollment(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (payment_method_id) REFERENCES payment_methods(id)
);

-- Add indexes
CREATE INDEX idx_transport_payments_enrollment ON transport_payments(enrollment_id);
CREATE INDEX idx_transport_payments_student ON transport_payments(student_id);
CREATE INDEX idx_transport_payments_date ON transport_payments(payment_date);

-- Add comments
COMMENT ON TABLE transport_payments IS 'Transport fee payment transaction records';
COMMENT ON COLUMN transport_payments.enrollment_id IS 'Foreign key to student_transport_enrollment table';
COMMENT ON COLUMN transport_payments.student_id IS 'Foreign key to students table';
COMMENT ON COLUMN transport_payments.amount IS 'Payment amount';
COMMENT ON COLUMN transport_payments.payment_method_id IS 'Foreign key to payment_methods table';
COMMENT ON COLUMN transport_payments.payment_date IS 'Date of payment';
COMMENT ON COLUMN transport_payments.transaction_id IS 'Transaction reference ID';
COMMENT ON COLUMN transport_payments.receipt_number IS 'Receipt number for this payment';

