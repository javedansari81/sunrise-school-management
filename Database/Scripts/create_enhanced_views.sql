-- =====================================================
-- Create Enhanced Fee Management Views
-- =====================================================

-- Drop existing view if it exists
DROP VIEW IF EXISTS enhanced_student_fee_status CASCADE;

-- Create the enhanced_student_fee_status view
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
    
    -- Monthly tracking data (if available)
    COALESCE(monthly_stats.total_months_tracked, 0) as total_months_tracked,
    COALESCE(monthly_stats.paid_months, 0) as paid_months,
    COALESCE(monthly_stats.pending_months, 0) as pending_months,
    COALESCE(monthly_stats.overdue_months, 0) as overdue_months,
    COALESCE(monthly_stats.monthly_total, 0) as monthly_total,
    COALESCE(monthly_stats.monthly_paid, 0) as monthly_paid,
    COALESCE(monthly_stats.monthly_balance, 0) as monthly_balance,
    
    -- Collection percentage
    CASE 
        WHEN fr.total_amount > 0 THEN 
            ROUND((fr.paid_amount * 100.0 / fr.total_amount), 2)
        ELSE 0 
    END as collection_percentage,
    
    -- Has monthly tracking flag
    CASE 
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

WHERE s.is_active = true
  AND (s.is_deleted = false OR s.is_deleted IS NULL);

COMMENT ON VIEW enhanced_student_fee_status IS 'Enhanced student fee summary combining legacy and monthly tracking data';

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_enhanced_fee_status_session_year 
ON students(session_year_id) WHERE is_active = true;

CREATE INDEX IF NOT EXISTS idx_enhanced_fee_status_class 
ON students(class_id) WHERE is_active = true;

-- Grant permissions
GRANT SELECT ON enhanced_student_fee_status TO PUBLIC;
