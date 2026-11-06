-- =====================================================
-- Table: inventory_size_types
-- Description: Stores size type definitions for inventory items
-- Dependencies: None (metadata table)
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS inventory_size_types CASCADE;

-- Create table
CREATE TABLE inventory_size_types (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id),
    name VARCHAR(50) NOT NULL,
    description TEXT,
    sort_order INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Add comments
COMMENT ON TABLE inventory_size_types IS 'Size type definitions for inventory items';
COMMENT ON COLUMN inventory_size_types.id IS 'Primary key - auto-increment';
COMMENT ON COLUMN inventory_size_types.name IS 'Size name (XS, S, M, L, XL, XXL, FREE_SIZE)';
COMMENT ON COLUMN inventory_size_types.description IS 'Human-readable description of the size';
COMMENT ON COLUMN inventory_size_types.sort_order IS 'Order for displaying sizes';
COMMENT ON COLUMN inventory_size_types.is_active IS 'Flag to show/hide size type';

-- Multi-tenancy: every row belongs to one school
CREATE INDEX IF NOT EXISTS idx_inventory_size_types_school_id ON inventory_size_types (school_id);
CREATE UNIQUE INDEX IF NOT EXISTS inventory_size_types_school_name_unique ON inventory_size_types (school_id, name);
COMMENT ON COLUMN inventory_size_types.school_id IS 'School (tenant) this row belongs to';
