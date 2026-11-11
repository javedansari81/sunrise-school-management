-- =====================================================
-- Table: route_stops
-- Description: Ordered stops on a route.
-- Dependencies: schools, routes
-- =====================================================

DROP TABLE IF EXISTS route_stops CASCADE;

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
