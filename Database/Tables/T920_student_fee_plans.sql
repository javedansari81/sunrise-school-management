-- =====================================================
-- Table: student_fee_plans
-- Description: Which fee heads a student pays in a session, at what amount and
--              from which month to which month. Dues are generated from here.
-- Dependencies: students, session_years, fee_heads, users
-- =====================================================

DROP TABLE IF EXISTS student_fee_plans CASCADE;

CREATE TABLE student_fee_plans (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id),
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    session_year_id INTEGER NOT NULL REFERENCES session_years(id),
    fee_head_id INTEGER NOT NULL REFERENCES fee_heads(id),
    amount DECIMAL(10,2) NOT NULL CHECK (amount >= 0),
    frequency VARCHAR(20) NOT NULL DEFAULT 'MONTHLY'
        CHECK (frequency IN ('MONTHLY', 'QUARTERLY', 'HALF_YEARLY', 'ANNUAL', 'ONE_TIME')),
    billing_months SMALLINT[],
    due_day SMALLINT NOT NULL DEFAULT 10 CHECK (due_day BETWEEN 1 AND 28),
    start_period DATE NOT NULL,
    end_period DATE,
    source VARCHAR(20) NOT NULL CHECK (source IN ('CLASS', 'TRANSPORT', 'MANUAL')),
    source_ref_id INTEGER,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    remarks TEXT,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT student_fee_plans_period_order CHECK (end_period IS NULL OR end_period >= start_period),
    CONSTRAINT student_fee_plans_first_of_month CHECK (
        EXTRACT(DAY FROM start_period) = 1 AND (end_period IS NULL OR EXTRACT(DAY FROM end_period) = 1)
    )
);

CREATE INDEX idx_student_fee_plans_school_id ON student_fee_plans (school_id);
CREATE INDEX idx_student_fee_plans_student_session ON student_fee_plans (student_id, session_year_id);
-- One open-ended class-based line per student, session and head. A line ended by a
-- class or price change keeps billing up to its end_period; is_active = FALSE means cancelled.
CREATE UNIQUE INDEX student_fee_plans_one_class_line
    ON student_fee_plans (school_id, student_id, session_year_id, fee_head_id)
    WHERE source = 'CLASS' AND is_active AND end_period IS NULL;

COMMENT ON TABLE student_fee_plans IS 'Fee heads a student pays per session (unified fee module)';
COMMENT ON COLUMN student_fee_plans.start_period IS 'First billed month (first day of the month)';
COMMENT ON COLUMN student_fee_plans.end_period IS 'Last billed month (first day of the month); NULL = to the end of the session';
COMMENT ON COLUMN student_fee_plans.source_ref_id IS 'fee_structure_items.id for CLASS, the transport assignment id for TRANSPORT';
COMMENT ON COLUMN student_fee_plans.school_id IS 'School (tenant) this row belongs to';
