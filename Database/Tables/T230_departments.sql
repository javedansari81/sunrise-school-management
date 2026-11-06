-- =====================================================
-- Table: departments
-- Description: Stores department options for teachers
-- Dependencies: None (metadata table)
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS departments CASCADE;

-- Create table
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id),
    name VARCHAR(50) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Add comments
COMMENT ON TABLE departments IS 'Department options for teachers';
COMMENT ON COLUMN departments.id IS 'Primary key - auto-increment';
COMMENT ON COLUMN departments.name IS 'Department name (e.g., SCIENCE, MATHEMATICS, ENGLISH, etc.)';
COMMENT ON COLUMN departments.description IS 'Department description';
COMMENT ON COLUMN departments.is_active IS 'Whether the department is active';

-- Create indexes
CREATE INDEX idx_departments_name ON departments(name);
CREATE INDEX idx_departments_is_active ON departments(is_active);

-- Success message

-- Multi-tenancy: every row belongs to one school
CREATE INDEX IF NOT EXISTS idx_departments_school_id ON departments (school_id);
CREATE UNIQUE INDEX IF NOT EXISTS departments_school_name_unique ON departments (school_id, name);
COMMENT ON COLUMN departments.school_id IS 'School (tenant) this row belongs to';
