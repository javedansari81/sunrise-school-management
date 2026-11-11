-- =====================================================
-- Table: transport_types
-- Description: Kinds of vehicle a school uses (E-Rickshaw, Van, Bus).
--              Transport operations module (Phase 3).
-- Dependencies: schools
-- =====================================================

DROP TABLE IF EXISTS transport_types CASCADE;

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
