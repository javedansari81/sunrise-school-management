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

    -- Foreign keys to metadata tables
    payment_type_id INTEGER NOT NULL DEFAULT 1,
    payment_status_id INTEGER NOT NULL DEFAULT 1,
    payment_method_id INTEGER,

    -- Enhanced fields for new system
    fee_structure_id INTEGER,
    is_monthly_tracked BOOLEAN DEFAULT FALSE,
    academic_month INTEGER,
    academic_year INTEGER,

    -- Fee Details
    total_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    paid_amount DECIMAL(10,2) DEFAULT 0.00,
    balance_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,

    -- Sibling waiver columns (from V010)
    has_sibling_waiver BOOLEAN DEFAULT FALSE,
    sibling_waiver_percentage DECIMAL(5,2) DEFAULT 0.00 CHECK (sibling_waiver_percentage >= 0 AND sibling_waiver_percentage <= 100),
    original_total_amount DECIMAL(10,2),

    -- Due Date
    due_date DATE,

    -- Payment Details (for single payment records)
    transaction_id VARCHAR(100),
    payment_date DATE,

    -- Additional Info
    remarks TEXT,

    -- System fields
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    -- Foreign Key Constraints
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (session_year_id) REFERENCES session_years(id),
    FOREIGN KEY (class_id) REFERENCES classes(id),
    FOREIGN KEY (payment_type_id) REFERENCES payment_types(id),
    FOREIGN KEY (payment_status_id) REFERENCES payment_statuses(id),
    FOREIGN KEY (payment_method_id) REFERENCES payment_methods(id),
    FOREIGN KEY (fee_structure_id) REFERENCES fee_structures(id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_fee_records_student ON fee_records(student_id);
CREATE INDEX IF NOT EXISTS idx_fee_records_session ON fee_records(session_year_id);
CREATE INDEX IF NOT EXISTS idx_fee_records_monthly_tracked ON fee_records(is_monthly_tracked) WHERE is_monthly_tracked = TRUE;
CREATE INDEX IF NOT EXISTS idx_fee_records_sibling_waiver ON fee_records(has_sibling_waiver) WHERE has_sibling_waiver = TRUE;

-- Add comments
COMMENT ON TABLE fee_records IS 'Student fee records';
COMMENT ON COLUMN fee_records.student_id IS 'Foreign key to students table';
COMMENT ON COLUMN fee_records.payment_method_id IS 'Foreign key to payment_methods table';
COMMENT ON COLUMN fee_records.fee_structure_id IS 'Foreign key to fee_structures table';
COMMENT ON COLUMN fee_records.is_monthly_tracked IS 'Whether this fee record uses monthly tracking system';
COMMENT ON COLUMN fee_records.academic_month IS 'Academic month (1-12, where 4=April)';
COMMENT ON COLUMN fee_records.academic_year IS 'Academic year (e.g., 2025)';
COMMENT ON COLUMN fee_records.balance_amount IS 'Calculated as total_amount - paid_amount';
COMMENT ON COLUMN fee_records.has_sibling_waiver IS 'Whether this fee record has a sibling-based waiver applied';
COMMENT ON COLUMN fee_records.sibling_waiver_percentage IS 'Percentage of fee waived due to sibling discount (0-100)';
COMMENT ON COLUMN fee_records.original_total_amount IS 'Original total amount before sibling waiver applied';
COMMENT ON COLUMN fee_records.transaction_id IS 'Payment transaction ID';
COMMENT ON COLUMN fee_records.payment_date IS 'Date of payment';
COMMENT ON COLUMN fee_records.remarks IS 'Additional remarks or notes';

