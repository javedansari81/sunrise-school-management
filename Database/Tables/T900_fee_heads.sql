-- =====================================================
-- Table: fee_heads
-- Description: A school's list of fee types (Tuition, Transport, Admission, ...).
--              A new fee type is a row, not a schema change.
-- Dependencies: schools
-- =====================================================

DROP TABLE IF EXISTS fee_heads CASCADE;

CREATE TABLE fee_heads (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id),
    code VARCHAR(30) NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(20) NOT NULL DEFAULT 'ACADEMIC'
        CHECK (category IN ('ACADEMIC', 'TRANSPORT', 'ONE_TIME', 'PENALTY', 'OTHER')),
    default_frequency VARCHAR(20) NOT NULL DEFAULT 'MONTHLY'
        CHECK (default_frequency IN ('MONTHLY', 'QUARTERLY', 'HALF_YEARLY', 'ANNUAL', 'ONE_TIME')),
    is_system BOOLEAN NOT NULL DEFAULT FALSE,
    sort_order INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT fee_heads_school_code_unique UNIQUE (school_id, code),
    CONSTRAINT fee_heads_school_name_unique UNIQUE (school_id, name)
);

CREATE INDEX idx_fee_heads_school_id ON fee_heads (school_id);

COMMENT ON TABLE fee_heads IS 'Fee types defined per school (unified fee module)';
COMMENT ON COLUMN fee_heads.code IS 'Stable code, unique per school (TUITION, TRANSPORT, LATE_FEE, ...)';
COMMENT ON COLUMN fee_heads.is_system IS 'Used by the system (TRANSPORT, LATE_FEE): cannot be deleted or have its code changed';
COMMENT ON COLUMN fee_heads.school_id IS 'School (tenant) this row belongs to';
