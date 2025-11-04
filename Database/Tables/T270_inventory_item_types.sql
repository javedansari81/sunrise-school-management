-- =====================================================
-- Table: inventory_item_types
-- Description: Stores inventory item type definitions (uniforms and accessories)
-- Dependencies: None (metadata table)
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS inventory_item_types CASCADE;

-- Create table
CREATE TABLE inventory_item_types (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    category VARCHAR(50), -- 'UNIFORM', 'ACCESSORY'
    image_url VARCHAR(500), -- URL/path to item image
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Add comments
COMMENT ON TABLE inventory_item_types IS 'Inventory item type definitions for school uniforms and accessories';
COMMENT ON COLUMN inventory_item_types.id IS 'Primary key - manually assigned ID';
COMMENT ON COLUMN inventory_item_types.name IS 'Item type name (CASUAL_DRESS_1, SHIRT, TIE, etc.)';
COMMENT ON COLUMN inventory_item_types.description IS 'Human-readable description of the item';
COMMENT ON COLUMN inventory_item_types.category IS 'Item category (UNIFORM, ACCESSORY)';
COMMENT ON COLUMN inventory_item_types.image_url IS 'URL/path to item image';
COMMENT ON COLUMN inventory_item_types.is_active IS 'Flag to show/hide item type';

