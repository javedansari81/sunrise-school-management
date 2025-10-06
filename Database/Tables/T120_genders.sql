-- =====================================================
-- Table: genders
-- Description: Stores gender options (MALE, FEMALE, OTHER)
-- Dependencies: None (metadata table)
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS genders CASCADE;

-- Create table
CREATE TABLE genders (
    id INTEGER PRIMARY KEY,
    name VARCHAR(20) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Add comments
COMMENT ON TABLE genders IS 'Gender options for users';
COMMENT ON COLUMN genders.id IS 'Primary key - manually assigned ID';
COMMENT ON COLUMN genders.name IS 'Gender name (MALE, FEMALE, OTHER)';

