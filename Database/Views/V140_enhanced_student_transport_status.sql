-- =====================================================
-- View: enhanced_student_transport_status
-- Description: Comprehensive view of student transport enrollment and payment status
-- Dependencies: students, classes, session_years, student_transport_enrollment, 
--               transport_monthly_tracking, transport_types, payment_statuses
-- =====================================================

-- Drop existing view
DROP VIEW IF EXISTS enhanced_student_transport_status CASCADE;

-- Create view
CREATE OR REPLACE VIEW enhanced_student_transport_status AS
SELECT
    -- Student Information
    s.id AS student_id,
    s.admission_number,
    CONCAT(s.first_name, ' ', s.last_name) AS student_name,
    c.description AS class_name,
    sy.name AS session_year,
    
    -- Enrollment Information
    e.id AS enrollment_id,
    e.transport_type_id,
    tt.description AS transport_type_name,
    e.enrollment_date,
    e.discontinue_date,
    e.is_active AS is_enrolled,
    e.distance_km,
    e.monthly_fee,
    e.pickup_location,
    e.drop_location,
    
    -- Monthly Tracking Statistics
    COALESCE(mt.total_months_tracked, 0) AS total_months_tracked,
    COALESCE(mt.enabled_months, 0) AS enabled_months,
    COALESCE(mt.paid_months, 0) AS paid_months,
    COALESCE(mt.pending_months, 0) AS pending_months,
    COALESCE(mt.overdue_months, 0) AS overdue_months,
    
    -- Financial Summary
    COALESCE(mt.total_amount, 0.00) AS total_amount,
    COALESCE(mt.total_paid, 0.00) AS total_paid,
    COALESCE(mt.total_balance, 0.00) AS total_balance,
    
    -- Collection Percentage
    CASE 
        WHEN COALESCE(mt.total_amount, 0) > 0 THEN 
            ROUND((COALESCE(mt.total_paid, 0) / mt.total_amount * 100)::NUMERIC, 2)
        ELSE 0.00
    END AS collection_percentage,
    
    -- Tracking Status
    CASE 
        WHEN mt.total_months_tracked > 0 THEN TRUE 
        ELSE FALSE 
    END AS has_monthly_tracking

FROM students s
LEFT JOIN classes c ON s.class_id = c.id
LEFT JOIN session_years sy ON s.session_year_id = sy.id
LEFT JOIN student_transport_enrollment e ON s.id = e.student_id
    AND s.session_year_id = e.session_year_id
    AND e.is_active = TRUE
LEFT JOIN transport_types tt ON e.transport_type_id = tt.id
LEFT JOIN (
    -- Subquery to get monthly tracking statistics
    SELECT
        tmt.student_id,
        tmt.session_year_id,
        tmt.enrollment_id,
        COUNT(*) AS total_months_tracked,
        COUNT(CASE WHEN tmt.is_service_enabled = TRUE THEN 1 END) AS enabled_months,
        COUNT(CASE WHEN ps.name = 'PAID' AND tmt.is_service_enabled = TRUE THEN 1 END) AS paid_months,
        COUNT(CASE WHEN ps.name = 'PENDING' AND tmt.is_service_enabled = TRUE THEN 1 END) AS pending_months,
        COUNT(CASE WHEN ps.name = 'OVERDUE' AND tmt.is_service_enabled = TRUE THEN 1 END) AS overdue_months,
        SUM(CASE WHEN tmt.is_service_enabled = TRUE THEN tmt.monthly_amount ELSE 0 END) AS total_amount,
        SUM(CASE WHEN tmt.is_service_enabled = TRUE THEN tmt.paid_amount ELSE 0 END) AS total_paid,
        SUM(CASE WHEN tmt.is_service_enabled = TRUE THEN tmt.balance_amount ELSE 0 END) AS total_balance
    FROM transport_monthly_tracking tmt
    LEFT JOIN payment_statuses ps ON tmt.payment_status_id = ps.id
    GROUP BY tmt.student_id, tmt.session_year_id, tmt.enrollment_id
) mt ON s.id = mt.student_id AND s.session_year_id = mt.session_year_id
WHERE (s.is_deleted = FALSE OR s.is_deleted IS NULL);

-- Add comment
COMMENT ON VIEW enhanced_student_transport_status IS 
'Comprehensive view of student transport enrollment status with monthly tracking statistics and payment summary';

