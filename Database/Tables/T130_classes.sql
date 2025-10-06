-- =====================================================
-- Table: classes
-- Description: Stores class definitions (Pre-Nursery to Class 12)
-- Dependencies: None (metadata table)
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS classes CASCADE;

-- Create table
CREATE TABLE classes (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    sort_order INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Add comments
COMMENT ON TABLE classes IS 'Class definitions from Pre-Nursery to Class 12';
COMMENT ON COLUMN classes.id IS 'Primary key - manually assigned ID';
COMMENT ON COLUMN classes.name IS 'Class name (e.g., CLASS_1, CLASS_2)';
COMMENT ON COLUMN classes.sort_order IS 'Order for displaying classes';

