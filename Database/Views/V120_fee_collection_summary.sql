-- =====================================================
-- View: fee_collection_summary
-- Description: Fee collection statistics grouped by session, class, payment type and status
-- Dependencies: fee_records, students, session_years, classes, payment_types, payment_statuses
-- =====================================================

-- Drop existing view
DROP VIEW IF EXISTS fee_collection_summary CASCADE;

-- Create view
CREATE OR REPLACE VIEW fee_collection_summary AS
SELECT
    sy.name AS session_year,
    c.name AS class_name,
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
WHERE (s.is_deleted = FALSE OR s.is_deleted IS NULL)
  AND s.is_active = TRUE
  AND c.is_active = TRUE
  AND sy.is_active = TRUE
GROUP BY sy.name, c.name, pt.name, ps.name;

-- Add comment
COMMENT ON VIEW fee_collection_summary IS 'Fee collection statistics grouped by session, class, payment type and status';

