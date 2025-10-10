-- =====================================================
-- View: enhanced_student_fee_status
-- Description: Enhanced student fee summary combining legacy and monthly tracking data
-- Dependencies: students, classes, session_years, fee_records, payment_statuses, monthly_fee_tracking
-- =====================================================

-- Drop existing view
DROP VIEW IF EXISTS enhanced_student_fee_status CASCADE;

-- Create view
CREATE OR REPLACE VIEW enhanced_student_fee_status AS
SELECT
    s.id as student_id,
    s.admission_number,
    s.first_name || ' ' || s.last_name as student_name,
    c.name as class_name,
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

    -- Has monthly tracking flag (check if monthly tracking records exist)
    CASE
        WHEN monthly_stats.total_months_tracked > 0 THEN true
        ELSE false
    END as has_monthly_tracking,

    -- Payment status information (from metadata)
    ps.name as payment_status,
    ps.color_code as payment_status_color

FROM students s
LEFT JOIN classes c ON s.class_id = c.id
LEFT JOIN session_years sy ON s.session_year_id = sy.id
LEFT JOIN fee_records fr ON s.id = fr.student_id AND s.session_year_id = fr.session_year_id
LEFT JOIN payment_statuses ps ON fr.payment_status_id = ps.id
LEFT JOIN (
    -- Subquery to get monthly tracking statistics with metadata-driven status names
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
    WHERE ps.is_active = true  -- Only include active payment statuses
    GROUP BY mft.student_id, mft.session_year_id
) monthly_stats ON s.id = monthly_stats.student_id AND s.session_year_id = monthly_stats.session_year_id

WHERE s.is_active = true
  AND (s.is_deleted = FALSE OR s.is_deleted IS NULL)
  AND c.is_active = true  -- Only include active classes
  AND sy.is_active = true;  -- Only include active session years

-- Add comment
COMMENT ON VIEW enhanced_student_fee_status IS 'Enhanced student fee summary combining legacy and monthly tracking data with metadata-driven architecture support';

