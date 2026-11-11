-- =====================================================
-- Table: student_concessions
-- Description: A concession granted to one student (staff child, scholarship,
--              custom), with reason and approver. Sibling concessions are not
--              stored here: they are worked out from the SIBLING rule and the
--              student's linked siblings each time dues are generated.
-- Dependencies: students, session_years, concession_rules, users
-- =====================================================

DROP TABLE IF EXISTS student_concessions CASCADE;

CREATE TABLE student_concessions (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id),
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    session_year_id INTEGER NOT NULL REFERENCES session_years(id),
    concession_rule_id INTEGER REFERENCES concession_rules(id),
    concession_type VARCHAR(20) NOT NULL
        CHECK (concession_type IN ('STAFF', 'SCHOLARSHIP', 'CUSTOM')),
    value_type VARCHAR(10) NOT NULL CHECK (value_type IN ('PERCENT', 'FIXED')),
    value DECIMAL(10,2) NOT NULL CHECK (value >= 0),
    fee_head_ids INTEGER[],
    start_period DATE,
    end_period DATE,
    reason TEXT NOT NULL,
    approved_by INTEGER REFERENCES users(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT student_concessions_percent_max CHECK (value_type <> 'PERCENT' OR value <= 100)
);

CREATE INDEX idx_student_concessions_school_id ON student_concessions (school_id);
CREATE INDEX idx_student_concessions_student_session ON student_concessions (student_id, session_year_id);

COMMENT ON TABLE student_concessions IS 'Concessions granted to individual students (unified fee module)';
COMMENT ON COLUMN student_concessions.fee_head_ids IS 'Fee heads covered; NULL = every head';
COMMENT ON COLUMN student_concessions.school_id IS 'School (tenant) this row belongs to';
