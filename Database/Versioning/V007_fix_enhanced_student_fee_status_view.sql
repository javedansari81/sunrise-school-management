-- V007: Fix enhanced_student_fee_status view to handle soft delete columns
-- This script updates the enhanced_student_fee_status view to properly exclude soft-deleted students
-- Date: 2025-08-04
-- Issue: Monthly tracking functionality broken after adding soft delete columns

-- Drop existing view if it exists
DROP VIEW IF EXISTS enhanced_student_fee_status CASCADE;

-- Create the updated enhanced_student_fee_status view with soft delete handling
CREATE OR REPLACE VIEW enhanced_student_fee_status AS
SELECT 
    s.id as student_id,
    s.admission_number,
    s.first_name || ' ' || s.last_name as student_name,
    c.display_name as class_name,
    sy.name as session_year,
    
    -- From existing fee_records
    fr.id as fee_record_id,
    fr.total_amount as annual_fee,
    fr.paid_amount as total_paid,
    fr.balance_amount as total_balance,
    
    -- Monthly tracking statistics
    COALESCE(monthly_stats.total_months_tracked, 0) as total_months_tracked,
    COALESCE(monthly_stats.paid_months, 0) as paid_months,
    COALESCE(monthly_stats.pending_months, 0) as pending_months,
    COALESCE(monthly_stats.overdue_months, 0) as overdue_months,
    COALESCE(monthly_stats.monthly_total, 0) as monthly_total,
    COALESCE(monthly_stats.monthly_paid, 0) as monthly_paid,
    COALESCE(monthly_stats.monthly_balance, 0) as monthly_balance,
    
    -- Collection percentage
    CASE 
        WHEN COALESCE(monthly_stats.monthly_total, 0) > 0 THEN
            ROUND((COALESCE(monthly_stats.monthly_paid, 0) / monthly_stats.monthly_total) * 100, 2)
        WHEN fr.total_amount > 0 THEN
            ROUND((fr.paid_amount / fr.total_amount) * 100, 2)
        ELSE 0
    END as collection_percentage,
    
    -- Has monthly tracking enabled
    CASE 
        WHEN monthly_stats.total_months_tracked > 0 THEN true
        WHEN fr.is_monthly_tracked = true THEN true
        ELSE false
    END as has_monthly_tracking

FROM students s
LEFT JOIN classes c ON s.class_id = c.id
LEFT JOIN session_years sy ON s.session_year_id = sy.id
LEFT JOIN fee_records fr ON s.id = fr.student_id AND s.session_year_id = fr.session_year_id
LEFT JOIN (
    -- Subquery to get monthly tracking statistics
    SELECT 
        mft.student_id,
        mft.session_year_id,
        COUNT(*) as total_months_tracked,
        COUNT(CASE WHEN ps.name = 'PAID' THEN 1 END) as paid_months,
        COUNT(CASE WHEN ps.name = 'PENDING' THEN 1 END) as pending_months,
        COUNT(CASE WHEN ps.name = 'OVERDUE' THEN 1 END) as overdue_months,
        SUM(mft.monthly_amount) as monthly_total,
        SUM(mft.paid_amount) as monthly_paid,
        SUM(mft.balance_amount) as monthly_balance
    FROM monthly_fee_tracking mft
    LEFT JOIN payment_statuses ps ON mft.payment_status_id = ps.id
    GROUP BY mft.student_id, mft.session_year_id
) monthly_stats ON s.id = monthly_stats.student_id AND s.session_year_id = monthly_stats.session_year_id

-- Updated WHERE clause to handle soft delete columns
WHERE s.is_active = true 
  AND (s.is_deleted = false OR s.is_deleted IS NULL);

COMMENT ON VIEW enhanced_student_fee_status IS 'Enhanced student fee summary combining legacy and monthly tracking data - Updated to handle soft delete columns';

-- Create indexes for better performance (only if they don't exist)
CREATE INDEX IF NOT EXISTS idx_enhanced_fee_status_session_year 
ON students(session_year_id) WHERE is_active = true AND (is_deleted = false OR is_deleted IS NULL);

CREATE INDEX IF NOT EXISTS idx_enhanced_fee_status_class 
ON students(class_id) WHERE is_active = true AND (is_deleted = false OR is_deleted IS NULL);

-- Grant permissions
GRANT SELECT ON enhanced_student_fee_status TO PUBLIC;

-- Add comment for tracking this fix
COMMENT ON VIEW enhanced_student_fee_status IS 'Enhanced student fee summary view - Fixed in V007 to properly handle soft delete columns (is_deleted, deleted_date) added in V004';

-- =====================================================
-- Update other views that reference students table
-- =====================================================

-- Update student_summary view to handle soft delete
DROP VIEW IF EXISTS student_summary CASCADE;
CREATE OR REPLACE VIEW student_summary AS
SELECT
    s.id,
    s.admission_number,
    s.first_name || ' ' || s.last_name AS full_name,
    c.display_name AS class,
    s.section,
    sy.name AS session_year,
    g.name AS gender,
    s.father_name,
    s.father_phone,
    s.mother_name,
    s.mother_phone,
    s.is_active,
    calculate_age(s.date_of_birth) AS age
FROM students s
LEFT JOIN classes c ON s.class_id = c.id
LEFT JOIN session_years sy ON s.session_year_id = sy.id
LEFT JOIN genders g ON s.gender_id = g.id
WHERE s.is_active = true
  AND (s.is_deleted = false OR s.is_deleted IS NULL);

COMMENT ON VIEW student_summary IS 'Student summary view - Updated to handle soft delete columns';

-- Update fee_collection_summary view to handle soft delete
DROP VIEW IF EXISTS fee_collection_summary CASCADE;
CREATE OR REPLACE VIEW fee_collection_summary AS
SELECT
    sy.name AS session_year,
    c.display_name AS class,
    pt.name AS payment_type,
    ps.name AS payment_status,
    COUNT(*) AS total_students,
    SUM(fr.total_amount) AS total_fees,
    SUM(fr.paid_amount) AS collected_amount,
    SUM(fr.balance_amount) AS pending_amount,
    ROUND((SUM(fr.paid_amount) * 100.0 / NULLIF(SUM(fr.total_amount), 0)), 2) AS collection_percentage
FROM fee_records fr
JOIN students s ON fr.student_id = s.id
JOIN session_years sy ON fr.session_year_id = sy.id
JOIN classes c ON s.class_id = c.id
JOIN payment_types pt ON fr.payment_type_id = pt.id
JOIN payment_statuses ps ON fr.payment_status_id = ps.id
WHERE s.is_active = true
  AND (s.is_deleted = false OR s.is_deleted IS NULL)
GROUP BY sy.name, c.display_name, pt.name, ps.name;

COMMENT ON VIEW fee_collection_summary IS 'Fee collection summary view - Updated to handle soft delete columns';

-- Update student_fee_summary view to handle soft delete
DROP VIEW IF EXISTS student_fee_summary CASCADE;
CREATE OR REPLACE VIEW student_fee_summary AS
SELECT
    s.id as student_id,
    s.admission_number,
    s.first_name,
    s.last_name,
    c.display_name as class_name,
    sy.name as session_year,
    COUNT(mfr.id) as total_months,
    COUNT(CASE WHEN mfr.payment_status_id = 3 THEN 1 END) as paid_months,
    COUNT(CASE WHEN mfr.payment_status_id = 1 THEN 1 END) as pending_months,
    COUNT(CASE WHEN mfr.payment_status_id = 4 THEN 1 END) as overdue_months,
    SUM(mfr.monthly_amount) as total_annual_fee,
    SUM(mfr.paid_amount) as total_paid,
    SUM(mfr.balance_amount) as total_balance,
    SUM(mfr.late_fee) as total_late_fee
FROM students s
JOIN classes c ON s.class_id = c.id
JOIN session_years sy ON s.session_year_id = sy.id
LEFT JOIN monthly_fee_records mfr ON s.id = mfr.student_id AND s.session_year_id = mfr.session_year_id
WHERE s.is_active = true
  AND (s.is_deleted = false OR s.is_deleted IS NULL)
GROUP BY s.id, s.admission_number, s.first_name, s.last_name, c.display_name, sy.name;

COMMENT ON VIEW student_fee_summary IS 'Comprehensive fee summary for each student - Updated to handle soft delete columns';

-- Update overdue_fees_summary view to handle soft delete
DROP VIEW IF EXISTS overdue_fees_summary CASCADE;
CREATE OR REPLACE VIEW overdue_fees_summary AS
SELECT
    s.id as student_id,
    s.admission_number,
    s.first_name || ' ' || s.last_name as student_name,
    c.display_name as class_name,
    mfr.month,
    mfr.year,
    mfr.monthly_amount,
    mfr.paid_amount,
    mfr.balance_amount,
    mfr.due_date,
    CURRENT_DATE - mfr.due_date as days_overdue,
    mfr.late_fee
FROM students s
JOIN classes c ON s.class_id = c.id
JOIN monthly_fee_records mfr ON s.id = mfr.student_id
WHERE mfr.payment_status_id = 4 -- Overdue status
  AND s.is_active = true
  AND (s.is_deleted = false OR s.is_deleted IS NULL)
ORDER BY mfr.due_date ASC;

COMMENT ON VIEW overdue_fees_summary IS 'All overdue fee records with student details - Updated to handle soft delete columns';

-- Update v_student_payment_summary view to handle soft delete
DROP VIEW IF EXISTS v_student_payment_summary CASCADE;
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
WHERE s.is_active = true
  AND (s.is_deleted = false OR s.is_deleted IS NULL)
GROUP BY s.id, s.first_name, s.last_name, s.admission_number, c.name, sy.name;

COMMENT ON VIEW v_student_payment_summary IS 'Student payment summary view - Updated to handle soft delete columns';

-- Grant permissions to all updated views
GRANT SELECT ON student_summary TO PUBLIC;
GRANT SELECT ON fee_collection_summary TO PUBLIC;
GRANT SELECT ON student_fee_summary TO PUBLIC;
GRANT SELECT ON overdue_fees_summary TO PUBLIC;
GRANT SELECT ON v_student_payment_summary TO PUBLIC;
