-- =====================================================
-- Table: inventory_stock
-- Description: Tracks current stock levels for inventory items
-- Dependencies: inventory_item_types, inventory_size_types
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS inventory_stock CASCADE;

-- Create table
CREATE TABLE inventory_stock (
    id SERIAL PRIMARY KEY,
    inventory_item_type_id INTEGER NOT NULL,
    size_type_id INTEGER,
    
    -- Stock Levels
    current_quantity INTEGER NOT NULL DEFAULT 0 CHECK (current_quantity >= 0),
    minimum_threshold INTEGER NOT NULL DEFAULT 10,
    reorder_quantity INTEGER NOT NULL DEFAULT 50,
    
    -- Metadata
    last_restocked_date DATE,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Foreign Keys
    FOREIGN KEY (inventory_item_type_id) REFERENCES inventory_item_types(id),
    FOREIGN KEY (size_type_id) REFERENCES inventory_size_types(id),
    
    -- Unique constraint: one record per item-size combination
    UNIQUE(inventory_item_type_id, size_type_id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_inventory_stock_item ON inventory_stock(inventory_item_type_id);
CREATE INDEX IF NOT EXISTS idx_inventory_stock_size ON inventory_stock(size_type_id);
CREATE INDEX IF NOT EXISTS idx_inventory_stock_low ON inventory_stock(current_quantity) WHERE current_quantity <= minimum_threshold;

-- Add comments
COMMENT ON TABLE inventory_stock IS 'Current stock levels for inventory items';
COMMENT ON COLUMN inventory_stock.inventory_item_type_id IS 'Reference to inventory item type';
COMMENT ON COLUMN inventory_stock.size_type_id IS 'Reference to size type (nullable for items without sizes)';
COMMENT ON COLUMN inventory_stock.current_quantity IS 'Current available quantity in stock';
COMMENT ON COLUMN inventory_stock.minimum_threshold IS 'Minimum quantity before low-stock alert';
COMMENT ON COLUMN inventory_stock.reorder_quantity IS 'Suggested reorder quantity';
COMMENT ON COLUMN inventory_stock.last_restocked_date IS 'Date of last stock replenishment';
COMMENT ON COLUMN inventory_stock.last_updated IS 'Timestamp of last stock update';

