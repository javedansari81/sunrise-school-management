-- =====================================================
-- Table: inventory_purchase_items
-- Description: Stores line items for inventory purchases
-- Dependencies: inventory_purchases, inventory_item_types, inventory_size_types
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS inventory_purchase_items CASCADE;

-- Create table
CREATE TABLE inventory_purchase_items (
    id SERIAL PRIMARY KEY,
    purchase_id INTEGER NOT NULL,
    inventory_item_type_id INTEGER NOT NULL,
    size_type_id INTEGER,
    
    -- Item Details
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10,2) NOT NULL CHECK (unit_price > 0),
    total_price DECIMAL(10,2) NOT NULL CHECK (total_price > 0),
    
    -- Audit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Foreign Keys
    FOREIGN KEY (purchase_id) REFERENCES inventory_purchases(id) ON DELETE CASCADE,
    FOREIGN KEY (inventory_item_type_id) REFERENCES inventory_item_types(id),
    FOREIGN KEY (size_type_id) REFERENCES inventory_size_types(id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_inventory_purchase_items_purchase ON inventory_purchase_items(purchase_id);
CREATE INDEX IF NOT EXISTS idx_inventory_purchase_items_item_type ON inventory_purchase_items(inventory_item_type_id);
CREATE INDEX IF NOT EXISTS idx_inventory_purchase_items_size ON inventory_purchase_items(size_type_id);

-- Add comments
COMMENT ON TABLE inventory_purchase_items IS 'Line items for inventory purchases';
COMMENT ON COLUMN inventory_purchase_items.purchase_id IS 'Reference to parent purchase transaction';
COMMENT ON COLUMN inventory_purchase_items.inventory_item_type_id IS 'Reference to inventory item type';
COMMENT ON COLUMN inventory_purchase_items.size_type_id IS 'Reference to size type (optional)';
COMMENT ON COLUMN inventory_purchase_items.quantity IS 'Quantity of items purchased';
COMMENT ON COLUMN inventory_purchase_items.unit_price IS 'Price per unit at time of purchase';
COMMENT ON COLUMN inventory_purchase_items.total_price IS 'Total price for this line item (quantity × unit_price)';

