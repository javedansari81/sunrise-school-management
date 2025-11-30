-- =====================================================
-- Data Load: attendance_statuses
-- Description: Insert default attendance statuses with color codes
-- =====================================================

INSERT INTO attendance_statuses (id, name, description, color_code, affects_attendance_percentage, is_active) VALUES
(1, 'PRESENT', 'Present', '#28A745', TRUE, TRUE),
(2, 'ABSENT', 'Absent', '#DC3545', TRUE, TRUE),
(3, 'LATE', 'Late', '#FFC107', TRUE, TRUE),
(4, 'HALF_DAY', 'Half Day', '#17A2B8', TRUE, TRUE),
(5, 'EXCUSED', 'Excused', '#6C757D', FALSE, TRUE),
(6, 'HOLIDAY', 'Holiday', '#007BFF', FALSE, TRUE),
(7, 'LEAVE', 'On Leave', '#6F42C1', FALSE, TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    color_code = EXCLUDED.color_code,
    affects_attendance_percentage = EXCLUDED.affects_attendance_percentage,
    is_active = EXCLUDED.is_active,
    updated_at = CURRENT_TIMESTAMP;

-- Reset sequence to ensure next auto-generated ID is correct
SELECT setval('attendance_statuses_id_seq', (SELECT MAX(id) FROM attendance_statuses));

