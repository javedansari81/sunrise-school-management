-- =====================================================
-- Table: session_years
-- Description: Stores academic session years (e.g., 2024-25)
-- Dependencies: None (metadata table)
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS session_years CASCADE;

-- Create table
CREATE TABLE session_years (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id),
    name VARCHAR(20) NOT NULL,
    description TEXT NOT NULL,
    start_date DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Add comments
COMMENT ON TABLE session_years IS 'Academic session years (April to March in India)';
COMMENT ON COLUMN session_years.id IS 'Primary key - auto-increment';
COMMENT ON COLUMN session_years.name IS 'Session year name (e.g., 2024-25)';
COMMENT ON COLUMN session_years.is_current IS 'Flag indicating the current active session';

-- Multi-tenancy: every row belongs to one school
CREATE INDEX IF NOT EXISTS idx_session_years_school_id ON session_years (school_id);
CREATE UNIQUE INDEX IF NOT EXISTS session_years_school_name_unique ON session_years (school_id, name);
COMMENT ON COLUMN session_years.school_id IS 'School (tenant) this row belongs to';
