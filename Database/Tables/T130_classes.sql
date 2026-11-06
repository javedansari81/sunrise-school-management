-- =====================================================
-- Table: classes
-- Description: Stores class definitions (Pre-Nursery to Class 12)
-- Dependencies: None (metadata table)
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS classes CASCADE;

-- Create table
CREATE TABLE classes (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id),
    name VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    sort_order INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Add comments
COMMENT ON TABLE classes IS 'Class definitions from Pre-Nursery to Class 12';
COMMENT ON COLUMN classes.id IS 'Primary key - auto-increment';
COMMENT ON COLUMN classes.name IS 'Class name (e.g., CLASS_1, CLASS_2)';
COMMENT ON COLUMN classes.sort_order IS 'Order for displaying classes';

-- Multi-tenancy: every row belongs to one school
CREATE INDEX IF NOT EXISTS idx_classes_school_id ON classes (school_id);
CREATE UNIQUE INDEX IF NOT EXISTS classes_school_name_unique ON classes (school_id, name);
COMMENT ON COLUMN classes.school_id IS 'School (tenant) this row belongs to';
