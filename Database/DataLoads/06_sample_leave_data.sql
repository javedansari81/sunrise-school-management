-- =====================================================
-- Sample Leave Data for Testing
-- =====================================================
-- This file contains comprehensive test data for the leave management system
-- including both student and teacher leave requests with various statuses

-- =====================================================
-- Create Sample Users for Leave Management (if not exists)
-- =====================================================

-- Insert sample admin user for approvals (if not exists)
INSERT INTO users (id, username, email, first_name, last_name, role_id, is_active, created_at)
VALUES (1, 'admin', 'admin@school.com', 'Admin', 'User', 1, true, NOW())
ON CONFLICT (id) DO NOTHING;

-- Insert sample teacher user (if not exists)
INSERT INTO users (id, username, email, first_name, last_name, role_id, is_active, created_at)
VALUES (2, 'teacher1', 'teacher1@school.com', 'John', 'Teacher', 2, true, NOW())
ON CONFLICT (id) DO NOTHING;

-- Insert sample student user (if not exists)
INSERT INTO users (id, username, email, first_name, last_name, role_id, is_active, created_at)
VALUES (3, 'student1', 'student1@school.com', 'Jane', 'Student', 3, true, NOW())
ON CONFLICT (id) DO NOTHING;

-- Insert sample teacher record (if not exists)
INSERT INTO teachers (id, user_id, employee_id, first_name, last_name, phone, email, position, department, joining_date, is_active, created_at)
VALUES (1, 2, 'T001', 'John', 'Teacher', '9876543210', 'teacher1@school.com', 'Senior Teacher', 'Mathematics', '2023-01-01', true, NOW())
ON CONFLICT (id) DO NOTHING;

-- Insert second teacher for substitute arrangements (if not exists)
INSERT INTO teachers (id, user_id, employee_id, first_name, last_name, phone, email, position, department, joining_date, is_active, created_at)
VALUES (2, NULL, 'T002', 'Mary', 'Substitute', '9876543211', 'substitute@school.com', 'Substitute Teacher', 'General', '2023-01-01', true, NOW())
ON CONFLICT (id) DO NOTHING;

-- Insert sample student record (if not exists)
INSERT INTO students (id, user_id, admission_number, first_name, last_name, date_of_birth, gender_id, class_id, session_year_id, father_name, mother_name, admission_date, is_active, created_at)
VALUES (1, 3, 'STU001', 'Jane', 'Student', '2010-05-15', 1, 1, 4, 'Father Name', 'Mother Name', '2023-01-01', true, NOW())
ON CONFLICT (id) DO NOTHING;

-- =====================================================
-- Sample Leave Requests for Students
-- =====================================================

-- Student Leave Request 1 - Pending Sick Leave
INSERT INTO leave_requests (
    applicant_id, applicant_type, leave_type_id, start_date, end_date, total_days, 
    reason, medical_certificate_url, leave_status_id, parent_consent, 
    emergency_contact_name, emergency_contact_phone, created_at
) VALUES (
    1, 'student', 1, '2024-02-15', '2024-02-17', 3,
    'Student has fever and needs rest as advised by doctor. Medical certificate attached.',
    'https://example.com/medical-cert-001.pdf', 1, true,
    'John Doe Sr.', '9876543210', NOW()
) ON CONFLICT DO NOTHING;

-- Student Leave Request 2 - Approved Casual Leave
INSERT INTO leave_requests (
    applicant_id, applicant_type, leave_type_id, start_date, end_date, total_days,
    reason, leave_status_id, parent_consent, reviewed_by, reviewed_at,
    review_comments, emergency_contact_name, emergency_contact_phone, created_at
) VALUES (
    1, 'student', 2, '2024-01-20', '2024-01-22', 3,
    'Family wedding ceremony. Need to attend important family function.',
    2, true,
    (SELECT id FROM users WHERE username = 'admin' LIMIT 1),
    NOW() - INTERVAL '5 days',
    'Approved for family function. Please ensure to catch up on missed lessons.',
    'John Doe Sr.', '9876543210', NOW() - INTERVAL '10 days'
) ON CONFLICT DO NOTHING;

-- Student Leave Request 3 - Rejected Emergency Leave
INSERT INTO leave_requests (
    applicant_id, applicant_type, leave_type_id, start_date, end_date, total_days,
    reason, leave_status_id, reviewed_by, reviewed_at,
    review_comments, emergency_contact_name, emergency_contact_phone, created_at
) VALUES (
    1, 'student', 3, '2024-01-10', '2024-01-12', 3,
    'Emergency travel required due to family situation.',
    3, (SELECT id FROM users WHERE username = 'admin' LIMIT 1), NOW() - INTERVAL '15 days',
    'Insufficient documentation provided. Please reapply with proper supporting documents.',
    'John Doe Sr.', '9876543210', NOW() - INTERVAL '20 days'
) ON CONFLICT DO NOTHING;

-- Student Leave Request 4 - Half Day Leave (Pending)
INSERT INTO leave_requests (
    applicant_id, applicant_type, leave_type_id, start_date, end_date, total_days, 
    reason, leave_status_id, is_half_day, half_day_session, parent_consent,
    emergency_contact_name, emergency_contact_phone, created_at
) VALUES (
    1, 'student', 2, '2024-02-20', '2024-02-20', 1,
    'Doctor appointment in the afternoon. Will attend morning classes.',
    1, true, 'afternoon', true,
    'John Doe Sr.', '9876543210', NOW()
) ON CONFLICT DO NOTHING;

-- =====================================================
-- Sample Leave Requests for Teachers
-- =====================================================

-- Teacher Leave Request 1 - Approved Sick Leave
INSERT INTO leave_requests (
    applicant_id, applicant_type, leave_type_id, start_date, end_date, total_days,
    reason, medical_certificate_url, leave_status_id, substitute_teacher_id,
    substitute_arranged, reviewed_by, reviewed_at, review_comments, created_at
) VALUES (
    1, 'teacher', 1, '2024-01-25', '2024-01-27', 3,
    'Diagnosed with viral fever. Doctor advised complete rest for 3 days.',
    'https://example.com/teacher-medical-cert-001.pdf', 2,
    (SELECT id FROM teachers WHERE employee_id = 'T002' LIMIT 1),
    true, (SELECT id FROM users WHERE username = 'admin' LIMIT 1), NOW() - INTERVAL '3 days',
    'Approved. Substitute teacher arranged. Please submit fitness certificate before resuming.',
    NOW() - INTERVAL '8 days'
) ON CONFLICT DO NOTHING;

-- Teacher Leave Request 2 - Pending Personal Leave
INSERT INTO leave_requests (
    applicant_id, applicant_type, leave_type_id, start_date, end_date, total_days,
    reason, leave_status_id, substitute_teacher_id, substitute_arranged, created_at
) VALUES (
    1, 'teacher', 5, '2024-03-01', '2024-03-03', 3,
    'Personal work related to property documentation. Need to visit government offices.',
    1, (SELECT id FROM teachers WHERE employee_id = 'T002' LIMIT 1), true, NOW()
) ON CONFLICT DO NOTHING;

-- Teacher Leave Request 3 - Approved Casual Leave
INSERT INTO leave_requests (
    applicant_id, applicant_type, leave_type_id, start_date, end_date, total_days,
    reason, leave_status_id, reviewed_by, reviewed_at, review_comments,
    substitute_teacher_id, substitute_arranged, created_at
) VALUES (
    1, 'teacher', 2, '2024-01-15', '2024-01-16', 2,
    'Attending professional development workshop on modern teaching methods.',
    2, (SELECT id FROM users WHERE username = 'admin' LIMIT 1), NOW() - INTERVAL '10 days',
    'Approved. Workshop will benefit teaching quality. Please share learnings with team.',
    (SELECT id FROM teachers WHERE employee_id = 'T002' LIMIT 1), true, NOW() - INTERVAL '15 days'
) ON CONFLICT DO NOTHING;

-- =====================================================
-- Sample Leave Balance for Teachers
-- =====================================================

-- Leave Balance for Teacher 1 (Current Session Year)
INSERT INTO leave_balance (
    teacher_id, session_year_id,
    casual_leave_total, casual_leave_used, casual_leave_balance,
    sick_leave_total, sick_leave_used, sick_leave_balance,
    earned_leave_total, earned_leave_used, earned_leave_balance,
    maternity_leave_total, maternity_leave_used, maternity_leave_balance,
    paternity_leave_total, paternity_leave_used, paternity_leave_balance,
    carry_forward_from_previous, created_at
) VALUES
(1, 4, 12, 2, 10, 15, 3, 12, 20, 0, 20, 180, 0, 180, 15, 0, 15, 2, NOW())
ON CONFLICT (teacher_id, session_year_id) DO NOTHING;

-- =====================================================
-- Sample Leave Policies
-- =====================================================

-- Student Leave Policies
INSERT INTO leave_policies (
    policy_name, applicant_type, leave_type_id, max_days_per_application, 
    max_days_per_year, min_notice_days, requires_medical_certificate, 
    requires_approval, effective_from, is_active, created_at
) VALUES 
('Student Sick Leave Policy', 'student', 1, 7, 15, 0, true, true, '2024-01-01', true, NOW()),
('Student Casual Leave Policy', 'student', 2, 3, 12, 1, false, true, '2024-01-01', true, NOW()),
('Student Emergency Leave Policy', 'student', 3, 5, 10, 0, false, true, '2024-01-01', true, NOW())
ON CONFLICT DO NOTHING;

-- Teacher Leave Policies
INSERT INTO leave_policies (
    policy_name, applicant_type, leave_type_id, max_days_per_application, 
    max_days_per_year, min_notice_days, requires_medical_certificate, 
    requires_approval, effective_from, is_active, created_at
) VALUES 
('Teacher Sick Leave Policy', 'teacher', 1, 15, 30, 0, true, true, '2024-01-01', true, NOW()),
('Teacher Casual Leave Policy', 'teacher', 2, 5, 15, 2, false, true, '2024-01-01', true, NOW()),
('Teacher Emergency Leave Policy', 'teacher', 3, 3, 8, 0, false, true, '2024-01-01', true, NOW()),
('Teacher Medical Leave Policy', 'teacher', 4, 30, 90, 7, true, true, '2024-01-01', true, NOW()),
('Teacher Personal Leave Policy', 'teacher', 5, 5, 12, 3, false, true, '2024-01-01', true, NOW())
ON CONFLICT DO NOTHING;

-- =====================================================
-- Sample Leave Approvers
-- =====================================================

-- Admin can approve all types of leaves for both students and teachers
INSERT INTO leave_approvers (
    approver_id, leave_type_id, applicant_type, max_days_can_approve,
    can_approve_all, is_active, created_at
) VALUES
((SELECT id FROM users WHERE username = 'admin' LIMIT 1), 1, 'student', 30, true, true, NOW()), -- Admin can approve student sick leave
((SELECT id FROM users WHERE username = 'admin' LIMIT 1), 2, 'student', 30, true, true, NOW()), -- Admin can approve student casual leave
((SELECT id FROM users WHERE username = 'admin' LIMIT 1), 3, 'student', 30, true, true, NOW()), -- Admin can approve student emergency leave
((SELECT id FROM users WHERE username = 'admin' LIMIT 1), 1, 'teacher', 30, true, true, NOW()), -- Admin can approve teacher sick leave
((SELECT id FROM users WHERE username = 'admin' LIMIT 1), 2, 'teacher', 30, true, true, NOW()), -- Admin can approve teacher casual leave
((SELECT id FROM users WHERE username = 'admin' LIMIT 1), 3, 'teacher', 30, true, true, NOW()), -- Admin can approve teacher emergency leave
((SELECT id FROM users WHERE username = 'admin' LIMIT 1), 4, 'teacher', 90, true, true, NOW()), -- Admin can approve teacher medical leave
((SELECT id FROM users WHERE username = 'admin' LIMIT 1), 5, 'teacher', 30, true, true, NOW())  -- Admin can approve teacher personal leave
ON CONFLICT DO NOTHING;

-- =====================================================
-- Sample Leave Calendar Entries (for approved leaves)
-- =====================================================

-- Calendar entries for approved student leave (Jan 20-22, 2024)
INSERT INTO leave_calendar (
    leave_request_id, leave_date, applicant_id, applicant_type, leave_type_id,
    year, month, day_of_week, created_at
) VALUES 
(2, '2024-01-20', 1, 'student', 2, 2024, 1, 6, NOW()), -- Saturday
(2, '2024-01-21', 1, 'student', 2, 2024, 1, 7, NOW()), -- Sunday  
(2, '2024-01-22', 1, 'student', 2, 2024, 1, 1, NOW())  -- Monday
ON CONFLICT DO NOTHING;

-- Calendar entries for approved teacher leave (Jan 25-27, 2024)
INSERT INTO leave_calendar (
    leave_request_id, leave_date, applicant_id, applicant_type, leave_type_id,
    year, month, day_of_week, created_at
) VALUES 
(5, '2024-01-25', 1, 'teacher', 1, 2024, 1, 4, NOW()), -- Thursday
(5, '2024-01-26', 1, 'teacher', 1, 2024, 1, 5, NOW()), -- Friday
(5, '2024-01-27', 1, 'teacher', 1, 2024, 1, 6, NOW())  -- Saturday
ON CONFLICT DO NOTHING;

-- Calendar entries for approved teacher casual leave (Jan 15-16, 2024)
INSERT INTO leave_calendar (
    leave_request_id, leave_date, applicant_id, applicant_type, leave_type_id,
    year, month, day_of_week, created_at
) VALUES 
(7, '2024-01-15', 1, 'teacher', 2, 2024, 1, 1, NOW()), -- Monday
(7, '2024-01-16', 1, 'teacher', 2, 2024, 1, 2, NOW())  -- Tuesday
ON CONFLICT DO NOTHING;

-- =====================================================
-- Verification Queries
-- =====================================================

-- Show sample leave requests
SELECT 
    'SAMPLE LEAVE REQUESTS:' as info,
    lr.id,
    lr.applicant_type,
    lr.applicant_id,
    lt.name as leave_type,
    lr.start_date,
    lr.end_date,
    lr.total_days,
    ls.name as status,
    lr.reason
FROM leave_requests lr
JOIN leave_types lt ON lr.leave_type_id = lt.id
JOIN leave_statuses ls ON lr.leave_status_id = ls.id
ORDER BY lr.created_at DESC
LIMIT 10;

-- Show leave balance summary
SELECT
    'LEAVE BALANCE SUMMARY:' as info,
    lb.teacher_id,
    'Casual Leave' as leave_type,
    lb.casual_leave_total as allocated_days,
    lb.casual_leave_used as used_days,
    lb.casual_leave_balance as available_days
FROM leave_balance lb
UNION ALL
SELECT
    'LEAVE BALANCE SUMMARY:' as info,
    lb.teacher_id,
    'Sick Leave' as leave_type,
    lb.sick_leave_total as allocated_days,
    lb.sick_leave_used as used_days,
    lb.sick_leave_balance as available_days
FROM leave_balance lb
UNION ALL
SELECT
    'LEAVE BALANCE SUMMARY:' as info,
    lb.teacher_id,
    'Earned Leave' as leave_type,
    lb.earned_leave_total as allocated_days,
    lb.earned_leave_used as used_days,
    lb.earned_leave_balance as available_days
FROM leave_balance lb
ORDER BY teacher_id, leave_type;

-- Show leave policies
SELECT 
    'LEAVE POLICIES:' as info,
    lp.policy_name,
    lp.applicant_type,
    lt.name as leave_type,
    lp.max_days_per_year,
    lp.requires_medical_certificate
FROM leave_policies lp
JOIN leave_types lt ON lp.leave_type_id = lt.id
WHERE lp.is_active = true
ORDER BY lp.applicant_type, lt.name;
