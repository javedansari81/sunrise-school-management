-- =====================================================
-- Table: session_years
-- Description: Stores academic session years (e.g., 2024-25)
-- Dependencies: None (metadata table)
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS session_years CASCADE;

-- Create table
CREATE TABLE session_years (
    id INTEGER PRIMARY KEY,
    name VARCHAR(20) NOT NULL UNIQUE,
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
COMMENT ON COLUMN session_years.id IS 'Primary key - manually assigned ID';
COMMENT ON COLUMN session_years.name IS 'Session year name (e.g., 2024-25)';
COMMENT ON COLUMN session_years.is_current IS 'Flag indicating the current active session';

