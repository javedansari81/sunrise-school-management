-- =====================================================
-- Table: student_dues
-- Description: One billable line per student, fee head and period. The
--              student's balance is the sum of open dues. A paid or part-paid
--              due is never edited: changes are ADJUSTMENT lines or reversals.
-- Dependencies: students, session_years, fee_heads, student_fee_plans, users
-- =====================================================

DROP TABLE IF EXISTS student_dues CASCADE;

CREATE TABLE student_dues (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id),
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    session_year_id INTEGER NOT NULL REFERENCES session_years(id),
    fee_head_id INTEGER NOT NULL REFERENCES fee_heads(id),
    student_fee_plan_id INTEGER REFERENCES student_fee_plans(id),
    line_type VARCHAR(20) NOT NULL DEFAULT 'REGULAR'
        CHECK (line_type IN ('REGULAR', 'LATE_FEE', 'ADJUSTMENT', 'MANUAL')),
    related_due_id INTEGER REFERENCES student_dues(id),
    period DATE NOT NULL,
    due_date DATE NOT NULL,
    description VARCHAR(255),
    gross_amount DECIMAL(10,2) NOT NULL,
    concession_amount DECIMAL(10,2) NOT NULL DEFAULT 0 CHECK (concession_amount >= 0),
    net_amount DECIMAL(10,2) NOT NULL,
    paid_amount DECIMAL(10,2) NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING'
        CHECK (status IN ('PENDING', 'PARTIAL', 'PAID', 'CANCELLED', 'WAIVED')),
    cancelled_at TIMESTAMP WITH TIME ZONE,
    cancelled_by INTEGER REFERENCES users(id),
    cancel_reason TEXT,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT student_dues_first_of_month CHECK (EXTRACT(DAY FROM period) = 1),
    CONSTRAINT student_dues_net CHECK (net_amount = gross_amount - concession_amount),
    CONSTRAINT student_dues_paid_range CHECK (paid_amount >= 0 AND paid_amount <= GREATEST(net_amount, 0))
);

CREATE INDEX idx_student_dues_school_id ON student_dues (school_id);
CREATE INDEX idx_student_dues_student_session ON student_dues (student_id, session_year_id);
CREATE INDEX idx_student_dues_open ON student_dues (school_id, due_date) WHERE status IN ('PENDING', 'PARTIAL');
-- A regular or late-fee line is generated once per student, head and period
CREATE UNIQUE INDEX student_dues_one_per_period
    ON student_dues (school_id, student_id, fee_head_id, session_year_id, period)
    WHERE line_type IN ('REGULAR', 'LATE_FEE') AND status <> 'CANCELLED';

COMMENT ON TABLE student_dues IS 'Billable lines per student, head and period (unified fee module)';
COMMENT ON COLUMN student_dues.period IS 'Billing month (first day of the month); for quarterly and longer, the first month of the period';
COMMENT ON COLUMN student_dues.related_due_id IS 'ADJUSTMENT: the due it adjusts. LATE_FEE: not used (one late fee per student and month)';
COMMENT ON COLUMN student_dues.paid_amount IS 'Sum of allocations to this due, kept in the same transaction; checked by the consistency report';
COMMENT ON COLUMN student_dues.school_id IS 'School (tenant) this row belongs to';
