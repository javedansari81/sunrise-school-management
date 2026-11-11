-- =====================================================
-- Table: payments
-- Description: Money received (kind PAYMENT) or given back (kind REVERSAL,
--              negative amount, pointing at the payment it reverses). The part
--              of a payment not allocated to dues is the student's credit.
-- Dependencies: students, session_years, payment_methods, reversal_reasons, users
-- =====================================================

DROP TABLE IF EXISTS payments CASCADE;

CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id),
    student_id INTEGER NOT NULL REFERENCES students(id),
    session_year_id INTEGER NOT NULL REFERENCES session_years(id),
    kind VARCHAR(10) NOT NULL DEFAULT 'PAYMENT' CHECK (kind IN ('PAYMENT', 'REVERSAL')),
    receipt_number VARCHAR(40),
    amount DECIMAL(10,2) NOT NULL,
    payment_method_id INTEGER REFERENCES payment_methods(id),
    payment_date DATE NOT NULL DEFAULT CURRENT_DATE,
    transaction_id VARCHAR(100),
    remarks TEXT,

    -- Reversal
    reverses_payment_id INTEGER REFERENCES payments(id),
    reversal_reason_id INTEGER REFERENCES reversal_reasons(id),

    -- Receipt document
    receipt_url TEXT,
    receipt_cloudinary_id TEXT,

    -- Online gateway (decision 11: not used yet)
    gateway_name VARCHAR(30),
    gateway_order_id VARCHAR(100),
    gateway_payment_id VARCHAR(100),
    gateway_status VARCHAR(30),

    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT payments_receipt_unique UNIQUE (school_id, receipt_number),
    CONSTRAINT payments_kind_shape CHECK (
        (kind = 'PAYMENT' AND amount > 0 AND reverses_payment_id IS NULL AND payment_method_id IS NOT NULL)
        OR (kind = 'REVERSAL' AND amount < 0 AND reverses_payment_id IS NOT NULL AND reversal_reason_id IS NOT NULL)
    )
);

CREATE INDEX idx_payments_school_id ON payments (school_id);
CREATE INDEX idx_payments_student ON payments (student_id, session_year_id);
CREATE INDEX idx_payments_date ON payments (school_id, payment_date);
CREATE INDEX idx_payments_reverses ON payments (reverses_payment_id) WHERE reverses_payment_id IS NOT NULL;

COMMENT ON TABLE payments IS 'Payments and reversals (unified fee module)';
COMMENT ON COLUMN payments.receipt_number IS 'Per school and session, e.g. SUN/2026-27/000123; NULL for reversals';
COMMENT ON COLUMN payments.school_id IS 'School (tenant) this row belongs to';
