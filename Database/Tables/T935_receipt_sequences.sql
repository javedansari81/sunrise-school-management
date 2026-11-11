-- =====================================================
-- Table: receipt_sequences
-- Description: Receipt numbering per school and session, e.g. SUN/2026-27/000123.
--              The next number is taken with SELECT ... FOR UPDATE inside the
--              payment transaction, so two cashiers never get the same number.
-- Dependencies: schools, session_years
-- =====================================================

DROP TABLE IF EXISTS receipt_sequences CASCADE;

CREATE TABLE receipt_sequences (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id),
    session_year_id INTEGER NOT NULL REFERENCES session_years(id),
    prefix VARCHAR(20) NOT NULL,
    next_number INTEGER NOT NULL DEFAULT 1 CHECK (next_number > 0),
    padding SMALLINT NOT NULL DEFAULT 6,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT receipt_sequences_school_session_unique UNIQUE (school_id, session_year_id)
);

CREATE INDEX idx_receipt_sequences_school_id ON receipt_sequences (school_id);

COMMENT ON TABLE receipt_sequences IS 'Receipt number series per school and session (unified fee module)';
COMMENT ON COLUMN receipt_sequences.school_id IS 'School (tenant) this row belongs to';
