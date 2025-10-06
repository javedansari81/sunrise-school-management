-- =====================================================
-- Table: user_types
-- Description: Stores user role definitions (ADMIN, TEACHER, STUDENT, STAFF, PARENT)
-- Dependencies: None (metadata table)
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS user_types CASCADE;

-- Create table
CREATE TABLE user_types (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Add comments
COMMENT ON TABLE user_types IS 'User role definitions for the system';
COMMENT ON COLUMN user_types.id IS 'Primary key - manually assigned ID';
COMMENT ON COLUMN user_types.name IS 'Unique role name (e.g., ADMIN, TEACHER, STUDENT)';
COMMENT ON COLUMN user_types.description IS 'Human-readable description of the role';
COMMENT ON COLUMN user_types.is_active IS 'Flag to enable/disable the role';

