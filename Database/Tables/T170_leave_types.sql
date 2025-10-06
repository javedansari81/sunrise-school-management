-- =====================================================
-- Table: leave_types
-- Description: Stores leave type definitions (SICK, CASUAL, EMERGENCY, etc.)
-- Dependencies: None (metadata table)
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS leave_types CASCADE;

-- Create table
CREATE TABLE leave_types (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    max_days_per_year INTEGER,
    requires_medical_certificate BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Add comments
COMMENT ON TABLE leave_types IS 'Leave type definitions for leave management';
COMMENT ON COLUMN leave_types.id IS 'Primary key - manually assigned ID';
COMMENT ON COLUMN leave_types.name IS 'Leave type name (SICK, CASUAL, EMERGENCY, MATERNITY, PATERNITY)';
COMMENT ON COLUMN leave_types.max_days_per_year IS 'Maximum days allowed per year for this leave type';
COMMENT ON COLUMN leave_types.requires_medical_certificate IS 'Flag indicating if medical certificate is required';

