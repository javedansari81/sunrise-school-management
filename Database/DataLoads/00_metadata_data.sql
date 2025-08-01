-- =====================================================
-- Initial Data for Metadata Tables
-- =====================================================
-- This script populates all metadata tables with initial reference data
-- Primary keys are manually assigned (non-auto-increment)

-- Start transaction
BEGIN;

-- =====================================================
-- User Types Data
-- =====================================================
INSERT INTO user_types (id, name, description, is_active) VALUES
(1, 'ADMIN', 'System Administrator with full access', TRUE),
(2, 'TEACHER', 'Teaching staff member', TRUE),
(3, 'STUDENT', 'Student enrolled in the school', TRUE),
(4, 'STAFF', 'Non-teaching staff member', TRUE),
(5, 'PARENT', 'Parent or guardian of a student', TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- Session Years Data
-- =====================================================
INSERT INTO session_years (id, name, start_date, end_date, is_current, is_active) VALUES
(1, '2022-23', '2022-04-01', '2023-03-31', FALSE, TRUE),
(2, '2023-24', '2023-04-01', '2024-03-31', FALSE, TRUE),
(3, '2024-25', '2024-04-01', '2025-03-31', FALSE, TRUE),
(4, '2025-26', '2025-04-01', '2026-03-31', TRUE, TRUE),
(5, '2026-27', '2026-04-01', '2027-03-31', FALSE, TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    start_date = EXCLUDED.start_date,
    end_date = EXCLUDED.end_date,
    is_current = EXCLUDED.is_current,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- Genders Data
-- =====================================================
INSERT INTO genders (id, name, description, is_active) VALUES
(1, 'Male', 'Male gender', TRUE),
(2, 'Female', 'Female gender', TRUE),
(3, 'Other', 'Other gender identity', TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- Classes Data
-- =====================================================
INSERT INTO classes (id, name, display_name, sort_order, is_active) VALUES
(1, 'PG', 'Pre-Nursery', 1, TRUE),
(2, 'NURSERY', 'Nursery', 2, TRUE),
(3, 'LKG', 'Lower Kindergarten', 3, TRUE),
(4, 'UKG', 'Upper Kindergarten', 4, TRUE),
(5, 'CLASS_1', 'Class 1', 5, TRUE),
(6, 'CLASS_2', 'Class 2', 6, TRUE),
(7, 'CLASS_3', 'Class 3', 7, TRUE),
(8, 'CLASS_4', 'Class 4', 8, TRUE),
(9, 'CLASS_5', 'Class 5', 9, TRUE),
(10, 'CLASS_6', 'Class 6', 10, TRUE),
(11, 'CLASS_7', 'Class 7', 11, TRUE),
(12, 'CLASS_8', 'Class 8', 12, TRUE),
(13, 'CLASS_9', 'Class 9', 13, TRUE),
(14, 'CLASS_10', 'Class 10', 14, TRUE),
(15, 'CLASS_11', 'Class 11', 15, TRUE),
(16, 'CLASS_12', 'Class 12', 16, TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    display_name = EXCLUDED.display_name,
    sort_order = EXCLUDED.sort_order,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- Payment Types Data
-- =====================================================
INSERT INTO payment_types (id, name, description, is_active) VALUES
(1, 'Monthly', 'Monthly payment frequency', TRUE),
(2, 'Quarterly', 'Quarterly payment frequency (3 months)', TRUE),
(3, 'Half Yearly', 'Half yearly payment frequency (6 months)', TRUE),
(4, 'Yearly', 'Annual payment frequency', TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- Payment Statuses Data
-- =====================================================
INSERT INTO payment_statuses (id, name, description, color_code, is_active) VALUES
(1, 'Pending', 'Payment is pending', '#FFA500', TRUE),
(2, 'Partial', 'Partial payment received', '#FFFF00', TRUE),
(3, 'Paid', 'Payment completed', '#00FF00', TRUE),
(4, 'Overdue', 'Payment is overdue', '#FF0000', TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    color_code = EXCLUDED.color_code,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- Payment Methods Data
-- =====================================================
INSERT INTO payment_methods (id, name, description, requires_reference, is_active) VALUES
(1, 'Cash', 'Cash payment', FALSE, TRUE),
(2, 'Cheque', 'Cheque payment', TRUE, TRUE),
(3, 'Online', 'Online bank transfer', TRUE, TRUE),
(4, 'UPI', 'UPI payment', TRUE, TRUE),
(5, 'Card', 'Credit/Debit card payment', TRUE, TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    requires_reference = EXCLUDED.requires_reference,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- Leave Types Data
-- =====================================================
INSERT INTO leave_types (id, name, description, max_days_per_year, requires_medical_certificate, is_active) VALUES
(1, 'Sick Leave', 'Medical leave for illness', 15, TRUE, TRUE),
(2, 'Casual Leave', 'General casual leave', 12, FALSE, TRUE),
(3, 'Emergency Leave', 'Emergency situations', 5, FALSE, TRUE),
(4, 'Medical Leave', 'Extended medical leave', 30, TRUE, TRUE),
(5, 'Personal Leave', 'Personal reasons', 10, FALSE, TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    max_days_per_year = EXCLUDED.max_days_per_year,
    requires_medical_certificate = EXCLUDED.requires_medical_certificate,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- Leave Statuses Data
-- =====================================================
INSERT INTO leave_statuses (id, name, description, color_code, is_final, is_active) VALUES
(1, 'Pending', 'Leave application pending approval', '#FFA500', FALSE, TRUE),
(2, 'Approved', 'Leave application approved', '#00FF00', TRUE, TRUE),
(3, 'Rejected', 'Leave application rejected', '#FF0000', TRUE, TRUE),
(4, 'Cancelled', 'Leave application cancelled', '#808080', TRUE, TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    color_code = EXCLUDED.color_code,
    is_final = EXCLUDED.is_final,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- Expense Categories Data
-- =====================================================
INSERT INTO expense_categories (id, name, description, budget_limit, requires_approval, is_active) VALUES
(1, 'Infrastructure', 'Building and infrastructure expenses', 500000.00, TRUE, TRUE),
(2, 'Maintenance', 'Maintenance and repair expenses', 100000.00, TRUE, TRUE),
(3, 'Utilities', 'Electricity, water, internet expenses', 50000.00, FALSE, TRUE),
(4, 'Supplies', 'Office and classroom supplies', 25000.00, FALSE, TRUE),
(5, 'Equipment', 'Furniture and equipment purchases', 200000.00, TRUE, TRUE),
(6, 'Transportation', 'Vehicle and transportation expenses', 75000.00, TRUE, TRUE),
(7, 'Events', 'School events and activities', 30000.00, TRUE, TRUE),
(8, 'Marketing', 'Marketing and promotional expenses', 20000.00, TRUE, TRUE),
(9, 'Staff Welfare', 'Staff welfare and benefits', 40000.00, TRUE, TRUE),
(10, 'Academic', 'Academic materials and resources', 60000.00, FALSE, TRUE),
(11, 'Sports', 'Sports equipment and activities', 35000.00, TRUE, TRUE),
(12, 'Library', 'Library books and resources', 25000.00, FALSE, TRUE),
(13, 'Laboratory', 'Laboratory equipment and supplies', 80000.00, TRUE, TRUE),
(14, 'Security', 'Security services and equipment', 45000.00, TRUE, TRUE),
(15, 'Cleaning', 'Cleaning services and supplies', 30000.00, FALSE, TRUE),
(16, 'Other', 'Miscellaneous expenses', 15000.00, TRUE, TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    budget_limit = EXCLUDED.budget_limit,
    requires_approval = EXCLUDED.requires_approval,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- Expense Statuses Data
-- =====================================================
INSERT INTO expense_statuses (id, name, description, color_code, is_final, is_active) VALUES
(1, 'Pending', 'Expense request pending approval', '#FFA500', FALSE, TRUE),
(2, 'Approved', 'Expense request approved', '#00FF00', FALSE, TRUE),
(3, 'Rejected', 'Expense request rejected', '#FF0000', TRUE, TRUE),
(4, 'Paid', 'Expense payment completed', '#0000FF', TRUE, TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    color_code = EXCLUDED.color_code,
    is_final = EXCLUDED.is_final,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- Employment Statuses Data
-- =====================================================
INSERT INTO employment_statuses (id, name, description, is_active) VALUES
(1, 'Full Time', 'Full-time permanent employee', TRUE),
(2, 'Part Time', 'Part-time employee', TRUE),
(3, 'Contract', 'Contract-based employee', TRUE),
(4, 'Substitute', 'Substitute teacher', TRUE),
(5, 'Probation', 'Employee on probation period', TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- Qualifications Data
-- =====================================================
INSERT INTO qualifications (id, name, description, level_order, is_active) VALUES
(1, 'Certificate', 'Certificate course', 1, TRUE),
(2, 'Diploma', 'Diploma qualification', 2, TRUE),
(3, 'Bachelor''s Degree', 'Bachelor''s degree', 3, TRUE),
(4, 'Master''s Degree', 'Master''s degree', 4, TRUE),
(5, 'PhD', 'Doctorate degree', 5, TRUE),
(6, 'Other', 'Other qualifications', 6, TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    level_order = EXCLUDED.level_order,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- Commit transaction
COMMIT;

-- =====================================================
-- Verification Queries
-- =====================================================
SELECT 'Metadata tables populated successfully!' as result;

-- Show counts for verification
SELECT 'user_types' as table_name, COUNT(*) as record_count FROM user_types
UNION ALL
SELECT 'session_years', COUNT(*) FROM session_years
UNION ALL
SELECT 'genders', COUNT(*) FROM genders
UNION ALL
SELECT 'classes', COUNT(*) FROM classes
UNION ALL
SELECT 'payment_types', COUNT(*) FROM payment_types
UNION ALL
SELECT 'payment_statuses', COUNT(*) FROM payment_statuses
UNION ALL
SELECT 'payment_methods', COUNT(*) FROM payment_methods
UNION ALL
SELECT 'leave_types', COUNT(*) FROM leave_types
UNION ALL
SELECT 'leave_statuses', COUNT(*) FROM leave_statuses
UNION ALL
SELECT 'expense_categories', COUNT(*) FROM expense_categories
UNION ALL
SELECT 'expense_statuses', COUNT(*) FROM expense_statuses
UNION ALL
SELECT 'employment_statuses', COUNT(*) FROM employment_statuses
UNION ALL
SELECT 'qualifications', COUNT(*) FROM qualifications
ORDER BY table_name;
