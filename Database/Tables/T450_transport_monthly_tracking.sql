-- =====================================================
-- Table: transport_monthly_tracking
-- Description: Month-wise tracking of transport fees for students
-- Dependencies: student_transport_enrollment, students, session_years, payment_statuses
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS transport_monthly_tracking CASCADE;

-- Create table
CREATE TABLE transport_monthly_tracking (
    id SERIAL PRIMARY KEY,
    enrollment_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    session_year_id INTEGER NOT NULL,
    
    -- Month Details
    academic_month INTEGER NOT NULL CHECK (academic_month BETWEEN 1 AND 12),
    academic_year INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    
    -- Service Status
    is_service_enabled BOOLEAN DEFAULT TRUE,
    
    -- Amount Details
    monthly_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    paid_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    balance_amount DECIMAL(10,2) GENERATED ALWAYS AS (
        CASE 
            WHEN is_service_enabled THEN monthly_amount - paid_amount 
            ELSE 0.00 
        END
    ) STORED,
    
    -- Payment Status
    due_date DATE NOT NULL,
    payment_status_id INTEGER DEFAULT 1,
    
    -- Additional
    late_fee DECIMAL(10,2) DEFAULT 0.00,
    discount_amount DECIMAL(10,2) DEFAULT 0.00,
    remarks TEXT,
    
    -- Audit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    
    -- Foreign Key Constraints
    FOREIGN KEY (enrollment_id) REFERENCES student_transport_enrollment(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (session_year_id) REFERENCES session_years(id),
    FOREIGN KEY (payment_status_id) REFERENCES payment_statuses(id),
    
    -- Unique constraint
    UNIQUE(student_id, session_year_id, academic_month, academic_year)
);

-- Add indexes
CREATE INDEX idx_transport_monthly_enrollment ON transport_monthly_tracking(enrollment_id);
CREATE INDEX idx_transport_monthly_student ON transport_monthly_tracking(student_id);
CREATE INDEX idx_transport_monthly_session ON transport_monthly_tracking(session_year_id);
CREATE INDEX idx_transport_monthly_status ON transport_monthly_tracking(payment_status_id);
CREATE INDEX idx_transport_monthly_service_enabled ON transport_monthly_tracking(is_service_enabled);

-- Add comments
COMMENT ON TABLE transport_monthly_tracking IS 'Monthly transport fee tracking for students - stores month-wise payment records';
COMMENT ON COLUMN transport_monthly_tracking.enrollment_id IS 'Foreign key to student_transport_enrollment table';
COMMENT ON COLUMN transport_monthly_tracking.student_id IS 'Foreign key to students table';
COMMENT ON COLUMN transport_monthly_tracking.session_year_id IS 'Foreign key to session_years table';
COMMENT ON COLUMN transport_monthly_tracking.academic_month IS 'Academic month number (1-12, where 4=April, 1=January)';
COMMENT ON COLUMN transport_monthly_tracking.academic_year IS 'Academic year (e.g., 2025 for Apr-Dec, 2026 for Jan-Mar)';
COMMENT ON COLUMN transport_monthly_tracking.month_name IS 'Month name (April, May, etc.)';
COMMENT ON COLUMN transport_monthly_tracking.is_service_enabled IS 'Whether transport service is enabled for this month';
COMMENT ON COLUMN transport_monthly_tracking.monthly_amount IS 'Monthly transport fee amount';
COMMENT ON COLUMN transport_monthly_tracking.paid_amount IS 'Amount paid for this month';
COMMENT ON COLUMN transport_monthly_tracking.balance_amount IS 'Calculated balance (0 if service disabled)';
COMMENT ON COLUMN transport_monthly_tracking.due_date IS 'Payment due date for this month';
COMMENT ON COLUMN transport_monthly_tracking.payment_status_id IS 'Foreign key to payment_statuses table';

