-- =====================================================
-- Table: transport_rates
-- Description: Monthly transport price per session. Three kinds:
--              PER_STOP       price for one stop (optionally per transport type)
--              DISTANCE_SLAB  price for a distance band (optionally per type)
--              FLAT           price for a transport type
--              An assignment takes the first match in that order.
-- Dependencies: schools, session_years, transport_types, route_stops
-- =====================================================

DROP TABLE IF EXISTS transport_rates CASCADE;

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
