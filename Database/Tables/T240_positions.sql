-- =====================================================
-- Table: positions
-- Description: Stores position/designation options for teachers
-- Dependencies: None (metadata table)
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS positions CASCADE;

-- Create table
CREATE TABLE positions (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Add comments
COMMENT ON TABLE positions IS 'Position/designation options for teachers';
COMMENT ON COLUMN positions.id IS 'Primary key - manually assigned ID';
COMMENT ON COLUMN positions.name IS 'Position name (e.g., PRINCIPAL, VICE_PRINCIPAL, HEAD_TEACHER, TEACHER, etc.)';
COMMENT ON COLUMN positions.description IS 'Position description';
COMMENT ON COLUMN positions.is_active IS 'Whether the position is active';

-- Create indexes
CREATE INDEX idx_positions_name ON positions(name);
CREATE INDEX idx_positions_is_active ON positions(is_active);

-- Success message
\echo 'Table positions created successfully'

