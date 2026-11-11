-- =====================================================
-- V003: Transport operations module (Phase 3)
-- =====================================================
-- 1. Renames the pre-redesign transport_types table (a global list) to
--    legacy_transport_types, so the transport operations module can use the
--    name. The old transport code points at legacy_transport_types until
--    Phase 4 removes it.
-- 2. Creates the 7 tables of the transport operations module (same as
--    Tables/T960-T985).
-- 3. Seeds transport types, rates carried over from the old price list and
--    the fee.transport.due_day setting (same as Init/05_transport_defaults.sql).
-- =====================================================

-- 1. Legacy rename
ALTER TABLE transport_types RENAME TO legacy_transport_types;
ALTER TABLE legacy_transport_types RENAME CONSTRAINT transport_types_pkey TO legacy_transport_types_pkey;
ALTER TABLE legacy_transport_types RENAME CONSTRAINT transport_types_name_key TO legacy_transport_types_name_key;
COMMENT ON TABLE legacy_transport_types IS 'Pre-redesign transport types (global list); removed in Phase 4';

-- 2. Transport operations module tables
-- =====================================================
-- Table: transport_types
-- Description: Kinds of vehicle a school uses (E-Rickshaw, Van, Bus).
--              Transport operations module (Phase 3).
-- Dependencies: schools
-- =====================================================

CREATE TABLE transport_types (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id),
    name VARCHAR(50) NOT NULL,
    description TEXT,
    capacity INTEGER CHECK (capacity IS NULL OR capacity > 0),
    sort_order INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT transport_types_school_name_unique UNIQUE (school_id, name)
);

CREATE INDEX idx_transport_types_school_id ON transport_types (school_id);

COMMENT ON TABLE transport_types IS 'Kinds of vehicle a school uses (transport operations module)';
COMMENT ON COLUMN transport_types.capacity IS 'Default seats per vehicle of this type; a vehicle may set its own';
COMMENT ON COLUMN transport_types.school_id IS 'School (tenant) this row belongs to';

-- =====================================================
-- Table: vehicles
-- Description: Each physical vehicle of a school.
-- Dependencies: schools, transport_types
-- =====================================================

CREATE TABLE vehicles (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id),
    transport_type_id INTEGER NOT NULL REFERENCES transport_types(id),
    registration_number VARCHAR(30) NOT NULL,
    capacity INTEGER CHECK (capacity IS NULL OR capacity > 0),
    driver_name VARCHAR(100),
    driver_phone VARCHAR(20),
    remarks TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT vehicles_school_registration_unique UNIQUE (school_id, registration_number)
);

CREATE INDEX idx_vehicles_school_id ON vehicles (school_id);
CREATE INDEX idx_vehicles_transport_type_id ON vehicles (transport_type_id);

COMMENT ON TABLE vehicles IS 'Physical vehicles of a school (transport operations module)';
COMMENT ON COLUMN vehicles.capacity IS 'Seats; NULL = the transport type capacity';
COMMENT ON COLUMN vehicles.school_id IS 'School (tenant) this row belongs to';

-- =====================================================
-- Table: routes
-- Description: A named route, optionally served by one vehicle.
-- Dependencies: schools, vehicles
-- =====================================================

CREATE TABLE routes (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    vehicle_id INTEGER REFERENCES vehicles(id),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT routes_school_name_unique UNIQUE (school_id, name)
);

CREATE INDEX idx_routes_school_id ON routes (school_id);
CREATE INDEX idx_routes_vehicle_id ON routes (vehicle_id);

COMMENT ON TABLE routes IS 'Named routes (transport operations module)';
COMMENT ON COLUMN routes.vehicle_id IS 'Vehicle that serves the route; NULL = not set';
COMMENT ON COLUMN routes.school_id IS 'School (tenant) this row belongs to';

-- =====================================================
-- Table: route_stops
-- Description: Ordered stops on a route.
-- Dependencies: schools, routes
-- =====================================================

CREATE TABLE route_stops (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id),
    route_id INTEGER NOT NULL REFERENCES routes(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    sequence SMALLINT NOT NULL CHECK (sequence > 0),
    distance_km DECIMAL(6,2) CHECK (distance_km IS NULL OR distance_km >= 0),
    pickup_time TIME,
    drop_time TIME,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    -- Deferred, so stops can be reordered in one transaction
    CONSTRAINT route_stops_route_sequence_unique UNIQUE (route_id, sequence) DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT route_stops_route_name_unique UNIQUE (route_id, name)
);

CREATE INDEX idx_route_stops_school_id ON route_stops (school_id);

COMMENT ON TABLE route_stops IS 'Ordered stops on a route (transport operations module)';
COMMENT ON COLUMN route_stops.distance_km IS 'Distance from school; used for distance-slab pricing';
COMMENT ON COLUMN route_stops.school_id IS 'School (tenant) this row belongs to';

-- =====================================================
-- Table: transport_rates
-- Description: Monthly transport price per session. Three kinds:
--              PER_STOP       price for one stop (optionally per transport type)
--              DISTANCE_SLAB  price for a distance band (optionally per type)
--              FLAT           price for a transport type
--              An assignment takes the first match in that order.
-- Dependencies: schools, session_years, transport_types, route_stops
-- =====================================================

CREATE TABLE transport_rates (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id),
    session_year_id INTEGER NOT NULL REFERENCES session_years(id),
    basis VARCHAR(20) NOT NULL CHECK (basis IN ('PER_STOP', 'DISTANCE_SLAB', 'FLAT')),
    transport_type_id INTEGER REFERENCES transport_types(id),
    route_stop_id INTEGER REFERENCES route_stops(id) ON DELETE CASCADE,
    distance_from_km DECIMAL(6,2),
    distance_to_km DECIMAL(6,2),
    monthly_amount DECIMAL(10,2) NOT NULL CHECK (monthly_amount >= 0),
    description VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT transport_rates_shape CHECK (
        (basis = 'PER_STOP' AND route_stop_id IS NOT NULL
            AND distance_from_km IS NULL AND distance_to_km IS NULL)
        OR (basis = 'DISTANCE_SLAB' AND route_stop_id IS NULL
            AND distance_from_km IS NOT NULL AND distance_to_km IS NOT NULL
            AND distance_from_km >= 0 AND distance_to_km > distance_from_km)
        OR (basis = 'FLAT' AND transport_type_id IS NOT NULL AND route_stop_id IS NULL
            AND distance_from_km IS NULL AND distance_to_km IS NULL)
    )
);

CREATE INDEX idx_transport_rates_school_id ON transport_rates (school_id);
CREATE INDEX idx_transport_rates_session ON transport_rates (session_year_id, basis);
CREATE UNIQUE INDEX transport_rates_one_flat
    ON transport_rates (school_id, session_year_id, transport_type_id)
    WHERE basis = 'FLAT' AND is_active;
CREATE UNIQUE INDEX transport_rates_one_per_stop
    ON transport_rates (school_id, session_year_id, route_stop_id, COALESCE(transport_type_id, 0))
    WHERE basis = 'PER_STOP' AND is_active;

COMMENT ON TABLE transport_rates IS 'Monthly transport prices per session (transport operations module)';
COMMENT ON COLUMN transport_rates.transport_type_id IS 'NULL on PER_STOP and DISTANCE_SLAB = any transport type';
COMMENT ON COLUMN transport_rates.distance_from_km IS 'Slab covers distances above this (a slab from 0 includes 0)';
COMMENT ON COLUMN transport_rates.distance_to_km IS 'Slab covers distances up to and including this';
COMMENT ON COLUMN transport_rates.school_id IS 'School (tenant) this row belongs to';

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

-- =====================================================
-- Table: transport_assignment_pauses
-- Description: Months in which an assignment's service is paused and not
--              billed (e.g. a student away for two months).
-- Dependencies: schools, student_transport_assignments, users
-- =====================================================

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

-- 3. Defaults
-- =====================================================
-- Transport operations module: default transport types, rates and settings
-- =====================================================
-- Runs for every school, so the same script serves a fresh deployment
-- (school 1) and migration V003 (every existing school). Each step skips a
-- school that already has the rows. New schools created later get theirs from
-- app/modules/transport/provisioning.py.
--
-- 1. Transport types E-Rickshaw, Van and Bus for every school without types.
-- 2. Rates carried over from the pre-redesign price list
--    (transport_type_pricing and transport_distance_slabs, which only Sunrise
--    has) for schools without rates. Price lists are configuration, not student
--    data, so they are kept (decision 1 drops only old enrollments and
--    payments). Old slabs ran 0-8, 8.01-10, ...; new slabs cover
--    (from, to], so 8.01 becomes 8.00.
-- 3. The fee.transport.due_day setting.
-- =====================================================

INSERT INTO transport_types (school_id, name, description, capacity, sort_order)
SELECT s.id, d.name, d.description, d.capacity, d.sort_order
FROM schools s
CROSS JOIN (VALUES
    ('E-Rickshaw', 'E-Rickshaw service', 6, 10),
    ('Van', 'Van service', 12, 20),
    ('Bus', 'Bus service', 40, 30)
) AS d (name, description, capacity, sort_order)
WHERE NOT EXISTS (SELECT 1 FROM transport_types t WHERE t.school_id = s.id);

CREATE TEMP TABLE _legacy_transport_type_map AS
SELECT lt.id AS legacy_id,
       CASE lt.name
           WHEN 'E_RICKSHAW' THEN 'E-Rickshaw'
           WHEN 'VAN' THEN 'Van'
           WHEN 'BUS' THEN 'Bus'
           ELSE initcap(replace(lt.name, '_', ' '))
       END AS name
FROM legacy_transport_types lt;

INSERT INTO transport_rates (school_id, session_year_id, basis, transport_type_id, monthly_amount, description)
SELECT sy.school_id, p.session_year_id, 'FLAT', t.id, p.base_monthly_fee, 'Carried over from the old price list'
FROM transport_type_pricing p
JOIN session_years sy ON sy.id = p.session_year_id
JOIN _legacy_transport_type_map m ON m.legacy_id = p.transport_type_id
JOIN transport_types t ON t.school_id = sy.school_id AND t.name = m.name
WHERE p.is_active
  AND NOT EXISTS (SELECT 1 FROM transport_rates r WHERE r.school_id = sy.school_id AND r.basis = 'FLAT');

INSERT INTO transport_rates (school_id, session_year_id, basis, transport_type_id,
                             distance_from_km, distance_to_km, monthly_amount, description)
SELECT sy.school_id, p.session_year_id, 'DISTANCE_SLAB', t.id,
       CASE WHEN ds.distance_from_km = 0 THEN 0 ELSE ds.distance_from_km - 0.01 END,
       ds.distance_to_km, ds.monthly_fee, ds.description
FROM transport_distance_slabs ds
JOIN transport_type_pricing p ON p.transport_type_id = ds.transport_type_id AND p.is_active
JOIN session_years sy ON sy.id = p.session_year_id
JOIN _legacy_transport_type_map m ON m.legacy_id = ds.transport_type_id
JOIN transport_types t ON t.school_id = sy.school_id AND t.name = m.name
WHERE ds.is_active
  AND NOT EXISTS (SELECT 1 FROM transport_rates r WHERE r.school_id = sy.school_id AND r.basis = 'DISTANCE_SLAB');

DROP TABLE _legacy_transport_type_map;

INSERT INTO school_settings (school_id, key, value, description)
SELECT id, 'fee.transport.due_day', '10', 'Day of the month transport dues fall due (1-28)'
FROM schools
ON CONFLICT (school_id, key) DO NOTHING;
