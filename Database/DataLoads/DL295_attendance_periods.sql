-- =====================================================
-- Data Load: attendance_periods
-- Description: Insert default attendance periods with time ranges
-- =====================================================

INSERT INTO attendance_periods (id, name, description, start_time, end_time, is_active) VALUES
(1, 'FULL_DAY', 'Full Day', '08:00:00', '14:30:00', TRUE),
(2, 'MORNING', 'Morning', '08:00:00', '11:00:00', TRUE),
(3, 'AFTERNOON', 'Afternoon', '11:00:00', '14:30:00', TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    start_time = EXCLUDED.start_time,
    end_time = EXCLUDED.end_time,
    is_active = EXCLUDED.is_active,
    updated_at = CURRENT_TIMESTAMP;

-- Reset sequence to ensure next auto-generated ID is correct
SELECT setval('attendance_periods_id_seq', (SELECT MAX(id) FROM attendance_periods));

