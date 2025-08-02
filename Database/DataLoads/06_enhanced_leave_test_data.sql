-- =====================================================
-- Enhanced Leave Management Test Data
-- =====================================================
-- Comprehensive test data covering various scenarios and edge cases
-- This file extends the basic sample data with more complex scenarios

-- =====================================================
-- Additional Test Users and Records
-- =====================================================

-- Insert additional teacher users
INSERT INTO users (id, username, email, first_name, last_name, role_id, is_active, created_at)
VALUES 
(4, 'teacher2', 'teacher2@school.com', 'Sarah', 'Johnson', 2, true, NOW()),
(5, 'teacher3', 'teacher3@school.com', 'Michael', 'Brown', 2, true, NOW()),
(6, 'principal', 'principal@school.com', 'Dr. Robert', 'Wilson', 1, true, NOW())
ON CONFLICT (id) DO NOTHING;

-- Insert additional teacher records
INSERT INTO teachers (id, user_id, employee_id, first_name, last_name, phone, email, position, department, joining_date, is_active, created_at)
VALUES 
(3, 4, 'T003', 'Sarah', 'Johnson', '9876543212', 'teacher2@school.com', 'Senior Teacher', 'English', '2022-06-01', true, NOW()),
(4, 5, 'T004', 'Michael', 'Brown', '9876543213', 'teacher3@school.com', 'Teacher', 'Science', '2023-03-15', true, NOW()),
(5, 6, 'T005', 'Dr. Robert', 'Wilson', '9876543214', 'principal@school.com', 'Principal', 'Administration', '2020-01-01', true, NOW())
ON CONFLICT (id) DO NOTHING;

-- Insert additional student users
INSERT INTO users (id, username, email, first_name, last_name, role_id, is_active, created_at)
VALUES 
(7, 'student2', 'student2@school.com', 'Alex', 'Smith', 3, true, NOW()),
(8, 'student3', 'student3@school.com', 'Emma', 'Davis', 3, true, NOW()),
(9, 'student4', 'student4@school.com', 'Ryan', 'Miller', 3, true, NOW())
ON CONFLICT (id) DO NOTHING;

-- Insert additional student records
INSERT INTO students (id, user_id, admission_number, first_name, last_name, date_of_birth, gender_id, class_id, session_year_id, father_name, mother_name, admission_date, is_active, created_at)
VALUES 
(2, 7, 'STU002', 'Alex', 'Smith', '2009-08-20', 1, 2, 4, 'David Smith', 'Lisa Smith', '2023-01-01', true, NOW()),
(3, 8, 'STU003', 'Emma', 'Davis', '2011-03-10', 2, 1, 4, 'Mark Davis', 'Jennifer Davis', '2023-01-01', true, NOW()),
(4, 9, 'STU004', 'Ryan', 'Miller', '2010-11-05', 1, 3, 4, 'James Miller', 'Susan Miller', '2023-01-01', true, NOW())
ON CONFLICT (id) DO NOTHING;

-- =====================================================
-- Complex Leave Request Scenarios
-- =====================================================

-- Scenario 1: Multiple consecutive leave requests by same student
INSERT INTO leave_requests (
    applicant_id, applicant_type, leave_type_id, start_date, end_date, total_days, 
    reason, leave_status_id, parent_consent, emergency_contact_name, emergency_contact_phone, created_at
) VALUES 
-- First request - approved
(2, 'student', 2, '2024-01-10', '2024-01-12', 3,
 'Family wedding in hometown. Important cultural ceremony.',
 2, true, 'David Smith', '9876543220', NOW() - INTERVAL '20 days'),
-- Second request - pending (overlapping concern)
(2, 'student', 1, '2024-02-05', '2024-02-07', 3,
 'Severe cold and fever. Doctor advised rest.',
 1, true, 'David Smith', '9876543220', NOW() - INTERVAL '5 days'),
-- Third request - future date
(2, 'student', 3, '2024-03-15', '2024-03-15', 1,
 'Emergency dental appointment. Severe tooth pain.',
 1, true, 'David Smith', '9876543220', NOW())
ON CONFLICT DO NOTHING;

-- Scenario 2: Teacher with substitute arrangement challenges
INSERT INTO leave_requests (
    applicant_id, applicant_type, leave_type_id, start_date, end_date, total_days,
    reason, leave_status_id, substitute_teacher_id, substitute_arranged, created_at
) VALUES 
-- Request without substitute arranged
(3, 'teacher', 2, '2024-02-20', '2024-02-22', 3,
 'Attending educational conference on modern teaching methods.',
 1, NULL, false, NOW()),
-- Request with substitute but pending approval
(4, 'teacher', 1, '2024-02-25', '2024-02-29', 5,
 'Medical procedure scheduled. Doctor recommended 5 days rest.',
 1, 2, true, NOW())
ON CONFLICT DO NOTHING;

-- Scenario 3: Emergency leave requests (same day application)
INSERT INTO leave_requests (
    applicant_id, applicant_type, leave_type_id, start_date, end_date, total_days,
    reason, leave_status_id, parent_consent, emergency_contact_name, emergency_contact_phone, created_at
) VALUES 
(3, 'student', 3, CURRENT_DATE, CURRENT_DATE, 1,
 'Sudden family emergency. Grandfather hospitalized.',
 1, true, 'Mark Davis', '9876543221', NOW()),
(4, 'student', 3, CURRENT_DATE, CURRENT_DATE + INTERVAL '1 day', 2,
 'Mother met with accident. Need to be with family.',
 1, true, 'James Miller', '9876543222', NOW())
ON CONFLICT DO NOTHING;

-- Scenario 4: Long-term medical leave
INSERT INTO leave_requests (
    applicant_id, applicant_type, leave_type_id, start_date, end_date, total_days,
    reason, medical_certificate_url, leave_status_id, substitute_teacher_id, substitute_arranged, created_at
) VALUES 
(3, 'teacher', 4, '2024-03-01', '2024-03-21', 21,
 'Surgery scheduled for chronic back pain. Extended recovery period required.',
 'https://example.com/medical-cert-surgery.pdf', 1, 4, true, NOW())
ON CONFLICT DO NOTHING;

-- Scenario 5: Half-day leave requests
INSERT INTO leave_requests (
    applicant_id, applicant_type, leave_type_id, start_date, end_date, total_days,
    reason, leave_status_id, is_half_day, half_day_session, parent_consent,
    emergency_contact_name, emergency_contact_phone, created_at
) VALUES 
(1, 'student', 2, CURRENT_DATE + INTERVAL '3 days', CURRENT_DATE + INTERVAL '3 days', 1,
 'Dental appointment in morning. Will attend afternoon classes.',
 1, true, 'morning', true, 'John Doe Sr.', '9876543210', NOW()),
(2, 'student', 2, CURRENT_DATE + INTERVAL '5 days', CURRENT_DATE + INTERVAL '5 days', 1,
 'Eye checkup appointment in afternoon.',
 1, true, 'afternoon', true, 'David Smith', '9876543220', NOW())
ON CONFLICT DO NOTHING;

-- =====================================================
-- Leave Balance for Additional Teachers
-- =====================================================

-- Leave Balance for Teacher 3 (Sarah Johnson)
INSERT INTO leave_balance (
    teacher_id, session_year_id, 
    casual_leave_total, casual_leave_used, casual_leave_balance,
    sick_leave_total, sick_leave_used, sick_leave_balance,
    earned_leave_total, earned_leave_used, earned_leave_balance,
    maternity_leave_total, maternity_leave_used, maternity_leave_balance,
    paternity_leave_total, paternity_leave_used, paternity_leave_balance,
    carry_forward_from_previous, created_at
) VALUES 
(3, 4, 12, 0, 12, 15, 0, 15, 20, 5, 15, 180, 0, 180, 15, 0, 15, 3, NOW())
ON CONFLICT (teacher_id, session_year_id) DO NOTHING;

-- Leave Balance for Teacher 4 (Michael Brown)
INSERT INTO leave_balance (
    teacher_id, session_year_id, 
    casual_leave_total, casual_leave_used, casual_leave_balance,
    sick_leave_total, sick_leave_used, sick_leave_balance,
    earned_leave_total, earned_leave_used, earned_leave_balance,
    maternity_leave_total, maternity_leave_used, maternity_leave_balance,
    paternity_leave_total, paternity_leave_used, paternity_leave_balance,
    carry_forward_from_previous, created_at
) VALUES 
(4, 4, 12, 1, 11, 15, 2, 13, 20, 0, 20, 180, 0, 180, 15, 0, 15, 0, NOW())
ON CONFLICT (teacher_id, session_year_id) DO NOTHING;

-- Leave Balance for Principal (Dr. Robert Wilson)
INSERT INTO leave_balance (
    teacher_id, session_year_id, 
    casual_leave_total, casual_leave_used, casual_leave_balance,
    sick_leave_total, sick_leave_used, sick_leave_balance,
    earned_leave_total, earned_leave_used, earned_leave_balance,
    maternity_leave_total, maternity_leave_used, maternity_leave_balance,
    paternity_leave_total, paternity_leave_used, paternity_leave_balance,
    carry_forward_from_previous, created_at
) VALUES 
(5, 4, 15, 3, 12, 20, 1, 19, 25, 8, 17, 180, 0, 180, 15, 0, 15, 5, NOW())
ON CONFLICT (teacher_id, session_year_id) DO NOTHING;

-- =====================================================
-- Additional Leave Approvers
-- =====================================================

-- Principal can approve all types of leaves
INSERT INTO leave_approvers (
    approver_id, leave_type_id, applicant_type, max_days_can_approve,
    can_approve_all, is_active, created_at
) VALUES
(6, 1, 'student', 30, true, true, NOW()), -- Principal can approve student sick leave
(6, 2, 'student', 30, true, true, NOW()), -- Principal can approve student casual leave
(6, 3, 'student', 30, true, true, NOW()), -- Principal can approve student emergency leave
(6, 1, 'teacher', 90, true, true, NOW()), -- Principal can approve teacher sick leave
(6, 2, 'teacher', 30, true, true, NOW()), -- Principal can approve teacher casual leave
(6, 3, 'teacher', 30, true, true, NOW()), -- Principal can approve teacher emergency leave
(6, 4, 'teacher', 180, true, true, NOW()), -- Principal can approve teacher medical leave
(6, 5, 'teacher', 30, true, true, NOW())  -- Principal can approve teacher personal leave
ON CONFLICT DO NOTHING;

-- Senior teachers can approve student leaves
INSERT INTO leave_approvers (
    approver_id, leave_type_id, applicant_type, max_days_can_approve,
    can_approve_all, specific_classes, is_active, created_at
) VALUES
(2, 1, 'student', 7, false, '["Class 1", "Class 2", "Class 3"]', true, NOW()), -- John Teacher can approve student sick leave for specific classes
(2, 2, 'student', 5, false, '["Class 1", "Class 2", "Class 3"]', true, NOW()), -- John Teacher can approve student casual leave for specific classes
(4, 1, 'student', 7, false, '["Class 4", "Class 5"]', true, NOW()), -- Sarah Johnson can approve student sick leave for specific classes
(4, 2, 'student', 5, false, '["Class 4", "Class 5"]', true, NOW())  -- Sarah Johnson can approve student casual leave for specific classes
ON CONFLICT DO NOTHING;

-- =====================================================
-- Leave Notifications Sample Data
-- =====================================================

INSERT INTO leave_notifications (
    leave_request_id, recipient_id, notification_type, subject, message_content, 
    sent_at, status, created_at
) VALUES 
(1, 1, 'Email', 'Leave Application Submitted', 
 'Your leave application for sick leave from 2024-02-15 to 2024-02-17 has been submitted and is pending approval.',
 NOW() - INTERVAL '1 hour', 'Sent', NOW() - INTERVAL '1 hour'),
(2, 1, 'Email', 'Leave Application Approved', 
 'Your leave application for casual leave from 2024-01-20 to 2024-01-22 has been approved.',
 NOW() - INTERVAL '5 days', 'Read', NOW() - INTERVAL '5 days'),
(3, 1, 'Email', 'Leave Application Rejected', 
 'Your leave application for emergency leave from 2024-01-10 to 2024-01-12 has been rejected. Please contact administration for details.',
 NOW() - INTERVAL '15 days', 'Read', NOW() - INTERVAL '15 days')
ON CONFLICT DO NOTHING;

-- =====================================================
-- Verification Queries for Enhanced Data
-- =====================================================

-- Show all leave requests with applicant details
SELECT 
    'ALL LEAVE REQUESTS WITH DETAILS:' as info,
    lr.id,
    lr.applicant_type,
    CASE 
        WHEN lr.applicant_type = 'student' THEN s.first_name || ' ' || s.last_name
        WHEN lr.applicant_type = 'teacher' THEN t.first_name || ' ' || t.last_name
    END as applicant_name,
    lt.name as leave_type,
    lr.start_date,
    lr.end_date,
    lr.total_days,
    ls.name as status,
    lr.is_half_day,
    lr.substitute_arranged,
    lr.created_at
FROM leave_requests lr
LEFT JOIN students s ON lr.applicant_id = s.id AND lr.applicant_type = 'student'
LEFT JOIN teachers t ON lr.applicant_id = t.id AND lr.applicant_type = 'teacher'
JOIN leave_types lt ON lr.leave_type_id = lt.id
JOIN leave_statuses ls ON lr.leave_status_id = ls.id
ORDER BY lr.created_at DESC;

-- Show pending leave requests requiring attention
SELECT 
    'PENDING LEAVE REQUESTS:' as info,
    lr.id,
    lr.applicant_type,
    CASE 
        WHEN lr.applicant_type = 'student' THEN s.first_name || ' ' || s.last_name
        WHEN lr.applicant_type = 'teacher' THEN t.first_name || ' ' || t.last_name
    END as applicant_name,
    lt.name as leave_type,
    lr.start_date,
    lr.end_date,
    lr.total_days,
    CASE 
        WHEN lr.start_date <= CURRENT_DATE THEN 'URGENT'
        WHEN lr.start_date <= CURRENT_DATE + INTERVAL '3 days' THEN 'HIGH'
        ELSE 'NORMAL'
    END as priority
FROM leave_requests lr
LEFT JOIN students s ON lr.applicant_id = s.id AND lr.applicant_type = 'student'
LEFT JOIN teachers t ON lr.applicant_id = t.id AND lr.applicant_type = 'teacher'
JOIN leave_types lt ON lr.leave_type_id = lt.id
WHERE lr.leave_status_id = 1 -- Pending status
ORDER BY lr.start_date ASC;
