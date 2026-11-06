-- =====================================================
-- Table: positions
-- Description: Stores position/designation options for teachers
-- Dependencies: None (metadata table)
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS positions CASCADE;

-- Create table
CREATE TABLE positions (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id),
    name VARCHAR(50) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Add comments
COMMENT ON TABLE positions IS 'Position/designation options for teachers';
COMMENT ON COLUMN positions.id IS 'Primary key - auto-increment';
COMMENT ON COLUMN positions.name IS 'Position name (e.g., PRINCIPAL, VICE_PRINCIPAL, HEAD_TEACHER, TEACHER, etc.)';
COMMENT ON COLUMN positions.description IS 'Position description';
COMMENT ON COLUMN positions.is_active IS 'Whether the position is active';

-- Create indexes
CREATE INDEX idx_positions_name ON positions(name);
CREATE INDEX idx_positions_is_active ON positions(is_active);

-- Success message

-- Multi-tenancy: every row belongs to one school
CREATE INDEX IF NOT EXISTS idx_positions_school_id ON positions (school_id);
CREATE UNIQUE INDEX IF NOT EXISTS positions_school_name_unique ON positions (school_id, name);
COMMENT ON COLUMN positions.school_id IS 'School (tenant) this row belongs to';
