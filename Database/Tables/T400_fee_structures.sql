-- =====================================================
-- Table: fee_structures
-- Description: Stores fee structure definitions by class and session
-- Dependencies: classes, session_years
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS fee_structures CASCADE;

-- Create table
CREATE TABLE fee_structures (
    id SERIAL PRIMARY KEY,
    class_id INTEGER NOT NULL,
    session_year_id INTEGER NOT NULL,
    fee_type VARCHAR(50) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    due_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (class_id) REFERENCES classes(id),
    FOREIGN KEY (session_year_id) REFERENCES session_years(id)
);

-- Add comments
COMMENT ON TABLE fee_structures IS 'Fee structure definitions by class and session';
COMMENT ON COLUMN fee_structures.class_id IS 'Foreign key to classes table';
COMMENT ON COLUMN fee_structures.session_year_id IS 'Foreign key to session_years table';
COMMENT ON COLUMN fee_structures.fee_type IS 'Type of fee (e.g., TUITION, TRANSPORT, EXAM)';
COMMENT ON COLUMN fee_structures.amount IS 'Fee amount';

