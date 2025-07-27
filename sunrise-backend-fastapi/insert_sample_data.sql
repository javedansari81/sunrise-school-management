-- =====================================================
-- Sunrise School Management System - Sample Data
-- =====================================================

-- Insert Users (Admin, Teachers, Staff)
INSERT INTO users (first_name, last_name, mobile, email, password, user_type) VALUES
('Admin', 'User', '9876543210', 'admin@sunriseschool.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsHjxstm6', 'admin'),
('John', 'Smith', '9876543211', 'john.smith@sunriseschool.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsHjxstm6', 'teacher'),
('Sarah', 'Johnson', '9876543212', 'sarah.johnson@sunriseschool.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsHjxstm6', 'teacher'),
('Michael', 'Brown', '9876543213', 'michael.brown@sunriseschool.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsHjxstm6', 'staff'),
('Emily', 'Davis', '9876543214', 'emily.davis@sunriseschool.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsHjxstm6', 'teacher');

-- Insert Students
INSERT INTO students (admission_number, first_name, last_name, date_of_birth, gender, current_class, section, roll_number, 
                     father_name, father_phone, father_email, father_occupation,
                     mother_name, mother_phone, mother_email, mother_occupation,
                     admission_date, address, is_active) VALUES
('ADM001', 'Aarav', 'Sharma', '2015-03-15', 'Male', 'Class 3', 'A', '001', 
 'Rajesh Sharma', '9876543220', 'rajesh.sharma@email.com', 'Software Engineer',
 'Priya Sharma', '9876543221', 'priya.sharma@email.com', 'Teacher',
 '2023-04-01', '123 MG Road, Bangalore', true),

('ADM002', 'Ananya', 'Patel', '2016-07-22', 'Female', 'Class 2', 'B', '002',
 'Amit Patel', '9876543222', 'amit.patel@email.com', 'Business Owner',
 'Kavya Patel', '9876543223', 'kavya.patel@email.com', 'Doctor',
 '2023-04-01', '456 Brigade Road, Bangalore', true),

('ADM003', 'Arjun', 'Kumar', '2014-11-08', 'Male', 'Class 4', 'A', '003',
 'Suresh Kumar', '9876543224', 'suresh.kumar@email.com', 'Manager',
 'Lakshmi Kumar', '9876543225', 'lakshmi.kumar@email.com', 'Homemaker',
 '2023-04-01', '789 Koramangala, Bangalore', true),

('ADM004', 'Diya', 'Singh', '2017-01-12', 'Female', 'Class 1', 'A', '004',
 'Vikram Singh', '9876543226', 'vikram.singh@email.com', 'Consultant',
 'Meera Singh', '9876543227', 'meera.singh@email.com', 'Architect',
 '2023-04-01', '321 Indiranagar, Bangalore', true),

('ADM005', 'Karan', 'Gupta', '2015-09-30', 'Male', 'Class 3', 'B', '005',
 'Rohit Gupta', '9876543228', 'rohit.gupta@email.com', 'CA',
 'Neha Gupta', '9876543229', 'neha.gupta@email.com', 'Lawyer',
 '2023-04-01', '654 Whitefield, Bangalore', true),

('ADM006', 'Ishita', 'Reddy', '2016-05-18', 'Female', 'Class 2', 'A', '006',
 'Ravi Reddy', '9876543230', 'ravi.reddy@email.com', 'Engineer',
 'Sita Reddy', '9876543231', 'sita.reddy@email.com', 'Nurse',
 '2023-04-01', '987 Electronic City, Bangalore', true);

-- Insert Leave Requests
INSERT INTO leave_requests (student_id, leave_type, start_date, end_date, total_days, reason, description, status, emergency_contact) VALUES
(1, 'Sick Leave', '2024-01-15', '2024-01-17', 3, 'Fever and cold', 'Student has high fever and needs rest', 'Approved', '9876543220'),
(2, 'Family Function', '2024-01-20', '2024-01-22', 3, 'Wedding ceremony', 'Attending cousin wedding in hometown', 'Pending', '9876543222'),
(3, 'Medical Leave', '2024-01-25', '2024-01-26', 2, 'Doctor appointment', 'Regular health checkup', 'Approved', '9876543224'),
(4, 'Emergency Leave', '2024-01-28', '2024-01-28', 1, 'Family emergency', 'Urgent family matter', 'Pending', '9876543226'),
(5, 'Casual Leave', '2024-02-01', '2024-02-02', 2, 'Personal work', 'Family trip', 'Approved', '9876543228'),
(6, 'Sick Leave', '2024-02-05', '2024-02-07', 3, 'Stomach infection', 'Doctor advised rest', 'Pending', '9876543230');

-- Insert Expenses
INSERT INTO expenses (title, description, category, amount, tax_amount, total_amount, vendor_name, vendor_contact, 
                     payment_mode, expense_date, status, requested_by, invoice_number) VALUES
('Classroom Furniture', 'New desks and chairs for Class 1', 'Infrastructure', 25000.00, 4500.00, 29500.00, 
 'Modern Furniture Co.', '9876543240', 'Online Transfer', '2024-01-10', 'Paid', 1, 'INV-2024-001'),

('Electricity Bill', 'Monthly electricity charges', 'Utilities', 8500.00, 1530.00, 10030.00,
 'BESCOM', '1912', 'Online Transfer', '2024-01-15', 'Paid', 1, 'ELEC-JAN-2024'),

('Sports Equipment', 'Cricket bats, balls, and nets', 'Sports', 15000.00, 2700.00, 17700.00,
 'Sports World', '9876543241', 'UPI', '2024-01-20', 'Approved', 4, 'INV-2024-002'),

('Library Books', 'New story books for primary classes', 'Library', 12000.00, 2160.00, 14160.00,
 'Book Paradise', '9876543242', 'Cheque', '2024-01-25', 'Pending', 2, 'INV-2024-003'),

('Cleaning Supplies', 'Sanitizers, soaps, and cleaning materials', 'Cleaning', 3500.00, 630.00, 4130.00,
 'Clean & Fresh', '9876543243', 'Cash', '2024-01-30', 'Paid', 3, 'INV-2024-004'),

('Computer Lab Setup', 'New computers and software licenses', 'Equipment', 85000.00, 15300.00, 100300.00,
 'Tech Solutions', '9876543244', 'Online Transfer', '2024-02-01', 'Approved', 1, 'INV-2024-005');

-- Insert Fee Structures
INSERT INTO fee_structures (class_name, session_year, tuition_fee, admission_fee, development_fee, activity_fee, 
                           transport_fee, library_fee, lab_fee, exam_fee, other_fee, total_annual_fee) VALUES
('PG', '2024-25', 18000, 2000, 1500, 1000, 3000, 500, 0, 500, 500, 27000),
('Nursery', '2024-25', 20000, 2000, 1500, 1000, 3000, 500, 0, 500, 500, 29000),
('LKG', '2024-25', 22000, 2000, 1500, 1200, 3000, 600, 0, 600, 600, 31500),
('UKG', '2024-25', 24000, 2000, 1500, 1200, 3000, 600, 0, 600, 600, 33500),
('Class 1', '2024-25', 26000, 2500, 2000, 1500, 3500, 800, 500, 800, 800, 38400),
('Class 2', '2024-25', 28000, 2500, 2000, 1500, 3500, 800, 500, 800, 800, 40400),
('Class 3', '2024-25', 30000, 2500, 2000, 1500, 3500, 1000, 800, 1000, 1000, 43300),
('Class 4', '2024-25', 32000, 2500, 2000, 1500, 3500, 1000, 800, 1000, 1000, 45300);

-- Insert Fee Records
INSERT INTO fee_records (student_id, session_year, payment_type, total_amount, paid_amount, balance_amount, 
                        status, due_date, payment_method, transaction_id, payment_date) VALUES
(1, '2024-25', 'Quarterly', 10825, 10825, 0, 'Paid', '2024-04-30', 'Online', 'TXN123456789', '2024-04-25'),
(1, '2024-25', 'Quarterly', 10825, 0, 10825, 'Pending', '2024-07-31', NULL, NULL, NULL),
(2, '2024-25', 'Half Yearly', 20200, 20200, 0, 'Paid', '2024-09-30', 'UPI', 'UPI987654321', '2024-09-28'),
(3, '2024-25', 'Quarterly', 11325, 5000, 6325, 'Partial', '2024-04-30', 'Cash', NULL, '2024-04-20'),
(4, '2024-25', 'Monthly', 3200, 3200, 0, 'Paid', '2024-01-31', 'Online', 'TXN456789123', '2024-01-30'),
(5, '2024-25', 'Quarterly', 10825, 0, 10825, 'Overdue', '2024-01-31', NULL, NULL, NULL),
(6, '2024-25', 'Half Yearly', 20200, 15000, 5200, 'Partial', '2024-09-30', 'Cheque', 'CHQ001234', '2024-09-15');

-- Insert Fee Payments
INSERT INTO fee_payments (fee_record_id, amount, payment_method, payment_date, transaction_id, receipt_number) VALUES
(1, 10825, 'Online', '2024-04-25', 'TXN123456789', 'RCP-2024-001'),
(2, 20200, 'UPI', '2024-09-28', 'UPI987654321', 'RCP-2024-002'),
(3, 5000, 'Cash', '2024-04-20', NULL, 'RCP-2024-003'),
(4, 3200, 'Online', '2024-01-30', 'TXN456789123', 'RCP-2024-004'),
(7, 15000, 'Cheque', '2024-09-15', 'CHQ001234', 'RCP-2024-005');

-- Success message
SELECT 'Sample data inserted successfully!' as result;
SELECT 'Users: ' || COUNT(*) as users_count FROM users;
SELECT 'Students: ' || COUNT(*) as students_count FROM students;
SELECT 'Leave Requests: ' || COUNT(*) as leave_requests_count FROM leave_requests;
SELECT 'Expenses: ' || COUNT(*) as expenses_count FROM expenses;
SELECT 'Fee Records: ' || COUNT(*) as fee_records_count FROM fee_records;
