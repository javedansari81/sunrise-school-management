-- =====================================================
-- Table: transport_distance_slabs
-- Description: Stores distance-based pricing slabs for transport types
-- Dependencies: transport_types
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS transport_distance_slabs CASCADE;

-- Create table
CREATE TABLE transport_distance_slabs (
    id SERIAL PRIMARY KEY,
    transport_type_id INTEGER NOT NULL,
    distance_from_km DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    distance_to_km DECIMAL(5,2) NOT NULL,
    monthly_fee DECIMAL(10,2) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    
    -- Foreign Key Constraints
    FOREIGN KEY (transport_type_id) REFERENCES transport_types(id),
    
    -- Ensure no overlapping distance ranges for same transport type
    CONSTRAINT check_distance_range CHECK (distance_to_km > distance_from_km)
);

-- Add indexes
CREATE INDEX idx_transport_distance_slabs_type ON transport_distance_slabs(transport_type_id);

-- Add comments
COMMENT ON TABLE transport_distance_slabs IS 'Distance-based pricing slabs for transport types (e.g., Van: 0-8km=700, 8-10km=800)';
COMMENT ON COLUMN transport_distance_slabs.transport_type_id IS 'Foreign key to transport_types table';
COMMENT ON COLUMN transport_distance_slabs.distance_from_km IS 'Starting distance in kilometers (inclusive)';
COMMENT ON COLUMN transport_distance_slabs.distance_to_km IS 'Ending distance in kilometers (inclusive)';
COMMENT ON COLUMN transport_distance_slabs.monthly_fee IS 'Monthly fee for this distance range';

