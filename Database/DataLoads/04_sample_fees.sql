-- =====================================================
-- Sample Fee Data (Structures, Records, Payments)
-- =====================================================

-- Insert Fee Structures for 2024-25 session
INSERT INTO fee_structures (
    class_name, session_year, tuition_fee, admission_fee, development_fee, activity_fee,
    transport_fee, library_fee, lab_fee, exam_fee, other_fee, total_annual_fee, created_at
) VALUES 
('PG', '2024-25', 18000, 2000, 1500, 1000, 3000, 500, 0, 500, 500, 27000, NOW()),
('LKG', '2024-25', 22000, 2000, 1500, 1200, 3000, 600, 0, 600, 600, 31500, NOW()),
('UKG', '2024-25', 24000, 2000, 1500, 1200, 3000, 600, 0, 600, 600, 33500, NOW()),
('Class 1', '2024-25', 26000, 2500, 2000, 1500, 3500, 800, 500, 800, 800, 38400, NOW()),
('Class 2', '2024-25', 28000, 2500, 2000, 1500, 3500, 800, 500, 800, 800, 40400, NOW()),
('Class 3', '2024-25', 30000, 2500, 2000, 1500, 3500, 1000, 800, 1000, 1000, 43300, NOW()),
('Class 4', '2024-25', 32000, 2500, 2000, 1500, 3500, 1000, 800, 1000, 1000, 45300, NOW()),
('Class 5', '2024-25', 34000, 2500, 2000, 1500, 3500, 1000, 1000, 1000, 1000, 47500, NOW()),
('Class 6', '2024-25', 36000, 3000, 2500, 2000, 4000, 1200, 1200, 1200, 1200, 52300, NOW()),
('Class 7', '2024-25', 38000, 3000, 2500, 2000, 4000, 1200, 1200, 1200, 1200, 54300, NOW()),
('Class 8', '2024-25', 40000, 3000, 2500, 2000, 4000, 1200, 1200, 1200, 1200, 56300, NOW())
ON CONFLICT (class_name, session_year) DO NOTHING;

-- Insert Fee Records for students
INSERT INTO fee_records (
    student_id, session_year, payment_type, total_amount, paid_amount, balance_amount,
    status, due_date, payment_method, transaction_id, payment_date, created_at
) VALUES 
-- Student 1: Aarav Sharma (Class 5) - Quarterly payments
(1, '2024-25', 'Quarterly', 11000.0, 0.0, 11000.0, 'Pending', '2024-07-15', NULL, NULL, NULL, NOW()),

-- Student 2: Ananya Patel (Class 4) - Quarterly payments  
(2, '2024-25', 'Quarterly', 10500.0, 5000.0, 5500.0, 'Pending', '2024-07-15', NULL, NULL, NULL, NOW()),

-- Student 3: Arjun Kumar (Class 6) - Half Yearly payments
(3, '2024-25', 'Half Yearly', 23150.0, 0.0, 23150.0, 'Pending', '2024-09-15', NULL, NULL, NULL, NOW()),

-- Student 4: Diya Singh (Class 3) - Monthly payments
(4, '2024-25', 'Monthly', 3333.0, 3333.0, 0.0, 'Paid', '2024-06-15', NULL, NULL, NULL, NOW()),

-- Student 5: Ishaan Gupta (Class 5) - Quarterly payments
(5, '2024-25', 'Quarterly', 11000.0, 3000.0, 8000.0, 'Pending', '2024-07-15', NULL, NULL, NULL, NOW()),

-- Student 6: Kavya Reddy (Class 4) - Monthly payments
(6, '2024-25', 'Monthly', 3500.0, 0.0, 3500.0, 'Pending', '2024-06-15', NULL, NULL, NULL, NOW()),

-- Student 7: Rohan Joshi (Class 7) - Half Yearly payments
(7, '2024-25', 'Half Yearly', 24150.0, 12150.0, 12000.0, 'Pending', '2024-09-15', NULL, NULL, NULL, NOW()),

-- Student 8: Siya Agarwal (Class 2) - Quarterly payments
(8, '2024-25', 'Quarterly', 10000.0, 0.0, 10000.0, 'Pending', '2024-07-15', NULL, NULL, NULL, NOW()),

-- Student 9: Vihaan Malhotra (Class 6) - Monthly payments
(9, '2024-25', 'Monthly', 3858.0, 2000.0, 1858.0, 'Pending', '2024-06-15', NULL, NULL, NULL, NOW()),

-- Student 10: Zara Khan (Class 3) - Quarterly payments
(10, '2024-25', 'Quarterly', 10000.0, 5000.0, 5000.0, 'Pending', '2024-07-15', NULL, NULL, NULL, NOW()),

-- Student 11: Aditya Verma (LKG) - Monthly payments
(11, '2024-25', 'Monthly', 2583.0, 0.0, 2583.0, 'Pending', '2024-06-15', NULL, NULL, NULL, NOW()),

-- Student 12: Priya Nair (UKG) - Quarterly payments
(12, '2024-25', 'Quarterly', 8250.0, 4250.0, 4000.0, 'Pending', '2024-07-15', NULL, NULL, NULL, NOW()),

-- Student 13: Karan Chopra (Class 8) - Half Yearly payments
(13, '2024-25', 'Half Yearly', 25150.0, 0.0, 25150.0, 'Pending', '2024-09-15', NULL, NULL, NULL, NOW()),

-- Student 14: Sneha Bansal (PG) - Monthly payments
(14, '2024-25', 'Monthly', 2417.0, 1417.0, 1000.0, 'Pending', '2024-06-15', NULL, NULL, NULL, NOW()),

-- Student 15: Aryan Saxena (Class 7) - Quarterly payments
(15, '2024-25', 'Quarterly', 12075.0, 6075.0, 6000.0, 'Pending', '2024-07-15', NULL, NULL, NULL, NOW())
ON CONFLICT DO NOTHING;

-- Insert Fee Payments for some records
INSERT INTO fee_payments (
    fee_record_id, amount, payment_method, payment_date, transaction_id, receipt_number, collected_by, created_at
) VALUES 
-- Payment for Student 2 (Ananya Patel)
(2, 5000.0, 'Online', '2024-06-10', 'TXN123456789', 'RCP-2024-001', 1, NOW()),

-- Payment for Student 4 (Diya Singh) - Full payment
(4, 3333.0, 'UPI', '2024-06-12', 'UPI987654321', 'RCP-2024-002', 1, NOW()),

-- Payment for Student 5 (Ishaan Gupta) - Partial payment
(5, 3000.0, 'Cash', '2024-06-15', NULL, 'RCP-2024-003', 1, NOW()),

-- Payment for Student 7 (Rohan Joshi) - Partial payment
(7, 12150.0, 'Cheque', '2024-08-20', 'CHQ001234', 'RCP-2024-004', 1, NOW()),

-- Payment for Student 9 (Vihaan Malhotra) - Partial payment
(9, 2000.0, 'Online', '2024-06-18', 'TXN456789123', 'RCP-2024-005', 1, NOW()),

-- Payment for Student 10 (Zara Khan) - Partial payment
(10, 5000.0, 'UPI', '2024-07-01', 'UPI123789456', 'RCP-2024-006', 1, NOW()),

-- Payment for Student 12 (Priya Nair) - Partial payment
(12, 4250.0, 'Online', '2024-07-05', 'TXN789123456', 'RCP-2024-007', 1, NOW()),

-- Payment for Student 14 (Sneha Bansal) - Partial payment
(14, 1417.0, 'Cash', '2024-06-25', NULL, 'RCP-2024-008', 1, NOW()),

-- Payment for Student 15 (Aryan Saxena) - Partial payment
(15, 6075.0, 'Cheque', '2024-07-10', 'CHQ005678', 'RCP-2024-009', 1, NOW())
ON CONFLICT DO NOTHING;

-- Insert Fee Discounts for some students
INSERT INTO fee_discounts (
    student_id, session_year, discount_type, discount_name, discount_percentage, discount_amount,
    applicable_fees, approved_by, approved_at, approval_remarks, valid_from, valid_to, is_active, created_at
) VALUES 
-- Sibling discount for Student 5 (Ishaan Gupta)
(5, '2024-25', 'Sibling Discount', '10% Sibling Discount', 10.0, NULL, 'tuition_fee', 1, NOW(), 'Second child discount', '2024-04-01', '2025-03-31', true, NOW()),

-- Merit scholarship for Student 13 (Karan Chopra)
(13, '2024-25', 'Merit Scholarship', 'Academic Excellence Award', 15.0, NULL, 'tuition_fee,development_fee', 1, NOW(), 'Top performer in previous year', '2024-04-01', '2025-03-31', true, NOW()),

-- Financial aid for Student 11 (Aditya Verma)
(11, '2024-25', 'Financial Aid', 'Need-based Assistance', NULL, 2000.0, 'admission_fee,development_fee', 1, NOW(), 'Family financial hardship', '2024-04-01', '2025-03-31', true, NOW())
ON CONFLICT DO NOTHING;

-- Display fee summary
SELECT 
    'Fee Structures' as data_type,
    COUNT(*) as count
FROM fee_structures
WHERE session_year = '2024-25'

UNION ALL

SELECT 
    'Fee Records' as data_type,
    COUNT(*) as count
FROM fee_records
WHERE session_year = '2024-25'

UNION ALL

SELECT 
    'Fee Payments' as data_type,
    COUNT(*) as count
FROM fee_payments

UNION ALL

SELECT 
    'Fee Discounts' as data_type,
    COUNT(*) as count
FROM fee_discounts
WHERE session_year = '2024-25';

-- Display fee collection summary
SELECT 
    SUM(total_amount) as total_fees,
    SUM(paid_amount) as collected_amount,
    SUM(balance_amount) as pending_amount,
    ROUND((SUM(paid_amount) * 100.0 / SUM(total_amount)), 2) as collection_percentage
FROM fee_records
WHERE session_year = '2024-25';
