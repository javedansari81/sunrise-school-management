-- =====================================================
-- Table: transport_type_pricing
-- Description: Session-based pricing for transport types
-- Dependencies: transport_types, session_years
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS transport_type_pricing CASCADE;

-- Create table
CREATE TABLE transport_type_pricing (
    id SERIAL PRIMARY KEY,
    transport_type_id INTEGER NOT NULL,
    session_year_id INTEGER NOT NULL,
    base_monthly_fee DECIMAL(10,2) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    
    -- Foreign Key Constraints
    FOREIGN KEY (transport_type_id) REFERENCES transport_types(id),
    FOREIGN KEY (session_year_id) REFERENCES session_years(id),
    
    -- Unique constraint: one pricing per transport type per session
    UNIQUE (transport_type_id, session_year_id)
);

-- Add indexes for performance
CREATE INDEX idx_transport_type_pricing_type ON transport_type_pricing(transport_type_id);
CREATE INDEX idx_transport_type_pricing_session ON transport_type_pricing(session_year_id);
CREATE INDEX idx_transport_type_pricing_active ON transport_type_pricing(is_active);

-- Add comments
COMMENT ON TABLE transport_type_pricing IS 'Session-based pricing for transport types (enables different rates per academic year)';
COMMENT ON COLUMN transport_type_pricing.transport_type_id IS 'Foreign key to transport_types table';
COMMENT ON COLUMN transport_type_pricing.session_year_id IS 'Foreign key to session_years table';
COMMENT ON COLUMN transport_type_pricing.base_monthly_fee IS 'Base monthly fee for this transport type in this session';

