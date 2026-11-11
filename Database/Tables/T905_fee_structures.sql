-- =====================================================
-- Table: fee_structures
-- Description: Header of a price list for one session. Moves from DRAFT to
--              PUBLISHED; publishing archives the previously published list of
--              the session. A published list is never edited: it is copied into
--              a new draft instead.
-- Dependencies: schools, session_years, users
-- Note: the pre-redesign table of the same name is now legacy_fee_structures (T400).
-- =====================================================

DROP TABLE IF EXISTS fee_structures CASCADE;

CREATE TABLE fee_structures (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id),
    session_year_id INTEGER NOT NULL REFERENCES session_years(id),
    name VARCHAR(150) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'DRAFT'
        CHECK (status IN ('DRAFT', 'PUBLISHED', 'ARCHIVED')),
    copied_from_id INTEGER REFERENCES fee_structures(id),
    published_at TIMESTAMP WITH TIME ZONE,
    published_by INTEGER REFERENCES users(id),
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_fee_structures_school_id ON fee_structures (school_id);
CREATE INDEX idx_fee_structures_session ON fee_structures (school_id, session_year_id);
-- At most one published price list per school and session
CREATE UNIQUE INDEX fee_structures_one_published
    ON fee_structures (school_id, session_year_id) WHERE status = 'PUBLISHED';

COMMENT ON TABLE fee_structures IS 'Price list header per session (unified fee module)';
COMMENT ON COLUMN fee_structures.school_id IS 'School (tenant) this row belongs to';
