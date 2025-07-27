-- Sample Data for Sunrise School Management System
-- This script inserts sample data for testing and demonstration

-- Insert sample users (admin, teachers, students)
INSERT INTO users (first_name, last_name, mobile, email, password, user_type) VALUES
('Admin', 'User', '9876543210', 'admin@sunriseschool.edu', '$2b$12$wq4BwIaHKkm5IPdmm9rvz.pyOmvDofmSGt9m5zJrRiv8Q6IuDM5tC', 'admin'),
('John', 'Teacher', '9876543211', 'teacher@sunriseschool.edu', '$2b$12$wq4BwIaHKkm5IPdmm9rvz.pyOmvDofmSGt9m5zJrRiv8Q6IuDM5tC', 'teacher'),
('Jane', 'Student', '9876543212', 'student@sunriseschool.edu', '$2b$12$wq4BwIaHKkm5IPdmm9rvz.pyOmvDofmSGt9m5zJrRiv8Q6IuDM5tC', 'student');

-- Insert sample teachers
INSERT INTO teachers (employee_id, first_name, last_name, date_of_birth, gender, email, phone, position, department, qualification, joining_date, subjects) VALUES
('EMP001', 'John', 'Smith', '1985-06-15', 'Male', 'john.smith@sunriseschool.edu', '9876543211', 'Senior Teacher', 'Mathematics', 'Master''s Degree', '2020-06-01', '["Mathematics", "Physics"]'),
('EMP002', 'Sarah', 'Johnson', '1988-03-22', 'Female', 'sarah.johnson@sunriseschool.edu', '9876543213', 'Teacher', 'English', 'Bachelor''s Degree', '2021-07-15', '["English", "Literature"]'),
('EMP003', 'Michael', 'Brown', '1982-11-08', 'Male', 'michael.brown@sunriseschool.edu', '9876543214', 'Head Teacher', 'Science', 'Master''s Degree', '2019-04-01', '["Chemistry", "Biology"]'),
('EMP004', 'Emily', 'Davis', '1990-09-12', 'Female', 'emily.davis@sunriseschool.edu', '9876543215', 'Teacher', 'Social Studies', 'Bachelor''s Degree', '2022-08-01', '["History", "Geography"]'),
('EMP005', 'Robert', 'Wilson', '1987-01-25', 'Male', 'robert.wilson@sunriseschool.edu', '9876543216', 'Teacher', 'Physical Education', 'Bachelor''s Degree', '2021-03-15', '["Physical Education", "Sports"]');

-- Insert sample students
INSERT INTO students (admission_number, first_name, last_name, date_of_birth, gender, current_class, section, roll_number, father_name, mother_name, admission_date, phone, email, address) VALUES
('SNS2024001', 'Aarav', 'Sharma', '2012-05-15', 'Male', 'Class 5', 'A', '001', 'Rajesh Sharma', 'Priya Sharma', '2024-04-01', '9876543220', 'aarav.sharma@gmail.com', '123 Main Street, Delhi'),
('SNS2024002', 'Ananya', 'Patel', '2013-08-22', 'Female', 'Class 4', 'B', '002', 'Suresh Patel', 'Meera Patel', '2024-04-01', '9876543221', 'ananya.patel@gmail.com', '456 Park Avenue, Mumbai'),
('SNS2024003', 'Arjun', 'Kumar', '2011-12-10', 'Male', 'Class 6', 'A', '003', 'Vikram Kumar', 'Sunita Kumar', '2024-04-01', '9876543222', 'arjun.kumar@gmail.com', '789 Garden Road, Bangalore'),
('SNS2024004', 'Diya', 'Singh', '2014-03-18', 'Female', 'Class 3', 'A', '004', 'Amit Singh', 'Kavita Singh', '2024-04-01', '9876543223', 'diya.singh@gmail.com', '321 Lake View, Chennai'),
('SNS2024005', 'Ishaan', 'Gupta', '2012-07-25', 'Male', 'Class 5', 'B', '005', 'Rohit Gupta', 'Neha Gupta', '2024-04-01', '9876543224', 'ishaan.gupta@gmail.com', '654 Hill Station, Pune'),
('SNS2024006', 'Kavya', 'Reddy', '2013-11-30', 'Female', 'Class 4', 'A', '006', 'Srinivas Reddy', 'Lakshmi Reddy', '2024-04-01', '9876543225', 'kavya.reddy@gmail.com', '987 Beach Road, Hyderabad'),
('SNS2024007', 'Rohan', 'Joshi', '2010-09-05', 'Male', 'Class 7', 'A', '007', 'Prakash Joshi', 'Asha Joshi', '2024-04-01', '9876543226', 'rohan.joshi@gmail.com', '147 Valley View, Kolkata'),
('SNS2024008', 'Siya', 'Agarwal', '2015-01-12', 'Female', 'Class 2', 'A', '008', 'Manish Agarwal', 'Pooja Agarwal', '2024-04-01', '9876543227', 'siya.agarwal@gmail.com', '258 River Side, Jaipur'),
('SNS2024009', 'Vihaan', 'Malhotra', '2011-04-20', 'Male', 'Class 6', 'B', '009', 'Deepak Malhotra', 'Ritu Malhotra', '2024-04-01', '9876543228', 'vihaan.malhotra@gmail.com', '369 Mountain View, Chandigarh'),
('SNS2024010', 'Zara', 'Khan', '2014-06-08', 'Female', 'Class 3', 'B', '010', 'Salman Khan', 'Fatima Khan', '2024-04-01', '9876543229', 'zara.khan@gmail.com', '741 City Center, Lucknow');

-- Insert fee structures for different classes
INSERT INTO fee_structures (class_name, session_year, tuition_fee, admission_fee, development_fee, activity_fee, transport_fee, library_fee, lab_fee, exam_fee, other_fee, total_annual_fee) VALUES
('PG', '2024-25', 20000, 2000, 1500, 1000, 3000, 500, 0, 500, 500, 29000),
('LKG', '2024-25', 22000, 2000, 1500, 1000, 3000, 500, 0, 500, 500, 31000),
('UKG', '2024-25', 24000, 2000, 1500, 1000, 3000, 500, 0, 500, 500, 33000),
('Class 1', '2024-25', 26000, 2000, 1500, 1200, 3000, 600, 500, 600, 600, 36000),
('Class 2', '2024-25', 28000, 2000, 1500, 1200, 3000, 600, 500, 600, 600, 38000),
('Class 3', '2024-25', 30000, 2000, 1500, 1200, 3000, 600, 500, 600, 600, 40000),
('Class 4', '2024-25', 32000, 2000, 1500, 1200, 3000, 600, 500, 600, 600, 42000),
('Class 5', '2024-25', 34000, 2000, 1500, 1200, 3000, 600, 500, 600, 600, 44000),
('Class 6', '2024-25', 36000, 2000, 1500, 1200, 3000, 600, 800, 600, 600, 46300),
('Class 7', '2024-25', 38000, 2000, 1500, 1200, 3000, 600, 800, 600, 600, 48300),
('Class 8', '2024-25', 40000, 2000, 1500, 1200, 3000, 600, 800, 600, 600, 50300);

-- Insert sample fee records
INSERT INTO fee_records (student_id, session_year, payment_type, total_amount, balance_amount, due_date) VALUES
(1, '2024-25', 'Quarterly', 11000, 11000, '2024-07-15'),
(2, '2024-25', 'Quarterly', 10500, 5500, '2024-07-15'),
(3, '2024-25', 'Half Yearly', 23150, 23150, '2024-09-15'),
(4, '2024-25', 'Monthly', 3333, 0, '2024-06-15'),
(5, '2024-25', 'Quarterly', 11000, 8000, '2024-07-15'),
(6, '2024-25', 'Monthly', 3500, 3500, '2024-06-15'),
(7, '2024-25', 'Half Yearly', 24150, 12000, '2024-09-15'),
(8, '2024-25', 'Quarterly', 10000, 10000, '2024-07-15'),
(9, '2024-25', 'Monthly', 3858, 1858, '2024-06-15'),
(10, '2024-25', 'Quarterly', 10000, 5000, '2024-07-15');

-- Update fee records with paid amounts
UPDATE fee_records SET paid_amount = 5000 WHERE id = 2;
UPDATE fee_records SET paid_amount = 3333, status = 'Paid' WHERE id = 4;
UPDATE fee_records SET paid_amount = 3000 WHERE id = 5;
UPDATE fee_records SET paid_amount = 12150 WHERE id = 7;
UPDATE fee_records SET paid_amount = 2000 WHERE id = 9;
UPDATE fee_records SET paid_amount = 5000 WHERE id = 10;

-- Insert sample fee payments
INSERT INTO fee_payments (fee_record_id, amount, payment_method, payment_date, transaction_id) VALUES
(2, 5000, 'Online', '2024-06-01', 'TXN001'),
(4, 3333, 'Cash', '2024-06-05', 'CASH001'),
(5, 3000, 'UPI', '2024-06-10', 'UPI001'),
(7, 12150, 'Cheque', '2024-06-15', 'CHQ001'),
(9, 2000, 'Card', '2024-06-20', 'CARD001'),
(10, 5000, 'Online', '2024-06-25', 'TXN002');

-- Insert sample leave requests
INSERT INTO leave_requests (student_id, leave_type, start_date, end_date, total_days, reason, status) VALUES
(1, 'Sick Leave', '2024-06-10', '2024-06-12', 3, 'Fever and cold', 'Approved'),
(2, 'Family Function', '2024-06-20', '2024-06-22', 3, 'Sister''s wedding', 'Pending'),
(3, 'Medical Leave', '2024-06-15', '2024-06-17', 3, 'Doctor appointment', 'Approved'),
(4, 'Casual Leave', '2024-06-25', '2024-06-25', 1, 'Personal work', 'Pending'),
(5, 'Emergency Leave', '2024-06-18', '2024-06-19', 2, 'Family emergency', 'Approved'),
(6, 'Sick Leave', '2024-06-30', '2024-07-01', 2, 'Stomach ache', 'Pending'),
(7, 'Other', '2024-07-05', '2024-07-05', 1, 'School event participation', 'Approved');

-- Update some leave requests with approval details
UPDATE leave_requests SET approved_by = 1, approved_at = NOW() WHERE status = 'Approved';

-- Insert sample expenses
INSERT INTO expenses (title, description, category, amount, tax_amount, total_amount, vendor_name, status, requested_by, expense_date) VALUES
('Office Stationery', 'Pens, pencils, notebooks for office use', 'Office Supplies', 5000, 900, 5900, 'ABC Stationery', 'Approved', 1, '2024-06-01'),
('Classroom Projector', 'New projector for Class 5 classroom', 'Equipment', 25000, 4500, 29500, 'Tech Solutions', 'Pending', 2, '2024-06-05'),
('Electricity Bill', 'Monthly electricity bill for June', 'Utilities', 15000, 0, 15000, 'State Electricity Board', 'Paid', 1, '2024-06-10'),
('Bus Maintenance', 'Monthly maintenance for school bus', 'Transport', 8000, 1440, 9440, 'Auto Service Center', 'Approved', 1, '2024-06-15'),
('Library Books', 'New books for school library', 'Academic Materials', 12000, 2160, 14160, 'Book Publishers', 'Pending', 2, '2024-06-20'),
('Cleaning Supplies', 'Cleaning materials for school premises', 'Maintenance', 3000, 540, 3540, 'Clean & Fresh', 'Approved', 1, '2024-06-25'),
('Sports Equipment', 'Cricket bats, footballs, and other sports items', 'Equipment', 7000, 1260, 8260, 'Sports World', 'Pending', 2, '2024-06-30');

-- Update some expenses with approval details
UPDATE expenses SET approved_by = 1, approved_at = NOW() WHERE status IN ('Approved', 'Paid');

-- Update users table to link with student and teacher profiles
UPDATE users SET teacher_id = 1 WHERE email = 'teacher@sunriseschool.edu';
UPDATE users SET student_id = 1 WHERE email = 'student@sunriseschool.edu';

-- Update teacher email to match user email
UPDATE teachers SET email = 'teacher@sunriseschool.edu' WHERE employee_id = 'EMP001';

-- Insert additional sample data for better testing

-- More students for different classes
INSERT INTO students (admission_number, first_name, last_name, date_of_birth, gender, current_class, section, roll_number, father_name, mother_name, admission_date) VALUES
('SNS2024011', 'Aditya', 'Verma', '2016-02-14', 'Male', 'LKG', 'A', '011', 'Sunil Verma', 'Rekha Verma', '2024-04-01'),
('SNS2024012', 'Priya', 'Nair', '2015-10-30', 'Female', 'UKG', 'A', '012', 'Ravi Nair', 'Sita Nair', '2024-04-01'),
('SNS2024013', 'Karan', 'Chopra', '2009-08-17', 'Male', 'Class 8', 'A', '013', 'Vinod Chopra', 'Anita Chopra', '2024-04-01'),
('SNS2024014', 'Sneha', 'Bansal', '2017-04-05', 'Female', 'PG', 'A', '014', 'Rajesh Bansal', 'Geeta Bansal', '2024-04-01'),
('SNS2024015', 'Aryan', 'Saxena', '2010-11-22', 'Male', 'Class 7', 'B', '015', 'Manoj Saxena', 'Shweta Saxena', '2024-04-01');

-- More fee records for the new students
INSERT INTO fee_records (student_id, session_year, payment_type, total_amount, balance_amount, due_date) VALUES
(11, '2024-25', 'Monthly', 2583, 2583, '2024-06-15'),
(12, '2024-25', 'Quarterly', 8250, 4000, '2024-07-15'),
(13, '2024-25', 'Half Yearly', 25150, 25150, '2024-09-15'),
(14, '2024-25', 'Monthly', 2417, 1000, '2024-06-15'),
(15, '2024-25', 'Quarterly', 12075, 6000, '2024-07-15');

-- Update some of the new fee records
UPDATE fee_records SET paid_amount = 4250 WHERE id = 12;
UPDATE fee_records SET paid_amount = 1417 WHERE id = 14;
UPDATE fee_records SET paid_amount = 6075 WHERE id = 15;

-- More leave requests
INSERT INTO leave_requests (student_id, leave_type, start_date, end_date, total_days, reason, status) VALUES
(11, 'Sick Leave', '2024-07-08', '2024-07-09', 2, 'Cold and cough', 'Pending'),
(12, 'Family Function', '2024-07-15', '2024-07-16', 2, 'Cousin''s birthday', 'Approved'),
(13, 'Medical Leave', '2024-07-20', '2024-07-22', 3, 'Dental treatment', 'Pending'),
(14, 'Casual Leave', '2024-07-25', '2024-07-25', 1, 'Family outing', 'Approved'),
(15, 'Other', '2024-07-30', '2024-07-30', 1, 'School competition', 'Approved');

-- Update approval status for new leave requests
UPDATE leave_requests SET approved_by = 1, approved_at = NOW() WHERE id IN (17, 19, 20);
