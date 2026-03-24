-- =====================================================
-- Table: inventory_item_category
-- Description: Stores inventory item category definitions (normalized)
-- Dependencies: None (metadata table)
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS inventory_item_category CASCADE;

-- Create table
CREATE TABLE inventory_item_category (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    display_order INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Add comments
COMMENT ON TABLE inventory_item_category IS 'Inventory item category definitions (UNIFORM, ACCESSORY, BOOKS, NOTEBOOKS, STATIONERY)';
COMMENT ON COLUMN inventory_item_category.id IS 'Primary key - manually assigned ID';
COMMENT ON COLUMN inventory_item_category.name IS 'Category name (UNIFORM, ACCESSORY, BOOKS, NOTEBOOKS, STATIONERY)';
COMMENT ON COLUMN inventory_item_category.description IS 'Human-readable description of the category';
COMMENT ON COLUMN inventory_item_category.display_order IS 'Order for displaying categories in UI';
COMMENT ON COLUMN inventory_item_category.is_active IS 'Flag to show/hide category';

-- Create index
CREATE INDEX idx_inventory_item_category_name ON inventory_item_category(name);
CREATE INDEX idx_inventory_item_category_active ON inventory_item_category(is_active);

