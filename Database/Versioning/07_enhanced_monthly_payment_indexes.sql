-- Enhanced Monthly Payment System - Performance Indexes
-- Date: 2025-08-01
-- Description: Add indexes to improve performance for month-wise payment queries

-- Index for monthly fee tracking queries by student and session
CREATE INDEX IF NOT EXISTS idx_monthly_fee_tracking_student_session 
ON monthly_fee_tracking(student_id, session_year_id, academic_month);

-- Index for monthly payment allocations
CREATE INDEX IF NOT EXISTS idx_monthly_payment_allocations_tracking 
ON monthly_payment_allocations(monthly_tracking_id);

-- Index for fee payments by date
CREATE INDEX IF NOT EXISTS idx_fee_payments_date 
ON fee_payments(payment_date);

-- Index for fee records by student and session
CREATE INDEX IF NOT EXISTS idx_fee_records_student_session 
ON fee_records(student_id, session_year_id);

-- Index for students by class (for fee structure lookup)
CREATE INDEX IF NOT EXISTS idx_students_class_session 
ON students(class_id, session_year_id);

-- Composite index for efficient payment history queries
CREATE INDEX IF NOT EXISTS idx_monthly_fee_tracking_composite 
ON monthly_fee_tracking(student_id, session_year_id, academic_month, payment_status_id);

-- Add a check constraint to ensure academic months are valid (1-12)
ALTER TABLE monthly_fee_tracking 
ADD CONSTRAINT IF NOT EXISTS chk_academic_month_valid 
CHECK (academic_month >= 1 AND academic_month <= 12);

-- Add a check constraint to ensure paid amount is not negative
ALTER TABLE monthly_fee_tracking 
ADD CONSTRAINT IF NOT EXISTS chk_paid_amount_positive 
CHECK (paid_amount >= 0);

-- Add a check constraint to ensure monthly amount is positive
ALTER TABLE monthly_fee_tracking 
ADD CONSTRAINT IF NOT EXISTS chk_monthly_amount_positive 
CHECK (monthly_amount > 0);

-- Add a check constraint to ensure allocation amount is positive
ALTER TABLE monthly_payment_allocations 
ADD CONSTRAINT IF NOT EXISTS chk_allocation_amount_positive 
CHECK (amount > 0);

-- Add a comment to document the enhanced payment system
COMMENT ON TABLE monthly_fee_tracking IS 'Enhanced monthly fee tracking system supporting partial payments, multi-month payments, and automatic allocation. Prevents duplicate payments for already-paid months.';

COMMENT ON TABLE monthly_payment_allocations IS 'Links fee payments to specific months with automatic allocation logic. Supports scenarios like 3200 rs = 3 full months + 200 rs partial for 4th month.';

-- Create a view for easy payment summary queries
CREATE OR REPLACE VIEW v_student_payment_summary AS
SELECT 
    s.id as student_id,
    s.first_name || ' ' || s.last_name as student_name,
    s.admission_number,
    c.name as class_name,
    sy.name as session_year,
    COUNT(mft.id) as total_months,
    COUNT(CASE WHEN mft.paid_amount >= mft.monthly_amount THEN 1 END) as paid_months,
    COUNT(CASE WHEN mft.paid_amount > 0 AND mft.paid_amount < mft.monthly_amount THEN 1 END) as partial_months,
    COUNT(CASE WHEN mft.paid_amount = 0 THEN 1 END) as pending_months,
    SUM(mft.monthly_amount) as total_annual_fee,
    SUM(mft.paid_amount) as total_paid,
    SUM(mft.monthly_amount - mft.paid_amount) as total_balance
FROM students s
LEFT JOIN classes c ON s.class_id = c.id
LEFT JOIN session_years sy ON s.session_year_id = sy.id
LEFT JOIN monthly_fee_tracking mft ON s.id = mft.student_id AND s.session_year_id = mft.session_year_id
GROUP BY s.id, s.first_name, s.last_name, s.admission_number, c.name, sy.name;

COMMENT ON VIEW v_student_payment_summary IS 'Comprehensive view showing payment summary for each student including paid, partial, and pending months.';
