-- =====================================================
-- Sample Attendance Data
-- =====================================================

-- Insert sample student attendance records for current month
INSERT INTO student_attendance (
    student_id, attendance_date, status, check_in_time, check_out_time, 
    late_minutes, marked_by, remarks, created_at
) VALUES 
-- Week 1 attendance
(1, '2024-07-01', 'Present', '08:00', '15:30', 0, 1, NULL, NOW()),
(2, '2024-07-01', 'Present', '08:05', '15:30', 5, 1, NULL, NOW()),
(3, '2024-07-01', 'Late', '08:20', '15:30', 20, 1, 'Traffic jam', NOW()),

(1, '2024-07-02', 'Present', '07:55', '15:30', 0, 1, NULL, NOW()),
(2, '2024-07-02', 'Absent', NULL, NULL, 0, 1, 'Sick', NOW()),
(3, '2024-07-02', 'Present', '08:00', '15:30', 0, 1, NULL, NOW()),

(1, '2024-07-03', 'Present', '08:00', '15:30', 0, 1, NULL, NOW()),
(2, '2024-07-03', 'Present', '08:10', '15:30', 10, 1, NULL, NOW()),
(3, '2024-07-03', 'Present', '08:00', '15:30', 0, 1, NULL, NOW()),

-- Week 2 attendance
(1, '2024-07-08', 'Present', '08:00', '15:30', 0, 1, NULL, NOW()),
(2, '2024-07-08', 'Present', '08:00', '15:30', 0, 1, NULL, NOW()),
(3, '2024-07-08', 'Present', '08:00', '15:30', 0, 1, NULL, NOW()),

(1, '2024-07-09', 'Late', '08:25', '15:30', 25, 1, 'Doctor appointment', NOW()),
(2, '2024-07-09', 'Present', '08:00', '15:30', 0, 1, NULL, NOW()),
(3, '2024-07-09', 'Present', '08:00', '15:30', 0, 1, NULL, NOW()),

(1, '2024-07-10', 'Present', '08:00', '15:30', 0, 1, NULL, NOW()),
(2, '2024-07-10', 'Present', '08:00', '15:30', 0, 1, NULL, NOW()),
(3, '2024-07-10', 'Half Day', '08:00', '12:00', 0, 1, 'Family function', NOW()),

-- Week 3 attendance
(1, '2024-07-15', 'Present', '08:00', '15:30', 0, 1, NULL, NOW()),
(2, '2024-07-15', 'Present', '08:00', '15:30', 0, 1, NULL, NOW()),
(3, '2024-07-15', 'Present', '08:00', '15:30', 0, 1, NULL, NOW()),

(1, '2024-07-16', 'Present', '08:00', '15:30', 0, 1, NULL, NOW()),
(2, '2024-07-16', 'Absent', NULL, NULL, 0, 1, 'Family emergency', NOW()),
(3, '2024-07-16', 'Present', '08:00', '15:30', 0, 1, NULL, NOW()),

(1, '2024-07-17', 'Present', '08:00', '15:30', 0, 1, NULL, NOW()),
(2, '2024-07-17', 'Present', '08:15', '15:30', 15, 1, NULL, NOW()),
(3, '2024-07-17', 'Present', '08:00', '15:30', 0, 1, NULL, NOW())
ON CONFLICT (student_id, attendance_date, subject, period_number) DO NOTHING;

-- Insert sample teacher attendance records
INSERT INTO teacher_attendance (
    teacher_id, attendance_date, status, check_in_time, check_out_time, 
    total_hours, late_minutes, marked_by, remarks, created_at
) VALUES 
-- Assuming we have teachers with IDs 1, 2, 3 (will be created when teacher data is loaded)
-- Week 1 teacher attendance
(1, '2024-07-01', 'Present', '07:45', '16:00', 8.25, 0, 1, NULL, NOW()),
(2, '2024-07-01', 'Present', '07:50', '16:00', 8.17, 0, 1, NULL, NOW()),
(3, '2024-07-01', 'Present', '07:45', '16:00', 8.25, 0, 1, NULL, NOW()),

(1, '2024-07-02', 'Present', '07:45', '16:00', 8.25, 0, 1, NULL, NOW()),
(2, '2024-07-02', 'Late', '08:15', '16:00', 7.75, 15, 1, 'Traffic', NOW()),
(3, '2024-07-02', 'Present', '07:45', '16:00', 8.25, 0, 1, NULL, NOW()),

(1, '2024-07-03', 'Present', '07:45', '16:00', 8.25, 0, 1, NULL, NOW()),
(2, '2024-07-03', 'Present', '07:45', '16:00', 8.25, 0, 1, NULL, NOW()),
(3, '2024-07-03', 'On Leave', NULL, NULL, 0, 0, 1, 'Sick Leave', NOW()),

-- Week 2 teacher attendance
(1, '2024-07-08', 'Present', '07:45', '16:00', 8.25, 0, 1, NULL, NOW()),
(2, '2024-07-08', 'Present', '07:45', '16:00', 8.25, 0, 1, NULL, NOW()),
(3, '2024-07-08', 'Present', '07:45', '16:00', 8.25, 0, 1, NULL, NOW()),

(1, '2024-07-09', 'Present', '07:45', '16:00', 8.25, 0, 1, NULL, NOW()),
(2, '2024-07-09', 'Present', '07:45', '16:00', 8.25, 0, 1, NULL, NOW()),
(3, '2024-07-09', 'Present', '07:45', '16:00', 8.25, 0, 1, NULL, NOW()),

(1, '2024-07-10', 'Present', '07:45', '16:00', 8.25, 0, 1, NULL, NOW()),
(2, '2024-07-10', 'Half Day', '07:45', '12:00', 4.25, 0, 1, 'Personal work', NOW()),
(3, '2024-07-10', 'Present', '07:45', '16:00', 8.25, 0, 1, NULL, NOW())
ON CONFLICT (teacher_id, attendance_date) DO NOTHING;

-- Insert attendance summary records (monthly summaries)
INSERT INTO attendance_summary (
    person_id, person_type, summary_period, year, month, 
    total_days, present_days, absent_days, late_days, half_days,
    attendance_percentage, calculated_at
) VALUES 
-- Student summaries for July 2024
(1, 'student', 'monthly', 2024, 7, 20, 18, 0, 1, 0, 90.0, NOW()),
(2, 'student', 'monthly', 2024, 7, 20, 16, 2, 0, 0, 80.0, NOW()),
(3, 'student', 'monthly', 2024, 7, 20, 18, 0, 0, 1, 90.0, NOW()),

-- Teacher summaries for July 2024
(1, 'teacher', 'monthly', 2024, 7, 22, 22, 0, 0, 0, 100.0, NOW()),
(2, 'teacher', 'monthly', 2024, 7, 22, 20, 0, 1, 1, 90.9, NOW()),
(3, 'teacher', 'monthly', 2024, 7, 22, 21, 1, 0, 0, 95.5, NOW())
ON CONFLICT (person_id, person_type, summary_period, year, month, week_number) DO NOTHING;

-- Insert attendance settings
INSERT INTO attendance_settings (
    setting_name, setting_value, setting_type, description, is_active, updated_at
) VALUES 
('school_start_time', '08:00', 'time', 'School start time', true, NOW()),
('school_end_time', '15:30', 'time', 'School end time', true, NOW()),
('late_threshold_minutes', '15', 'integer', 'Minutes after which student is marked late', true, NOW()),
('half_day_threshold_hours', '4', 'integer', 'Minimum hours for half day attendance', true, NOW()),
('attendance_required', 'true', 'boolean', 'Whether attendance marking is mandatory', true, NOW()),
('weekend_days', 'Saturday,Sunday', 'string', 'Weekend days when school is closed', true, NOW()),
('grace_period_minutes', '5', 'integer', 'Grace period before marking late', true, NOW()),
('auto_mark_absent_time', '10:00', 'time', 'Time after which students are auto-marked absent', true, NOW())
ON CONFLICT (setting_name) DO NOTHING;

-- Insert holiday calendar
INSERT INTO holiday_calendar (
    holiday_date, holiday_name, holiday_type, is_working_day, 
    description, academic_year, created_at
) VALUES 
-- National Holidays
('2024-08-15', 'Independence Day', 'National Holiday', false, 'National holiday celebrating independence', '2024-25', NOW()),
('2024-10-02', 'Gandhi Jayanti', 'National Holiday', false, 'Birth anniversary of Mahatma Gandhi', '2024-25', NOW()),
('2025-01-26', 'Republic Day', 'National Holiday', false, 'National holiday celebrating the constitution', '2024-25', NOW()),

-- Festivals
('2024-10-24', 'Dussehra', 'Festival', false, 'Hindu festival celebrating victory of good over evil', '2024-25', NOW()),
('2024-11-12', 'Diwali', 'Festival', false, 'Festival of lights', '2024-25', NOW()),
('2024-12-25', 'Christmas', 'Festival', false, 'Christian festival', '2024-25', NOW()),

-- School Holidays
('2024-12-24', 'Christmas Eve', 'School Holiday', false, 'Day before Christmas', '2024-25', NOW()),
('2024-12-31', 'New Year Eve', 'School Holiday', false, 'Last day of the year', '2024-25', NOW()),
('2025-01-01', 'New Year Day', 'School Holiday', false, 'First day of the new year', '2024-25', NOW()),

-- Exam Days (working days but special)
('2024-12-01', 'Annual Exam Start', 'Exam Day', true, 'Beginning of annual examinations', '2024-25', NOW()),
('2024-12-15', 'Annual Exam End', 'Exam Day', true, 'End of annual examinations', '2024-25', NOW())
ON CONFLICT (holiday_date) DO NOTHING;

-- Display attendance summary
SELECT 'Attendance Data Summary' as info;

SELECT 'Student Attendance Records' as data_type, COUNT(*) as count
FROM student_attendance

UNION ALL

SELECT 'Teacher Attendance Records' as data_type, COUNT(*) as count
FROM teacher_attendance

UNION ALL

SELECT 'Attendance Summary Records' as data_type, COUNT(*) as count
FROM attendance_summary

UNION ALL

SELECT 'Attendance Settings' as data_type, COUNT(*) as count
FROM attendance_settings

UNION ALL

SELECT 'Holiday Calendar Entries' as data_type, COUNT(*) as count
FROM holiday_calendar;

-- Display attendance statistics
SELECT 
    'Student Attendance Statistics' as report_type,
    s.first_name || ' ' || s.last_name as student_name,
    COUNT(sa.id) as total_days,
    COUNT(CASE WHEN sa.status = 'Present' THEN 1 END) as present_days,
    COUNT(CASE WHEN sa.status = 'Absent' THEN 1 END) as absent_days,
    COUNT(CASE WHEN sa.status = 'Late' THEN 1 END) as late_days,
    ROUND((COUNT(CASE WHEN sa.status = 'Present' THEN 1 END) * 100.0 / COUNT(sa.id)), 2) as attendance_percentage
FROM students s
LEFT JOIN student_attendance sa ON s.id = sa.student_id
WHERE sa.attendance_date >= '2024-07-01' AND sa.attendance_date <= '2024-07-31'
GROUP BY s.id, s.first_name, s.last_name
ORDER BY s.first_name;
