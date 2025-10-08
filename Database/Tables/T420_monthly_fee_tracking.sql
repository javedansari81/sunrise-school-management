-- =====================================================
-- Table: monthly_fee_tracking
-- Description: Stores monthly fee tracking records for students
-- Dependencies: students, session_years, payment_statuses
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS monthly_fee_tracking CASCADE;

-- Create table
CREATE TABLE monthly_fee_tracking (
    id SERIAL PRIMARY KEY,
    fee_record_id INTEGER,
    student_id INTEGER NOT NULL,
    session_year_id INTEGER NOT NULL,
    academic_month INTEGER NOT NULL CHECK (academic_month BETWEEN 1 AND 12),
    academic_year INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    monthly_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    paid_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    balance_amount DECIMAL(10,2) GENERATED ALWAYS AS (monthly_amount - paid_amount) STORED,
    due_date DATE NOT NULL,
    payment_status_id INTEGER DEFAULT 1,
    late_fee DECIMAL(10,2) DEFAULT 0.00,
    discount_amount DECIMAL(10,2) DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (fee_record_id) REFERENCES fee_records(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (session_year_id) REFERENCES session_years(id),
    FOREIGN KEY (payment_status_id) REFERENCES payment_statuses(id),
    UNIQUE(student_id, session_year_id, academic_month, academic_year)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_monthly_fee_student ON monthly_fee_tracking(student_id);
CREATE INDEX IF NOT EXISTS idx_monthly_fee_session ON monthly_fee_tracking(session_year_id);
CREATE INDEX IF NOT EXISTS idx_monthly_fee_record ON monthly_fee_tracking(fee_record_id);
CREATE INDEX IF NOT EXISTS idx_monthly_fee_status ON monthly_fee_tracking(payment_status_id);

-- Add comments
COMMENT ON TABLE monthly_fee_tracking IS 'Monthly fee tracking for students - stores month-wise payment records';
COMMENT ON COLUMN monthly_fee_tracking.fee_record_id IS 'Foreign key to fee_records table';
COMMENT ON COLUMN monthly_fee_tracking.academic_month IS 'Academic month number (1-12, where 4=April, 1=January)';
COMMENT ON COLUMN monthly_fee_tracking.academic_year IS 'Academic year (e.g., 2025 for Apr-Dec, 2026 for Jan-Mar)';
COMMENT ON COLUMN monthly_fee_tracking.month_name IS 'Month name (April, May, etc.)';
COMMENT ON COLUMN monthly_fee_tracking.monthly_amount IS 'Monthly fee amount for this month';
COMMENT ON COLUMN monthly_fee_tracking.paid_amount IS 'Amount paid for this month';
COMMENT ON COLUMN monthly_fee_tracking.balance_amount IS 'Computed: Remaining balance (monthly_amount - paid_amount)';
COMMENT ON COLUMN monthly_fee_tracking.due_date IS 'Due date for this month (typically 10th of the month)';
COMMENT ON COLUMN monthly_fee_tracking.late_fee IS 'Late fee charged if payment is overdue';
COMMENT ON COLUMN monthly_fee_tracking.discount_amount IS 'Discount applied to this month';

