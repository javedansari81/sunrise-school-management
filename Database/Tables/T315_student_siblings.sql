-- =====================================================
-- Table: student_siblings
-- Description: Stores sibling relationships between students for fee waiver management
-- Dependencies: students table
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS student_siblings CASCADE;

-- Create table
CREATE TABLE student_siblings (
    id SERIAL PRIMARY KEY,
    
    -- Student References
    student_id INTEGER NOT NULL,
    sibling_student_id INTEGER NOT NULL,
    
    -- Relationship Details
    relationship_type VARCHAR(20) DEFAULT 'SIBLING' CHECK (relationship_type IN ('SIBLING', 'TWIN', 'HALF_SIBLING')),
    is_auto_detected BOOLEAN DEFAULT TRUE,
    
    -- Birth Order and Fee Waiver
    birth_order INTEGER NOT NULL CHECK (birth_order > 0),
    fee_waiver_percentage DECIMAL(5,2) DEFAULT 0.00 CHECK (fee_waiver_percentage >= 0 AND fee_waiver_percentage <= 100),
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    
    -- Foreign Keys
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (sibling_student_id) REFERENCES students(id) ON DELETE CASCADE,
    
    -- Constraints
    UNIQUE(student_id, sibling_student_id),
    CHECK (student_id != sibling_student_id)
);

-- Create indexes
CREATE INDEX idx_student_siblings_student_id ON student_siblings(student_id);
CREATE INDEX idx_student_siblings_sibling_student_id ON student_siblings(sibling_student_id);
CREATE INDEX idx_student_siblings_active ON student_siblings(is_active);

-- Add comments
COMMENT ON TABLE student_siblings IS 'Stores sibling relationships between students for fee waiver management';
COMMENT ON COLUMN student_siblings.student_id IS 'Primary student ID';
COMMENT ON COLUMN student_siblings.sibling_student_id IS 'Sibling student ID';
COMMENT ON COLUMN student_siblings.relationship_type IS 'Type of sibling relationship (SIBLING, TWIN, HALF_SIBLING)';
COMMENT ON COLUMN student_siblings.is_auto_detected IS 'Whether relationship was auto-detected by system or manually added';
COMMENT ON COLUMN student_siblings.birth_order IS 'Birth order among all siblings (1=eldest, 2=second, etc.)';
COMMENT ON COLUMN student_siblings.fee_waiver_percentage IS 'Fee waiver percentage applied (0-100)';
COMMENT ON COLUMN student_siblings.is_active IS 'Whether this sibling relationship is currently active';

