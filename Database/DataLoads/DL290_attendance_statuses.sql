-- =====================================================
-- Data Load: attendance_statuses
-- Description: Insert default attendance statuses with color codes
-- Simplified to 3 statuses: Present, Absent, Leave
-- =====================================================

INSERT INTO attendance_statuses (id, name, description, color_code, affects_attendance_percentage, is_active) VALUES
(1, 'PRESENT', 'Present', '#28A745', TRUE, TRUE),
(2, 'ABSENT', 'Absent', '#DC3545', TRUE, TRUE),
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

