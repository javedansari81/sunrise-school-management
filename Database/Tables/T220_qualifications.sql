-- =====================================================
-- Table: qualifications
-- Description: Stores qualification options for teachers with level ordering
-- Dependencies: None (metadata table)
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS qualifications CASCADE;

-- Create table
CREATE TABLE qualifications (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    level_order INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Add comments
COMMENT ON TABLE qualifications IS 'Qualification options for teachers';
COMMENT ON COLUMN qualifications.id IS 'Primary key - manually assigned ID';
COMMENT ON COLUMN qualifications.name IS 'Qualification name (HIGH_SCHOOL, INTERMEDIATE, DIPLOMA, BACHELORS, MASTERS, PHD, B_ED, M_ED, D_ED)';
COMMENT ON COLUMN qualifications.level_order IS 'Order indicating qualification level (1=lowest, higher=more advanced)';

