-- =====================================================
-- Table: payment_allocations
-- Description: Which dues a payment settled. Reversals add negative rows
--              (is_reversal) instead of editing or deleting the original ones.
-- Dependencies: payments, student_dues
-- =====================================================

DROP TABLE IF EXISTS payment_allocations CASCADE;

CREATE TABLE payment_allocations (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id),
    payment_id INTEGER NOT NULL REFERENCES payments(id),
    student_due_id INTEGER NOT NULL REFERENCES student_dues(id),
    amount DECIMAL(10,2) NOT NULL,
    is_reversal BOOLEAN NOT NULL DEFAULT FALSE,
    reversal_payment_id INTEGER REFERENCES payments(id),
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT payment_allocations_sign CHECK (
        (NOT is_reversal AND amount > 0 AND reversal_payment_id IS NULL)
        OR (is_reversal AND amount < 0 AND reversal_payment_id IS NOT NULL)
    )
);

CREATE INDEX idx_payment_allocations_school_id ON payment_allocations (school_id);
CREATE INDEX idx_payment_allocations_payment ON payment_allocations (payment_id);
CREATE INDEX idx_payment_allocations_due ON payment_allocations (student_due_id);

COMMENT ON TABLE payment_allocations IS 'Payment to due allocations (unified fee module)';
COMMENT ON COLUMN payment_allocations.payment_id IS 'The PAYMENT whose money is allocated; reversal rows point at the same original payment';
COMMENT ON COLUMN payment_allocations.reversal_payment_id IS 'Reversal rows: the REVERSAL payment that took the money back';
COMMENT ON COLUMN payment_allocations.school_id IS 'School (tenant) this row belongs to';
