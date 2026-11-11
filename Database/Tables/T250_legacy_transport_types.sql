-- =====================================================
-- Table: legacy_transport_types
-- Description: Pre-redesign transport types (E_RICKSHAW, VAN). The transport
--              operations module uses the per-school transport_types (T960).
--              Removed in Phase 4.
-- Dependencies: None (metadata table)
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS legacy_transport_types CASCADE;

-- Create table
CREATE TABLE legacy_transport_types (
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
COMMENT ON TABLE legacy_transport_types IS 'Pre-redesign transport types (global list); removed in Phase 4';
COMMENT ON COLUMN legacy_transport_types.id IS 'Primary key - manually assigned ID';
COMMENT ON COLUMN legacy_transport_types.name IS 'Transport type name (E_RICKSHAW, VAN, etc.)';
COMMENT ON COLUMN legacy_transport_types.description IS 'Human-readable description';
COMMENT ON COLUMN legacy_transport_types.base_monthly_fee IS 'Base monthly fee for this transport type';
COMMENT ON COLUMN legacy_transport_types.capacity IS 'Vehicle capacity (number of students)';

