-- =====================================================
-- Table: leave_types
-- Description: Stores leave type definitions (SICK, CASUAL, EMERGENCY, etc.)
-- Dependencies: None (metadata table)
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS leave_types CASCADE;

-- Create table
CREATE TABLE leave_types (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id),
    name VARCHAR(50) NOT NULL,
    description TEXT,
    max_days_per_year INTEGER,
    requires_medical_certificate BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Add comments
COMMENT ON TABLE leave_types IS 'Leave type definitions for leave management';
COMMENT ON COLUMN leave_types.id IS 'Primary key - auto-increment';
COMMENT ON COLUMN leave_types.name IS 'Leave type name (SICK, CASUAL, EMERGENCY, MATERNITY, PATERNITY)';
COMMENT ON COLUMN leave_types.max_days_per_year IS 'Maximum days allowed per year for this leave type';
COMMENT ON COLUMN leave_types.requires_medical_certificate IS 'Flag indicating if medical certificate is required';

-- Multi-tenancy: every row belongs to one school
CREATE INDEX IF NOT EXISTS idx_leave_types_school_id ON leave_types (school_id);
CREATE UNIQUE INDEX IF NOT EXISTS leave_types_school_name_unique ON leave_types (school_id, name);
COMMENT ON COLUMN leave_types.school_id IS 'School (tenant) this row belongs to';
