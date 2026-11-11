-- =====================================================
-- Table: vehicles
-- Description: Each physical vehicle of a school.
-- Dependencies: schools, transport_types
-- =====================================================

DROP TABLE IF EXISTS vehicles CASCADE;

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
