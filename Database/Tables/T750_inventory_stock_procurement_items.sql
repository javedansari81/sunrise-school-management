-- =====================================================
-- Table: inventory_stock_procurement_items
-- Description: Line items for stock procurements
-- Dependencies: inventory_stock_procurements, inventory_item_types, inventory_size_types
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS inventory_stock_procurement_items CASCADE;

-- Create table
CREATE TABLE inventory_stock_procurement_items (
    id SERIAL PRIMARY KEY,
    procurement_id INTEGER NOT NULL,
    inventory_item_type_id INTEGER NOT NULL,
    size_type_id INTEGER,
    
    -- Item Details
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_cost DECIMAL(10,2) NOT NULL CHECK (unit_cost > 0),
    total_cost DECIMAL(10,2) NOT NULL CHECK (total_cost > 0),
    
    -- Audit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Foreign Keys
    FOREIGN KEY (procurement_id) REFERENCES inventory_stock_procurements(id) ON DELETE CASCADE,
    FOREIGN KEY (inventory_item_type_id) REFERENCES inventory_item_types(id),
    FOREIGN KEY (size_type_id) REFERENCES inventory_size_types(id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_stock_procurement_items_procurement ON inventory_stock_procurement_items(procurement_id);
CREATE INDEX IF NOT EXISTS idx_stock_procurement_items_item ON inventory_stock_procurement_items(inventory_item_type_id);

-- Add comments
COMMENT ON TABLE inventory_stock_procurement_items IS 'Line items for stock procurement transactions';
COMMENT ON COLUMN inventory_stock_procurement_items.procurement_id IS 'Reference to parent procurement transaction';
COMMENT ON COLUMN inventory_stock_procurement_items.inventory_item_type_id IS 'Reference to inventory item type';
COMMENT ON COLUMN inventory_stock_procurement_items.size_type_id IS 'Reference to size type (nullable for items without sizes)';
COMMENT ON COLUMN inventory_stock_procurement_items.quantity IS 'Quantity of items procured';
COMMENT ON COLUMN inventory_stock_procurement_items.unit_cost IS 'Cost per unit at time of procurement';
COMMENT ON COLUMN inventory_stock_procurement_items.total_cost IS 'Total cost for this line item (quantity × unit_cost)';

