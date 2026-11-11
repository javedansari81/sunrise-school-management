-- =====================================================
-- Table: transport_assignment_pauses
-- Description: Months in which an assignment's service is paused and not
--              billed (e.g. a student away for two months).
-- Dependencies: schools, student_transport_assignments, users
-- =====================================================

DROP TABLE IF EXISTS transport_assignment_pauses CASCADE;

CREATE TABLE transport_assignment_pauses (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id),
    assignment_id INTEGER NOT NULL REFERENCES student_transport_assignments(id) ON DELETE CASCADE,
    from_period DATE NOT NULL,
    to_period DATE NOT NULL,
    reason TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT transport_assignment_pauses_order CHECK (to_period >= from_period),
    CONSTRAINT transport_assignment_pauses_first_of_month CHECK (
        EXTRACT(DAY FROM from_period) = 1 AND EXTRACT(DAY FROM to_period) = 1
    )
);

CREATE INDEX idx_transport_assignment_pauses_school_id ON transport_assignment_pauses (school_id);
CREATE INDEX idx_transport_assignment_pauses_assignment ON transport_assignment_pauses (assignment_id);

COMMENT ON TABLE transport_assignment_pauses IS 'Paused (unbilled) months of a transport assignment';
COMMENT ON COLUMN transport_assignment_pauses.from_period IS 'First paused month (first day of the month)';
COMMENT ON COLUMN transport_assignment_pauses.to_period IS 'Last paused month (first day of the month)';
COMMENT ON COLUMN transport_assignment_pauses.is_active IS 'FALSE = pause removed (service resumed)';
COMMENT ON COLUMN transport_assignment_pauses.school_id IS 'School (tenant) this row belongs to';
