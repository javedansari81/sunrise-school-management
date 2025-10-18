-- =====================================================
-- Table: transport_types
-- Description: Stores transport type options (E_RICKSHAW, VAN, BUS, etc.)
-- Dependencies: None (metadata table)
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS transport_types CASCADE;

-- Create table
CREATE TABLE transport_types (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    base_monthly_fee DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    capacity INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Add comments
COMMENT ON TABLE transport_types IS 'Transport type options (E_RICKSHAW, VAN, BUS)';
COMMENT ON COLUMN transport_types.id IS 'Primary key - manually assigned ID';
COMMENT ON COLUMN transport_types.name IS 'Transport type name (E_RICKSHAW, VAN, etc.)';
COMMENT ON COLUMN transport_types.description IS 'Human-readable description';
COMMENT ON COLUMN transport_types.base_monthly_fee IS 'Base monthly fee for this transport type';
COMMENT ON COLUMN transport_types.capacity IS 'Vehicle capacity (number of students)';

