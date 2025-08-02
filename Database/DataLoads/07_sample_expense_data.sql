-- =====================================================
-- Sample Expense Data for Testing
-- =====================================================
-- This file contains comprehensive test data for the expense management system
-- including various categories, statuses, vendors, and approval workflows

-- =====================================================
-- Create Sample Users for Expense Management (if not exists)
-- =====================================================

-- Insert sample admin user for approvals (if not exists)
INSERT INTO users (id, username, email, first_name, last_name, role_id, is_active, created_at)
VALUES (1, 'admin', 'admin@school.com', 'Admin', 'User', 1, true, NOW())
ON CONFLICT (id) DO NOTHING;

-- Insert sample teacher user (if not exists)
INSERT INTO users (id, username, email, first_name, last_name, role_id, is_active, created_at)
VALUES (2, 'teacher1', 'teacher1@school.com', 'John', 'Teacher', 2, true, NOW())
ON CONFLICT (id) DO NOTHING;

-- Insert sample accountant user (if not exists)
INSERT INTO users (id, username, email, first_name, last_name, role_id, is_active, created_at)
VALUES (4, 'accountant', 'accountant@school.com', 'Jane', 'Accountant', 1, true, NOW())
ON CONFLICT (id) DO NOTHING;

-- =====================================================
-- Sample Vendors
-- =====================================================

INSERT INTO vendors (id, vendor_name, vendor_code, contact_person, phone, email, address_line1, city, state, gst_number, is_active, created_at) VALUES
(1, 'ABC Stationery Supplies', 'VENDOR001', 'Rajesh Kumar', '9876543210', 'rajesh@abcstationery.com', '123 Market Street', 'Mumbai', 'Maharashtra', '27ABCDE1234F1Z5', true, NOW()),
(2, 'XYZ Maintenance Services', 'VENDOR002', 'Priya Sharma', '9876543211', 'priya@xyzmaintenance.com', '456 Service Road', 'Delhi', 'Delhi', '07XYZAB5678G2H9', true, NOW()),
(3, 'PowerTech Solutions', 'VENDOR003', 'Amit Singh', '9876543212', 'amit@powertech.com', '789 Tech Park', 'Bangalore', 'Karnataka', '29POWER1234K3L6', true, NOW()),
(4, 'Green Transport Co.', 'VENDOR004', 'Sunita Patel', '9876543213', 'sunita@greentransport.com', '321 Transport Hub', 'Pune', 'Maharashtra', '27TRANS5678M4N7', true, NOW()),
(5, 'Fresh Foods Catering', 'VENDOR005', 'Ravi Gupta', '9876543214', 'ravi@freshfoods.com', '654 Food Street', 'Chennai', 'Tamil Nadu', '33FRESH9012P5Q8', true, NOW())
ON CONFLICT (id) DO NOTHING;

-- =====================================================
-- Sample Expense Records
-- =====================================================

-- Expense 1: Approved Infrastructure Expense
INSERT INTO expenses (
    id, expense_date, expense_category_id, subcategory, description,
    amount, tax_amount, total_amount, currency,
    vendor_name, vendor_contact, vendor_email, vendor_gst_number,
    payment_method_id, payment_status_id, payment_reference,
    expense_status_id, requested_by, approved_by, approved_at, approval_comments,
    session_year_id, is_budgeted, priority, invoice_url, created_at
) VALUES (
    1, '2024-01-15', 1, 'Classroom Renovation', 'Renovation of 3 classrooms including painting, flooring, and electrical work',
    85000.00, 15300.00, 100300.00, 'INR',
    'ABC Construction Ltd', '9876543210', 'contact@abcconstruction.com', '27ABCDE1234F1Z5',
    3, 2, 'TXN20240115001',
    2, 2, 1, NOW() - INTERVAL '10 days', 'Approved for urgent classroom renovation. Budget allocated.',
    4, true, 'High', 'https://example.com/invoices/INV001.pdf', NOW() - INTERVAL '15 days'
) ON CONFLICT (id) DO NOTHING;

-- Expense 2: Pending Maintenance Expense
INSERT INTO expenses (
    id, expense_date, expense_category_id, subcategory, description,
    amount, tax_amount, total_amount, currency,
    vendor_name, vendor_contact, vendor_email,
    payment_method_id, payment_status_id,
    expense_status_id, requested_by, session_year_id, is_budgeted, priority, created_at
) VALUES (
    2, '2024-01-20', 2, 'HVAC Maintenance', 'Annual maintenance of air conditioning systems in all buildings',
    25000.00, 4500.00, 29500.00, 'INR',
    'XYZ Maintenance Services', '9876543211', 'priya@xyzmaintenance.com',
    2, 1,
    1, 2, 4, true, 'Medium', NOW() - INTERVAL '5 days'
) ON CONFLICT (id) DO NOTHING;

-- Expense 3: Approved Utilities Expense
INSERT INTO expenses (
    id, expense_date, expense_category_id, subcategory, description,
    amount, tax_amount, total_amount, currency,
    vendor_name, vendor_contact, payment_method_id, payment_status_id, payment_date, payment_reference,
    expense_status_id, requested_by, approved_by, approved_at, approval_comments,
    session_year_id, is_budgeted, priority, is_recurring, recurring_frequency, next_due_date, created_at
) VALUES (
    3, '2024-01-10', 3, 'Electricity Bill', 'Monthly electricity bill for all school buildings',
    18500.00, 3330.00, 21830.00, 'INR',
    'State Electricity Board', '1912', 1, 3, '2024-01-12', 'ELEC202401001',
    2, 4, 1, NOW() - INTERVAL '12 days', 'Regular monthly utility expense. Approved.',
    4, true, 'Medium', true, 'Monthly', '2024-02-10', NOW() - INTERVAL '18 days'
) ON CONFLICT (id) DO NOTHING;

-- Expense 4: Rejected Supplies Expense
INSERT INTO expenses (
    id, expense_date, expense_category_id, subcategory, description,
    amount, tax_amount, total_amount, currency,
    vendor_name, vendor_contact, vendor_email,
    payment_method_id, payment_status_id,
    expense_status_id, requested_by, approved_by, approved_at, approval_comments,
    session_year_id, priority, created_at
) VALUES (
    4, '2024-01-18', 4, 'Office Supplies', 'Premium office furniture and decorative items for admin office',
    45000.00, 8100.00, 53100.00, 'INR',
    'Luxury Office Solutions', '9876543215', 'sales@luxuryoffice.com',
    2, 1,
    3, 2, 1, NOW() - INTERVAL '8 days', 'Rejected due to budget constraints. Please submit essential items only.',
    4, 'Low', NOW() - INTERVAL '12 days'
) ON CONFLICT (id) DO NOTHING;

-- Expense 5: Approved Equipment Expense
INSERT INTO expenses (
    id, expense_date, expense_category_id, subcategory, description,
    amount, tax_amount, total_amount, currency,
    vendor_name, vendor_contact, vendor_email, vendor_gst_number,
    payment_method_id, payment_status_id, payment_date, payment_reference,
    expense_status_id, requested_by, approved_by, approved_at, approval_comments,
    budget_category, session_year_id, is_budgeted, priority, invoice_url, receipt_url, created_at
) VALUES (
    5, '2024-01-22', 5, 'Computer Lab', 'Purchase of 20 desktop computers for computer lab upgrade',
    120000.00, 21600.00, 141600.00, 'INR',
    'TechWorld Computers', '9876543216', 'sales@techworld.com', '29TECH1234567890',
    3, 3, '2024-01-25', 'BANK20240125001',
    2, 2, 1, NOW() - INTERVAL '6 days', 'Approved for computer lab modernization. Essential for digital education.',
    'IT Infrastructure', 4, true, 'High', 'https://example.com/invoices/INV005.pdf', 'https://example.com/receipts/REC005.pdf', NOW() - INTERVAL '8 days'
) ON CONFLICT (id) DO NOTHING;

-- Expense 6: Emergency Transportation Expense
INSERT INTO expenses (
    id, expense_date, expense_category_id, subcategory, description,
    amount, tax_amount, total_amount, currency,
    vendor_name, vendor_contact,
    payment_method_id, payment_status_id,
    expense_status_id, requested_by, session_year_id, priority, is_emergency, created_at
) VALUES (
    6, '2024-01-25', 6, 'Emergency Transport', 'Emergency transportation for student medical emergency',
    2500.00, 0.00, 2500.00, 'INR',
    'Quick Cab Services', '9876543217',
    1, 1,
    1, 2, 4, 'Urgent', true, NOW() - INTERVAL '2 days'
) ON CONFLICT (id) DO NOTHING;

-- Expense 7: Approved Events Expense
INSERT INTO expenses (
    id, expense_date, expense_category_id, subcategory, description,
    amount, tax_amount, total_amount, currency,
    vendor_name, vendor_contact, vendor_email,
    payment_method_id, payment_status_id, payment_date, payment_reference,
    expense_status_id, requested_by, approved_by, approved_at, approval_comments,
    session_year_id, is_budgeted, priority, created_at
) VALUES (
    7, '2024-01-12', 7, 'Annual Day', 'Decorations, sound system, and catering for annual day celebration',
    35000.00, 6300.00, 41300.00, 'INR',
    'Event Masters', '9876543218', 'contact@eventmasters.com',
    2, 3, '2024-01-14', 'CHQ001234',
    2, 4, 1, NOW() - INTERVAL '14 days', 'Approved for annual day celebration. Well within budget.',
    4, true, 'Medium', NOW() - INTERVAL '16 days'
) ON CONFLICT (id) DO NOTHING;

-- Expense 8: Pending Academic Expense
INSERT INTO expenses (
    id, expense_date, expense_category_id, subcategory, description,
    amount, tax_amount, total_amount, currency,
    vendor_name, vendor_contact, vendor_email,
    payment_method_id, payment_status_id,
    expense_status_id, requested_by, session_year_id, is_budgeted, priority, created_at
) VALUES (
    8, '2024-01-28', 10, 'Textbooks', 'Purchase of updated textbooks for grades 9-12',
    75000.00, 13500.00, 88500.00, 'INR',
    'Educational Publishers Ltd', '9876543219', 'orders@edupublishers.com',
    3, 1,
    1, 2, 4, true, 'High', NOW() - INTERVAL '1 day'
) ON CONFLICT (id) DO NOTHING;

-- =====================================================
-- Update sequence values
-- =====================================================

-- Update vendors sequence
SELECT setval('vendors_id_seq', (SELECT MAX(id) FROM vendors));

-- Update expenses sequence
SELECT setval('expenses_id_seq', (SELECT MAX(id) FROM expenses));

-- =====================================================
-- Comments
-- =====================================================

COMMENT ON TABLE vendors IS 'Sample vendor data for expense management testing';
COMMENT ON TABLE expenses IS 'Sample expense data with various categories, statuses, and approval workflows';
