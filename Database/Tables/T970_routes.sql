-- =====================================================
-- Table: routes
-- Description: A named route, optionally served by one vehicle.
-- Dependencies: schools, vehicles
-- =====================================================

DROP TABLE IF EXISTS routes CASCADE;

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
