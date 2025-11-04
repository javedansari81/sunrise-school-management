-- =====================================================
-- Table: inventory_pricing
-- Description: Stores pricing for inventory items (supports multiple rates per item)
-- Dependencies: inventory_item_types, inventory_size_types, classes, session_years, users
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS inventory_pricing CASCADE;

-- Create table
CREATE TABLE inventory_pricing (
    id SERIAL PRIMARY KEY,
    inventory_item_type_id INTEGER NOT NULL,
    size_type_id INTEGER,
    class_id INTEGER, -- Optional: different prices for different classes
    session_year_id INTEGER NOT NULL,
    
    -- Pricing Details
    unit_price DECIMAL(10,2) NOT NULL CHECK (unit_price > 0),
    description TEXT,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    effective_from DATE NOT NULL,
    effective_to DATE,
    
    -- Audit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    created_by INTEGER,
    
    -- Foreign Keys
    FOREIGN KEY (inventory_item_type_id) REFERENCES inventory_item_types(id),
    FOREIGN KEY (size_type_id) REFERENCES inventory_size_types(id),
    FOREIGN KEY (class_id) REFERENCES classes(id),
    FOREIGN KEY (session_year_id) REFERENCES session_years(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_inventory_pricing_item ON inventory_pricing(inventory_item_type_id);
CREATE INDEX IF NOT EXISTS idx_inventory_pricing_session ON inventory_pricing(session_year_id);
CREATE INDEX IF NOT EXISTS idx_inventory_pricing_active ON inventory_pricing(is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_inventory_pricing_class ON inventory_pricing(class_id);
CREATE INDEX IF NOT EXISTS idx_inventory_pricing_size ON inventory_pricing(size_type_id);

-- Add comments
COMMENT ON TABLE inventory_pricing IS 'Pricing information for inventory items with support for multiple rates';
COMMENT ON COLUMN inventory_pricing.inventory_item_type_id IS 'Reference to inventory item type';
COMMENT ON COLUMN inventory_pricing.size_type_id IS 'Reference to size type (optional)';
COMMENT ON COLUMN inventory_pricing.class_id IS 'Reference to class for class-specific pricing (optional)';
COMMENT ON COLUMN inventory_pricing.session_year_id IS 'Reference to session year';
COMMENT ON COLUMN inventory_pricing.unit_price IS 'Price per unit';
COMMENT ON COLUMN inventory_pricing.effective_from IS 'Date from which this price is effective';
COMMENT ON COLUMN inventory_pricing.effective_to IS 'Date until which this price is effective (NULL = no end date)';

