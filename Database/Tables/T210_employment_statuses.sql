-- =====================================================
-- Table: employment_statuses
-- Description: Stores employment status options for teachers
-- Dependencies: None (metadata table)
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS employment_statuses CASCADE;

-- Create table
CREATE TABLE employment_statuses (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Add comments
COMMENT ON TABLE employment_statuses IS 'Employment status options for teachers';
COMMENT ON COLUMN employment_statuses.id IS 'Primary key - manually assigned ID';
COMMENT ON COLUMN employment_statuses.name IS 'Status name (FULL_TIME, PART_TIME, CONTRACT, PROBATION, RESIGNED, TERMINATED)';

