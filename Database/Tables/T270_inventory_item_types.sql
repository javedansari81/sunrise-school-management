-- =====================================================
-- Table: inventory_item_types
-- Description: Stores inventory item type definitions (uniforms and accessories)
-- Dependencies: inventory_item_category
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS inventory_item_types CASCADE;

-- Create table
CREATE TABLE inventory_item_types (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id),
    name VARCHAR(50) NOT NULL,
    description TEXT,
    inventory_item_category_id INTEGER NOT NULL,
    image_url VARCHAR(500), -- URL/path to item image
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT fk_inventory_item_types_category FOREIGN KEY (inventory_item_category_id)
        REFERENCES inventory_item_category(id) ON DELETE RESTRICT
);

CREATE INDEX idx_inventory_item_types_category_id ON inventory_item_types(inventory_item_category_id);

-- Add comments
COMMENT ON TABLE inventory_item_types IS 'Inventory item type definitions for school uniforms and accessories';
COMMENT ON COLUMN inventory_item_types.id IS 'Primary key - auto-increment';
COMMENT ON COLUMN inventory_item_types.name IS 'Item type name (CASUAL_DRESS_1, SHIRT, TIE, etc.)';
COMMENT ON COLUMN inventory_item_types.description IS 'Human-readable description of the item';
COMMENT ON COLUMN inventory_item_types.inventory_item_category_id IS 'Foreign key to inventory_item_category table';
COMMENT ON COLUMN inventory_item_types.image_url IS 'URL/path to item image';
COMMENT ON COLUMN inventory_item_types.is_active IS 'Flag to show/hide item type';

-- Multi-tenancy: every row belongs to one school
CREATE INDEX IF NOT EXISTS idx_inventory_item_types_school_id ON inventory_item_types (school_id);
CREATE UNIQUE INDEX IF NOT EXISTS inventory_item_types_school_name_unique ON inventory_item_types (school_id, name);
COMMENT ON COLUMN inventory_item_types.school_id IS 'School (tenant) this row belongs to';
