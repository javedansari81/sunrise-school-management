-- =====================================================
-- Sample Teacher Data
-- =====================================================

-- Insert sample teachers with comprehensive information
INSERT INTO teachers (
    employee_id, first_name, last_name, date_of_birth, gender,
    phone, email, address, city, state, postal_code, country,
    emergency_contact_name, emergency_contact_phone, emergency_contact_relation,
    position, department, subjects, qualification, experience_years,
    joining_date, employment_type, salary, class_teacher_of, classes_assigned,
    is_active, created_at
) VALUES 
-- Teacher 1: Priya Sharma (Mathematics)
(
    'EMP001', 'Priya', 'Sharma', '1985-06-15', 'Female',
    '9876543401', 'priya.sharma@sunriseschool.edu',
    '123 Teachers Colony, Jayanagar', 'Bangalore', 'Karnataka', '560011', 'India',
    'Rajesh Sharma', '9876543451', 'Husband',
    'Senior Teacher', 'Mathematics', 'Mathematics, Statistics',
    'M.Sc Mathematics, B.Ed', 8,
    '2020-06-01', 'Full Time', 45000.00, 'Class 5A', 'Class 5A, Class 5B, Class 6A',
    true, NOW()
),
-- Teacher 2: Amit Patel (Science)
(
    'EMP002', 'Amit', 'Patel', '1982-03-22', 'Male',
    '9876543402', 'amit.patel@sunriseschool.edu',
    '456 Science Block, Koramangala', 'Bangalore', 'Karnataka', '560034', 'India',
    'Kavya Patel', '9876543452', 'Wife',
    'Head Teacher', 'Science', 'Physics, Chemistry, Biology',
    'M.Sc Physics, B.Ed', 12,
    '2018-04-15', 'Full Time', 55000.00, 'Class 7A', 'Class 6A, Class 7A, Class 8A',
    true, NOW()
),
-- Teacher 3: Sunita Gupta (English)
(
    'EMP003', 'Sunita', 'Gupta', '1988-09-10', 'Female',
    '9876543403', 'sunita.gupta@sunriseschool.edu',
    '789 English Department, Indiranagar', 'Bangalore', 'Karnataka', '560038', 'India',
    'Mohan Gupta', '9876543453', 'Husband',
    'Teacher', 'English', 'English Literature, Grammar',
    'M.A English, B.Ed', 6,
    '2021-07-01', 'Full Time', 42000.00, 'Class 4A', 'Class 3A, Class 4A, Class 4B',
    true, NOW()
),
-- Teacher 4: Rahul Singh (Physical Education)
(
    'EMP004', 'Rahul', 'Singh', '1990-12-05', 'Male',
    '9876543404', 'rahul.singh@sunriseschool.edu',
    '321 Sports Complex, Whitefield', 'Bangalore', 'Karnataka', '560066', 'India',
    'Priya Singh', '9876543454', 'Wife',
    'Sports Teacher', 'Physical Education', 'Sports, Physical Training',
    'B.P.Ed, Diploma in Sports Coaching', 5,
    '2022-01-10', 'Full Time', 38000.00, NULL, 'All Classes',
    true, NOW()
),
-- Teacher 5: Meera Joshi (Hindi)
(
    'EMP005', 'Meera', 'Joshi', '1987-04-18', 'Female',
    '9876543405', 'meera.joshi@sunriseschool.edu',
    '654 Hindi Bhawan, Malleshwaram', 'Bangalore', 'Karnataka', '560003', 'India',
    'Anil Joshi', '9876543455', 'Husband',
    'Teacher', 'Hindi', 'Hindi Language, Hindi Literature',
    'M.A Hindi, B.Ed', 7,
    '2020-08-15', 'Full Time', 40000.00, 'Class 6A', 'Class 5A, Class 6A, Class 7A',
    true, NOW()
),
-- Teacher 6: Deepak Kumar (Social Studies)
(
    'EMP006', 'Deepak', 'Kumar', '1984-11-30', 'Male',
    '9876543406', 'deepak.kumar@sunriseschool.edu',
    '987 History Department, Basavanagudi', 'Bangalore', 'Karnataka', '560019', 'India',
    'Sunita Kumar', '9876543456', 'Wife',
    'Teacher', 'Social Studies', 'History, Geography, Civics',
    'M.A History, B.Ed', 9,
    '2019-03-20', 'Full Time', 43000.00, 'Class 8A', 'Class 6A, Class 7A, Class 8A',
    true, NOW()
),
-- Teacher 7: Kavita Reddy (Art & Craft)
(
    'EMP007', 'Kavita', 'Reddy', '1991-07-25', 'Female',
    '9876543407', 'kavita.reddy@sunriseschool.edu',
    '111 Art Studio, HSR Layout', 'Bangalore', 'Karnataka', '560102', 'India',
    'Ravi Reddy', '9876543457', 'Husband',
    'Art Teacher', 'Arts', 'Drawing, Painting, Craft',
    'B.F.A, Diploma in Art Education', 4,
    '2023-06-01', 'Part Time', 25000.00, NULL, 'Class 1-8',
    true, NOW()
),
-- Teacher 8: Vikram Malhotra (Computer Science)
(
    'EMP008', 'Vikram', 'Malhotra', '1986-02-14', 'Male',
    '9876543408', 'vikram.malhotra@sunriseschool.edu',
    '222 Computer Lab, Electronic City', 'Bangalore', 'Karnataka', '560100', 'India',
    'Ritu Malhotra', '9876543458', 'Wife',
    'Computer Teacher', 'Computer Science', 'Computer Applications, Programming',
    'MCA, B.Ed', 8,
    '2020-01-15', 'Full Time', 48000.00, NULL, 'Class 3-8',
    true, NOW()
),
-- Teacher 9: Anjali Nair (Music)
(
    'EMP009', 'Anjali', 'Nair', '1989-08-08', 'Female',
    '9876543409', 'anjali.nair@sunriseschool.edu',
    '333 Music Room, Rajajinagar', 'Bangalore', 'Karnataka', '560010', 'India',
    'Sunil Nair', '9876543459', 'Husband',
    'Music Teacher', 'Music', 'Vocal Music, Instrumental Music',
    'M.A Music, Diploma in Classical Music', 6,
    '2021-04-01', 'Part Time', 30000.00, NULL, 'All Classes',
    true, NOW()
),
-- Teacher 10: Ravi Agarwal (Librarian)
(
    'EMP010', 'Ravi', 'Agarwal', '1983-01-20', 'Male',
    '9876543410', 'ravi.agarwal@sunriseschool.edu',
    '444 Library Block, Marathahalli', 'Bangalore', 'Karnataka', '560037', 'India',
    'Pooja Agarwal', '9876543460', 'Wife',
    'Librarian', 'Library', 'Library Management, Reading Programs',
    'M.Lib.Sc, B.A', 10,
    '2017-09-01', 'Full Time', 35000.00, NULL, 'Library Services',
    true, NOW()
) ON CONFLICT (employee_id) DO NOTHING;

-- Insert teacher qualifications
INSERT INTO teacher_qualifications (
    teacher_id, degree_type, degree_name, institution, year_of_completion, grade_percentage, specialization
) VALUES 
((SELECT id FROM teachers WHERE employee_id = 'EMP001'), 'Master', 'M.Sc Mathematics', 'Bangalore University', 2007, 85.5, 'Pure Mathematics'),
((SELECT id FROM teachers WHERE employee_id = 'EMP001'), 'Bachelor', 'B.Ed', 'Karnataka State Open University', 2008, 78.2, 'Mathematics Education'),
((SELECT id FROM teachers WHERE employee_id = 'EMP002'), 'Master', 'M.Sc Physics', 'Indian Institute of Science', 2004, 88.7, 'Theoretical Physics'),
((SELECT id FROM teachers WHERE employee_id = 'EMP002'), 'Bachelor', 'B.Ed', 'Mysore University', 2005, 82.1, 'Science Education'),
((SELECT id FROM teachers WHERE employee_id = 'EMP003'), 'Master', 'M.A English', 'Bangalore University', 2010, 79.8, 'English Literature'),
((SELECT id FROM teachers WHERE employee_id = 'EMP003'), 'Bachelor', 'B.Ed', 'Karnataka State Open University', 2011, 81.5, 'English Education')
ON CONFLICT DO NOTHING;

-- Display inserted teachers
SELECT 
    employee_id,
    first_name || ' ' || last_name as teacher_name,
    position,
    department,
    class_teacher_of,
    employment_type,
    is_active
FROM teachers 
ORDER BY employee_id;
