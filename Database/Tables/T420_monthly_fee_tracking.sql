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
    student_id INTEGER NOT NULL,
    session_year_id INTEGER NOT NULL,
    month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
    year INTEGER NOT NULL,
    monthly_fee_amount DECIMAL(10,2) NOT NULL,
    paid_amount DECIMAL(10,2) DEFAULT 0.00,
    balance_amount DECIMAL(10,2) NOT NULL,
    payment_status_id INTEGER DEFAULT 1,
    due_date DATE,
    paid_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (session_year_id) REFERENCES session_years(id),
    FOREIGN KEY (payment_status_id) REFERENCES payment_statuses(id),
    UNIQUE(student_id, session_year_id, month, year)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_monthly_fee_student ON monthly_fee_tracking(student_id);
CREATE INDEX IF NOT EXISTS idx_monthly_fee_session ON monthly_fee_tracking(session_year_id);

-- Add comments
COMMENT ON TABLE monthly_fee_tracking IS 'Monthly fee tracking for students';
COMMENT ON COLUMN monthly_fee_tracking.month IS 'Month number (1-12)';
COMMENT ON COLUMN monthly_fee_tracking.year IS 'Year';
COMMENT ON COLUMN monthly_fee_tracking.balance_amount IS 'Remaining balance for this month';

