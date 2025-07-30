-- =====================================================
-- Sample Student Data
-- =====================================================

-- Insert sample students with comprehensive information
INSERT INTO students (
    admission_number, first_name, last_name, date_of_birth, gender, class, section, roll_number,
    phone, email, address, city, state, postal_code, country,
    father_name, father_phone, father_email, father_occupation,
    mother_name, mother_phone, mother_email, mother_occupation,
    emergency_contact_name, emergency_contact_phone, emergency_contact_relation,
    admission_date, session_year, is_active, created_at
) VALUES 
-- Student 1: Aarav Sharma
(
    'SNS2024001', 'Aarav', 'Sharma', '2015-03-15', 'Male', 'Class 5', 'A', '001',
    '9876543301', 'aarav.sharma@student.sunriseschool.edu', 
    '123 MG Road, Koramangala', 'Bangalore', 'Karnataka', '560034', 'India',
    'Rajesh Sharma', '9876543220', 'rajesh.sharma@gmail.com', 'Software Engineer',
    'Priya Sharma', '9876543221', 'priya.sharma@gmail.com', 'Teacher',
    'Rajesh Sharma', '9876543220', 'Father',
    '2024-04-01', '2024-25', true, NOW()
),
-- Student 2: Ananya Patel
(
    'SNS2024002', 'Ananya', 'Patel', '2016-07-22', 'Female', 'Class 4', 'B', '002',
    '9876543302', 'ananya.patel@student.sunriseschool.edu',
    '456 Brigade Road, Richmond Town', 'Bangalore', 'Karnataka', '560025', 'India',
    'Amit Patel', '9876543222', 'amit.patel@gmail.com', 'Business Owner',
    'Kavya Patel', '9876543223', 'kavya.patel@gmail.com', 'Doctor',
    'Amit Patel', '9876543222', 'Father',
    '2024-04-01', '2024-25', true, NOW()
),
-- Student 3: Arjun Kumar
(
    'SNS2024003', 'Arjun', 'Kumar', '2014-11-08', 'Male', 'Class 6', 'A', '003',
    '9876543303', 'arjun.kumar@student.sunriseschool.edu',
    '789 Koramangala 5th Block', 'Bangalore', 'Karnataka', '560095', 'India',
    'Suresh Kumar', '9876543224', 'suresh.kumar@gmail.com', 'Manager',
    'Lakshmi Kumar', '9876543225', 'lakshmi.kumar@gmail.com', 'Homemaker',
    'Suresh Kumar', '9876543224', 'Father',
    '2024-04-01', '2024-25', true, NOW()
),
-- Student 4: Diya Singh
(
    'SNS2024004', 'Diya', 'Singh', '2017-01-12', 'Female', 'Class 3', 'A', '004',
    '9876543304', 'diya.singh@student.sunriseschool.edu',
    '321 Indiranagar 100 Feet Road', 'Bangalore', 'Karnataka', '560038', 'India',
    'Vikram Singh', '9876543226', 'vikram.singh@gmail.com', 'Consultant',
    'Meera Singh', '9876543227', 'meera.singh@gmail.com', 'Architect',
    'Vikram Singh', '9876543226', 'Father',
    '2024-04-01', '2024-25', true, NOW()
),
-- Student 5: Ishaan Gupta
(
    'SNS2024005', 'Ishaan', 'Gupta', '2015-09-30', 'Male', 'Class 5', 'B', '005',
    '9876543305', 'ishaan.gupta@student.sunriseschool.edu',
    '654 Whitefield Main Road', 'Bangalore', 'Karnataka', '560066', 'India',
    'Rohit Gupta', '9876543228', 'rohit.gupta@gmail.com', 'Chartered Accountant',
    'Neha Gupta', '9876543229', 'neha.gupta@gmail.com', 'Lawyer',
    'Rohit Gupta', '9876543228', 'Father',
    '2024-04-01', '2024-25', true, NOW()
),
-- Student 6: Kavya Reddy
(
    'SNS2024006', 'Kavya', 'Reddy', '2016-05-18', 'Female', 'Class 4', 'A', '006',
    '9876543306', 'kavya.reddy@student.sunriseschool.edu',
    '987 Electronic City Phase 1', 'Bangalore', 'Karnataka', '560100', 'India',
    'Ravi Reddy', '9876543230', 'ravi.reddy@gmail.com', 'Engineer',
    'Sita Reddy', '9876543231', 'sita.reddy@gmail.com', 'Nurse',
    'Ravi Reddy', '9876543230', 'Father',
    '2024-04-01', '2024-25', true, NOW()
),
-- Student 7: Rohan Joshi
(
    'SNS2024007', 'Rohan', 'Joshi', '2013-12-03', 'Male', 'Class 7', 'A', '007',
    '9876543307', 'rohan.joshi@student.sunriseschool.edu',
    '111 Jayanagar 4th Block', 'Bangalore', 'Karnataka', '560011', 'India',
    'Anil Joshi', '9876543232', 'anil.joshi@gmail.com', 'Bank Manager',
    'Sunita Joshi', '9876543233', 'sunita.joshi@gmail.com', 'Professor',
    'Anil Joshi', '9876543232', 'Father',
    '2024-04-01', '2024-25', true, NOW()
),
-- Student 8: Siya Agarwal
(
    'SNS2024008', 'Siya', 'Agarwal', '2018-08-25', 'Female', 'Class 2', 'B', '008',
    '9876543308', 'siya.agarwal@student.sunriseschool.edu',
    '222 HSR Layout Sector 1', 'Bangalore', 'Karnataka', '560102', 'India',
    'Deepak Agarwal', '9876543234', 'deepak.agarwal@gmail.com', 'Marketing Manager',
    'Pooja Agarwal', '9876543235', 'pooja.agarwal@gmail.com', 'Interior Designer',
    'Deepak Agarwal', '9876543234', 'Father',
    '2024-04-01', '2024-25', true, NOW()
),
-- Student 9: Vihaan Malhotra
(
    'SNS2024009', 'Vihaan', 'Malhotra', '2014-06-14', 'Male', 'Class 6', 'B', '009',
    '9876543309', 'vihaan.malhotra@student.sunriseschool.edu',
    '333 Marathahalli Outer Ring Road', 'Bangalore', 'Karnataka', '560037', 'India',
    'Karan Malhotra', '9876543236', 'karan.malhotra@gmail.com', 'IT Director',
    'Ritu Malhotra', '9876543237', 'ritu.malhotra@gmail.com', 'Fashion Designer',
    'Karan Malhotra', '9876543236', 'Father',
    '2024-04-01', '2024-25', true, NOW()
),
-- Student 10: Zara Khan
(
    'SNS2024010', 'Zara', 'Khan', '2017-04-09', 'Female', 'Class 3', 'B', '010',
    '9876543310', 'zara.khan@student.sunriseschool.edu',
    '444 Banashankari 2nd Stage', 'Bangalore', 'Karnataka', '560070', 'India',
    'Imran Khan', '9876543238', 'imran.khan@gmail.com', 'Restaurant Owner',
    'Fatima Khan', '9876543239', 'fatima.khan@gmail.com', 'Pharmacist',
    'Imran Khan', '9876543238', 'Father',
    '2024-04-01', '2024-25', true, NOW()
) ON CONFLICT (admission_number) DO NOTHING;

-- Add more students for comprehensive testing
INSERT INTO students (
    admission_number, first_name, last_name, date_of_birth, gender, class, section, roll_number,
    phone, email, address, city, state, postal_code, country,
    father_name, father_phone, father_email, father_occupation,
    mother_name, mother_phone, mother_email, mother_occupation,
    emergency_contact_name, emergency_contact_phone, emergency_contact_relation,
    admission_date, session_year, is_active, created_at
) VALUES
-- Student 11: Aditya Verma (LKG)
(
    'SNS2024011', 'Aditya', 'Verma', '2019-02-28', 'Male', 'LKG', 'A', '011',
    '9876543311', 'aditya.verma@student.sunriseschool.edu',
    '555 Rajajinagar 1st Block', 'Bangalore', 'Karnataka', '560010', 'India',
    'Manoj Verma', '9876543240', 'manoj.verma@gmail.com', 'Civil Engineer',
    'Rekha Verma', '9876543241', 'rekha.verma@gmail.com', 'Housewife',
    'Manoj Verma', '9876543240', 'Father',
    '2024-04-01', '2024-25', true, NOW()
),
-- Student 12: Priya Nair (UKG)
(
    'SNS2024012', 'Priya', 'Nair', '2018-11-15', 'Female', 'UKG', 'A', '012',
    '9876543312', 'priya.nair@student.sunriseschool.edu',
    '666 Basavanagudi Bull Temple Road', 'Bangalore', 'Karnataka', '560019', 'India',
    'Sunil Nair', '9876543242', 'sunil.nair@gmail.com', 'Government Officer',
    'Latha Nair', '9876543243', 'latha.nair@gmail.com', 'School Principal',
    'Sunil Nair', '9876543242', 'Father',
    '2024-04-01', '2024-25', true, NOW()
),
-- Student 13: Karan Chopra (Class 8)
(
    'SNS2024013', 'Karan', 'Chopra', '2012-07-20', 'Male', 'Class 8', 'A', '013',
    '9876543313', 'karan.chopra@student.sunriseschool.edu',
    '777 Malleshwaram 15th Cross', 'Bangalore', 'Karnataka', '560003', 'India',
    'Rajiv Chopra', '9876543244', 'rajiv.chopra@gmail.com', 'Businessman',
    'Kavita Chopra', '9876543245', 'kavita.chopra@gmail.com', 'Yoga Instructor',
    'Rajiv Chopra', '9876543244', 'Father',
    '2024-04-01', '2024-25', true, NOW()
),
-- Student 14: Sneha Bansal (PG)
(
    'SNS2024014', 'Sneha', 'Bansal', '2020-01-10', 'Female', 'PG', 'A', '014',
    '9876543314', 'sneha.bansal@student.sunriseschool.edu',
    '888 RT Nagar Main Road', 'Bangalore', 'Karnataka', '560032', 'India',
    'Vinod Bansal', '9876543246', 'vinod.bansal@gmail.com', 'Textile Merchant',
    'Seema Bansal', '9876543247', 'seema.bansal@gmail.com', 'Beautician',
    'Vinod Bansal', '9876543246', 'Father',
    '2024-04-01', '2024-25', true, NOW()
),
-- Student 15: Aryan Saxena (Class 7)
(
    'SNS2024015', 'Aryan', 'Saxena', '2013-10-05', 'Male', 'Class 7', 'B', '015',
    '9876543315', 'aryan.saxena@student.sunriseschool.edu',
    '999 Yelahanka New Town', 'Bangalore', 'Karnataka', '560064', 'India',
    'Ashok Saxena', '9876543248', 'ashok.saxena@gmail.com', 'Chartered Accountant',
    'Nisha Saxena', '9876543249', 'nisha.saxena@gmail.com', 'Music Teacher',
    'Ashok Saxena', '9876543248', 'Father',
    '2024-04-01', '2024-25', true, NOW()
) ON CONFLICT (admission_number) DO NOTHING;

-- Display inserted students
SELECT
    admission_number,
    first_name || ' ' || last_name as student_name,
    class,
    section,
    father_name,
    is_active
FROM students
ORDER BY class, section, roll_number;
