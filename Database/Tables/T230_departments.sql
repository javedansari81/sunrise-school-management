-- =====================================================
-- Table: departments
-- Description: Stores department options for teachers
-- Dependencies: None (metadata table)
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS departments CASCADE;

-- Create table
CREATE TABLE departments (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Add comments
COMMENT ON TABLE departments IS 'Department options for teachers';
COMMENT ON COLUMN departments.id IS 'Primary key - manually assigned ID';
COMMENT ON COLUMN departments.name IS 'Department name (e.g., SCIENCE, MATHEMATICS, ENGLISH, etc.)';
COMMENT ON COLUMN departments.description IS 'Department description';
COMMENT ON COLUMN departments.is_active IS 'Whether the department is active';

-- Create indexes
CREATE INDEX idx_departments_name ON departments(name);
CREATE INDEX idx_departments_is_active ON departments(is_active);

-- Success message

