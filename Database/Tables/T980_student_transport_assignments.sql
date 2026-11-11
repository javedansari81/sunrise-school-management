-- =====================================================
-- Table: student_transport_assignments
-- Description: Who rides what, from when to when, at what monthly amount.
--              Each assignment owns TRANSPORT lines in student_fee_plans
--              (source_ref_id = this id); the fee module bills them.
--              A change ends one assignment and starts the next
--              (previous_assignment_id); paid months are never re-billed.
-- Dependencies: schools, students, session_years, transport_types, routes,
--               route_stops, transport_rates, users
-- =====================================================

DROP TABLE IF EXISTS student_transport_assignments CASCADE;

CREATE TABLE student_transport_assignments (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id),
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    session_year_id INTEGER NOT NULL REFERENCES session_years(id),
    transport_type_id INTEGER NOT NULL REFERENCES transport_types(id),
    route_id INTEGER REFERENCES routes(id),
    route_stop_id INTEGER REFERENCES route_stops(id),
    distance_km DECIMAL(6,2) CHECK (distance_km IS NULL OR distance_km >= 0),
    pickup_location VARCHAR(200),
    drop_location VARCHAR(200),
    start_date DATE NOT NULL,
    end_date DATE,
    monthly_amount DECIMAL(10,2) NOT NULL CHECK (monthly_amount >= 0),
    transport_rate_id INTEGER REFERENCES transport_rates(id) ON DELETE SET NULL,
    amount_overridden BOOLEAN NOT NULL DEFAULT FALSE,
    previous_assignment_id INTEGER REFERENCES student_transport_assignments(id),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    end_reason TEXT,
    remarks TEXT,
    created_by INTEGER REFERENCES users(id),
    ended_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT student_transport_assignments_dates CHECK (end_date IS NULL OR end_date >= start_date),
    CONSTRAINT student_transport_assignments_stop_needs_route CHECK (route_stop_id IS NULL OR route_id IS NOT NULL)
);

CREATE INDEX idx_student_transport_assignments_school_id ON student_transport_assignments (school_id);
CREATE INDEX idx_student_transport_assignments_student ON student_transport_assignments (student_id, session_year_id);
CREATE INDEX idx_student_transport_assignments_route ON student_transport_assignments (route_id, route_stop_id);
-- At most one open-ended assignment per student and session
CREATE UNIQUE INDEX student_transport_assignments_one_open
    ON student_transport_assignments (school_id, student_id, session_year_id)
    WHERE is_active AND end_date IS NULL;

COMMENT ON TABLE student_transport_assignments IS 'Who rides what (transport operations module); billed through student_fee_plans';
COMMENT ON COLUMN student_transport_assignments.start_date IS 'First day of riding; billed from that month if on or before the cut-off day, else from the next month';
COMMENT ON COLUMN student_transport_assignments.end_date IS 'Last day of riding; that month is billed if on or after the cut-off day. NULL = to the end of the session';
COMMENT ON COLUMN student_transport_assignments.monthly_amount IS 'Resolved from transport_rates when assigned (or set by hand); later rate edits do not change it';
COMMENT ON COLUMN student_transport_assignments.is_active IS 'FALSE = cancelled (entered by mistake); never billed';
COMMENT ON COLUMN student_transport_assignments.school_id IS 'School (tenant) this row belongs to';
