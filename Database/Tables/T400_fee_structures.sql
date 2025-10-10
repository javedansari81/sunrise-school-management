-- =====================================================
-- Table: fee_structures
-- Description: Stores fee structure definitions by class and session
-- Dependencies: classes, session_years
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS fee_structures CASCADE;

-- Create table with detailed fee components (matching SQLAlchemy model)
CREATE TABLE fee_structures (
    id SERIAL PRIMARY KEY,

    -- Foreign keys to metadata tables
    class_id INTEGER NOT NULL,
    session_year_id INTEGER NOT NULL,

    -- Fee Components (matching SQLAlchemy model)
    tuition_fee DECIMAL(10,2) DEFAULT 0.0,
    admission_fee DECIMAL(10,2) DEFAULT 0.0,
    development_fee DECIMAL(10,2) DEFAULT 0.0,
    activity_fee DECIMAL(10,2) DEFAULT 0.0,
    transport_fee DECIMAL(10,2) DEFAULT 0.0,
    library_fee DECIMAL(10,2) DEFAULT 0.0,
    lab_fee DECIMAL(10,2) DEFAULT 0.0,
    exam_fee DECIMAL(10,2) DEFAULT 0.0,
    other_fee DECIMAL(10,2) DEFAULT 0.0,

    -- Total (required field)
    total_annual_fee DECIMAL(10,2) NOT NULL DEFAULT 0.0,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    -- Foreign Key Constraints
    FOREIGN KEY (class_id) REFERENCES classes(id),
    FOREIGN KEY (session_year_id) REFERENCES session_years(id)
);

-- Add indexes for performance
CREATE INDEX idx_fee_structures_class_session ON fee_structures(class_id, session_year_id);
CREATE INDEX idx_fee_structures_class_id ON fee_structures(class_id);
CREATE INDEX idx_fee_structures_session_year_id ON fee_structures(session_year_id);

-- Add comments
COMMENT ON TABLE fee_structures IS 'Fee structure definitions by class and session with detailed fee components';
COMMENT ON COLUMN fee_structures.class_id IS 'Foreign key to classes table';
COMMENT ON COLUMN fee_structures.session_year_id IS 'Foreign key to session_years table';
COMMENT ON COLUMN fee_structures.tuition_fee IS 'Tuition fee amount';
COMMENT ON COLUMN fee_structures.admission_fee IS 'Admission fee amount';
COMMENT ON COLUMN fee_structures.development_fee IS 'Development fee amount';
COMMENT ON COLUMN fee_structures.activity_fee IS 'Activity fee amount';
COMMENT ON COLUMN fee_structures.transport_fee IS 'Transport fee amount';
COMMENT ON COLUMN fee_structures.library_fee IS 'Library fee amount';
COMMENT ON COLUMN fee_structures.lab_fee IS 'Lab fee amount';
COMMENT ON COLUMN fee_structures.exam_fee IS 'Exam fee amount';
COMMENT ON COLUMN fee_structures.other_fee IS 'Other miscellaneous fees';
COMMENT ON COLUMN fee_structures.total_annual_fee IS 'Total annual fee (sum of all components)';

