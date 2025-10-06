-- =====================================================
-- Table: fee_records
-- Description: Stores student fee records
-- Dependencies: students, session_years, classes, payment_types, payment_statuses
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS fee_records CASCADE;

-- Create table
CREATE TABLE fee_records (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL,
    session_year_id INTEGER NOT NULL,
    class_id INTEGER NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    paid_amount DECIMAL(10,2) DEFAULT 0.00,
    balance_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    payment_type_id INTEGER NOT NULL DEFAULT 1,
    payment_status_id INTEGER NOT NULL DEFAULT 1,
    due_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (session_year_id) REFERENCES session_years(id),
    FOREIGN KEY (class_id) REFERENCES classes(id),
    FOREIGN KEY (payment_type_id) REFERENCES payment_types(id),
    FOREIGN KEY (payment_status_id) REFERENCES payment_statuses(id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_fee_records_student ON fee_records(student_id);
CREATE INDEX IF NOT EXISTS idx_fee_records_session ON fee_records(session_year_id);

-- Add comments
COMMENT ON TABLE fee_records IS 'Student fee records';
COMMENT ON COLUMN fee_records.student_id IS 'Foreign key to students table';
COMMENT ON COLUMN fee_records.balance_amount IS 'Calculated as total_amount - paid_amount';

