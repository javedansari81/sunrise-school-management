-- Add sample teacher data for Faculty page testing
-- This script adds sample teachers if they don't already exist

-- Insert sample teachers
INSERT INTO teachers (
    employee_id, first_name, last_name, email, phone, 
    position, department, subjects, experience_years, 
    joining_date, is_active, created_at
) VALUES 
(
    'EMP001', 'Dr. Sarah', 'Johnson', 'sarah.johnson@sunriseschool.edu', '9876543210',
    'Principal', 'Administration', '["Management", "Leadership", "Educational Administration"]', 15,
    '2015-06-01', true, NOW()
),
(
    'EMP002', 'Mr. Rajesh', 'Kumar', 'rajesh.kumar@sunriseschool.edu', '9876543211',
    'Vice Principal', 'Administration', '["Mathematics", "Management"]', 12,
    '2017-07-15', true, NOW()
),
(
    'EMP003', 'Ms. Priya', 'Sharma', 'priya.sharma@sunriseschool.edu', '9876543212',
    'Head Teacher', 'Mathematics', '["Mathematics", "Statistics", "Algebra"]', 10,
    '2018-04-01', true, NOW()
),
(
    'EMP004', 'Dr. Amit', 'Patel', 'amit.patel@sunriseschool.edu', '9876543213',
    'Senior Teacher', 'Science', '["Physics", "Chemistry", "General Science"]', 8,
    '2019-08-20', true, NOW()
),
(
    'EMP005', 'Mrs. Sunita', 'Gupta', 'sunita.gupta@sunriseschool.edu', '9876543214',
    'Teacher', 'English', '["English Literature", "Grammar", "Creative Writing"]', 6,
    '2020-01-10', true, NOW()
),
(
    'EMP006', 'Mr. Vikram', 'Singh', 'vikram.singh@sunriseschool.edu', '9876543215',
    'Teacher', 'Social Studies', '["History", "Geography", "Civics"]', 5,
    '2020-06-15', true, NOW()
),
(
    'EMP007', 'Ms. Kavita', 'Reddy', 'kavita.reddy@sunriseschool.edu', '9876543216',
    'Teacher', 'Hindi', '["Hindi Literature", "Grammar", "Poetry"]', 4,
    '2021-03-01', true, NOW()
),
(
    'EMP008', 'Mr. Arjun', 'Nair', 'arjun.nair@sunriseschool.edu', '9876543217',
    'Teacher', 'Computer Science', '["Programming", "Web Development", "Database Management"]', 3,
    '2022-01-15', true, NOW()
),
(
    'EMP009', 'Mrs. Meera', 'Joshi', 'meera.joshi@sunriseschool.edu', '9876543218',
    'Teacher', 'Art', '["Drawing", "Painting", "Craft", "Art History"]', 7,
    '2019-09-01', true, NOW()
),
(
    'EMP010', 'Mr. Ravi', 'Agarwal', 'ravi.agarwal@sunriseschool.edu', '9876543219',
    'Physical Education Teacher', 'Sports', '["Physical Education", "Sports", "Yoga"]', 9,
    '2018-07-01', true, NOW()
)
ON CONFLICT (employee_id) DO NOTHING;

-- Verify the data was inserted
SELECT 
    employee_id, 
    CONCAT(first_name, ' ', last_name) as full_name,
    position,
    department,
    experience_years,
    is_active
FROM teachers 
WHERE is_active = true 
ORDER BY first_name, last_name;

-- Show count of active teachers
SELECT COUNT(*) as active_teacher_count 
FROM teachers 
WHERE is_active = true AND (is_deleted IS NULL OR is_deleted = false);
