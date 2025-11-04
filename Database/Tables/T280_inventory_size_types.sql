-- =====================================================
-- Table: inventory_size_types
-- Description: Stores size type definitions for inventory items
-- Dependencies: None (metadata table)
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS inventory_size_types CASCADE;

-- Create table
CREATE TABLE inventory_size_types (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    sort_order INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Add comments
COMMENT ON TABLE inventory_size_types IS 'Size type definitions for inventory items';
COMMENT ON COLUMN inventory_size_types.id IS 'Primary key - manually assigned ID';
COMMENT ON COLUMN inventory_size_types.name IS 'Size name (XS, S, M, L, XL, XXL, FREE_SIZE)';
COMMENT ON COLUMN inventory_size_types.description IS 'Human-readable description of the size';
COMMENT ON COLUMN inventory_size_types.sort_order IS 'Order for displaying sizes';
COMMENT ON COLUMN inventory_size_types.is_active IS 'Flag to show/hide size type';

