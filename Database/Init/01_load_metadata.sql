-- =====================================================
-- Load Metadata for Sunrise School Management System
-- =====================================================
-- This script loads all essential metadata into reference tables
-- Run this AFTER creating the database structure
--
-- USAGE:
-- psql -U sunrise_user -d sunrise_school_db -f Database/Init/01_load_metadata.sql

-- Start transaction
BEGIN;

-- =====================================================
-- User Types Data
-- =====================================================
INSERT INTO user_types (id, name, description, is_active) VALUES
(1, 'ADMIN', 'System Administrator', TRUE),
(2, 'TEACHER', 'Teaching Staff', TRUE),
(3, 'STUDENT', 'Enrolled Student', TRUE),
(4, 'STAFF', 'Non-Teaching Staff', TRUE),
(5, 'PARENT', 'Parent/Guardian', TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- Session Years Data (Indian Academic Calendar: April to March)
-- =====================================================
INSERT INTO session_years (id, name, description, start_date, end_date, is_current, is_active) VALUES
(1, '2022-23', 'Academic Year 2022-23', '2022-04-01', '2023-03-31', FALSE, TRUE),
(2, '2023-24', 'Academic Year 2023-24', '2023-04-01', '2024-03-31', FALSE, TRUE),
(3, '2024-25', 'Academic Year 2024-25', '2024-04-01', '2025-03-31', TRUE, TRUE),
(4, '2025-26', 'Academic Year 2025-26', '2025-04-01', '2026-03-31', FALSE, TRUE),
(5, '2026-27', 'Academic Year 2026-27', '2026-04-01', '2027-03-31', FALSE, TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    start_date = EXCLUDED.start_date,
    end_date = EXCLUDED.end_date,
    is_current = EXCLUDED.is_current,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- Genders Data
-- =====================================================
INSERT INTO genders (id, name, description, is_active) VALUES
(1, 'MALE', 'Male', TRUE),
(2, 'FEMALE', 'Female', TRUE),
(3, 'OTHER', 'Other', TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- Classes Data (Indian Education System: Pre-Nursery to Class 12)
-- =====================================================
INSERT INTO classes (id, name, description, sort_order, is_active) VALUES
(2, 'PRE_NURSERY', 'PG', 2, TRUE),
(3, 'LKG', 'LKG', 3, TRUE),
(4, 'UKG', 'UKG', 4, TRUE),
(5, 'CLASS_1', 'Class 1', 5, TRUE),
(6, 'CLASS_2', 'Class 2', 6, TRUE),
(7, 'CLASS_3', 'Class 3', 7, TRUE),
(8, 'CLASS_4', 'Class 4', 8, TRUE),
(9, 'CLASS_5', 'Class 5', 9, TRUE),
(10, 'CLASS_6', 'Class 6', 10, TRUE),
(11, 'CLASS_7', 'Class 7', 11, TRUE),
(12, 'CLASS_8', 'Class 8', 12, TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- Payment Types Data
-- =====================================================
INSERT INTO payment_types (id, name, description, is_active) VALUES
(1, 'MONTHLY', 'Monthly Payment', TRUE),
(2, 'QUARTERLY', 'Quarterly Payment', TRUE),
(3, 'ANNUAL', 'Annual Payment', TRUE),
(4, 'ONE_TIME', 'One-Time Payment', TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- Payment Statuses Data
-- =====================================================
INSERT INTO payment_statuses (id, name, description, color_code, is_active) VALUES
(1, 'PENDING', 'Pending Payment', '#FFA500', TRUE),
(2, 'PAID', 'Payment Completed', '#28A745', TRUE),
(3, 'PARTIAL', 'Partial Payment', '#FFC107', TRUE),
(4, 'OVERDUE', 'Overdue Payment', '#DC3545', TRUE),
(5, 'CANCELLED', 'Cancelled Payment', '#6C757D', TRUE)
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
(1, 'CASH', 'Cash Payment', FALSE, TRUE),
(2, 'UPI', 'UPI Payment', TRUE, TRUE),
(3, 'BANK_TRANSFER', 'Bank Transfer', TRUE, TRUE),
(4, 'CHEQUE', 'Cheque Payment', TRUE, TRUE),
(5, 'CARD', 'Card Payment', TRUE, TRUE),
(6, 'ONLINE', 'Online Gateway', TRUE, TRUE)
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
(1, 'SICK', 'Sick Leave', 12, TRUE, TRUE),
(2, 'CASUAL', 'Casual Leave', 15, FALSE, TRUE),
(3, 'EMERGENCY', 'Emergency Leave', 5, FALSE, TRUE),
(4, 'MATERNITY', 'Maternity Leave', 180, TRUE, TRUE),
(5, 'PATERNITY', 'Paternity Leave', 15, FALSE, TRUE)
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
(1, 'PENDING', 'Pending Approval', '#FFA500', FALSE, TRUE),
(2, 'APPROVED', 'Approved', '#28A745', TRUE, TRUE),
(3, 'REJECTED', 'Rejected', '#DC3545', TRUE, TRUE),
(4, 'CANCELLED', 'Cancelled', '#6C757D', TRUE, TRUE)
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
(1, 'STATIONERY', 'Office Stationery', 50000.00, TRUE, TRUE),
(2, 'MAINTENANCE', 'Building Maintenance', 100000.00, TRUE, TRUE),
(3, 'UTILITIES', 'Utility Bills', 75000.00, TRUE, TRUE),
(4, 'TRANSPORT', 'Transportation', 30000.00, TRUE, TRUE),
(5, 'EVENTS', 'School Events', 25000.00, TRUE, TRUE),
(6, 'EQUIPMENT', 'Educational Equipment', 150000.00, TRUE, TRUE)
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
(1, 'PENDING', 'Pending Approval', '#FFA500', FALSE, TRUE),
(2, 'APPROVED', 'Approved', '#28A745', FALSE, TRUE),
(3, 'REJECTED', 'Rejected', '#DC3545', TRUE, TRUE),
(4, 'PAID', 'Paid', '#007BFF', TRUE, TRUE)
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
(1, 'FULL_TIME', 'Full-Time Employee', TRUE),
(2, 'PART_TIME', 'Part-Time Employee', TRUE),
(3, 'CONTRACT', 'Contract Employee', TRUE),
(4, 'PROBATION', 'On Probation', TRUE),
(5, 'RESIGNED', 'Resigned', TRUE),
(6, 'TERMINATED', 'Terminated', TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- Qualifications Data
-- =====================================================
INSERT INTO qualifications (id, name, description, level_order, is_active) VALUES
(1, 'HIGH_SCHOOL', 'High School (10th)', 1, TRUE),
(2, 'INTERMEDIATE', 'Intermediate (12th)', 2, TRUE),
(3, 'DIPLOMA', 'Diploma', 3, TRUE),
(4, 'BACHELORS', 'Bachelor''s Degree', 4, TRUE),
(5, 'MASTERS', 'Master''s Degree', 5, TRUE),
(6, 'PHD', 'Doctorate', 6, TRUE),
(7, 'B_ED', 'Bachelor of Education', 4, TRUE),
(8, 'M_ED', 'Master of Education', 5, TRUE),
(9, 'D_ED', 'Diploma in Education', 3, TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    level_order = EXCLUDED.level_order,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- Departments Data
-- =====================================================
INSERT INTO departments (id, name, description, is_active) VALUES
(1, 'SCIENCE', 'Science Department', TRUE),
(2, 'MATHEMATICS', 'Mathematics Department', TRUE),
(3, 'ENGLISH', 'English Department', TRUE),
(4, 'HINDI', 'Hindi Department', TRUE),
(5, 'SOCIAL_STUDIES', 'Social Studies Department', TRUE),
(6, 'COMPUTER_SCIENCE', 'Computer Science Department', TRUE),
(7, 'PHYSICAL_EDUCATION', 'Physical Education Department', TRUE),
(8, 'ARTS', 'Arts Department', TRUE),
(9, 'MUSIC', 'Music Department', TRUE),
(10, 'ADMINISTRATION', 'Administration Department', TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- Positions Data
-- =====================================================
INSERT INTO positions (id, name, description, is_active) VALUES
(1, 'PRINCIPAL', 'Principal', TRUE),
(2, 'VICE_PRINCIPAL', 'Vice Principal', TRUE),
(3, 'HEAD_TEACHER', 'Head Teacher', TRUE),
(4, 'SENIOR_TEACHER', 'Senior Teacher', TRUE),
(5, 'TEACHER', 'Teacher', TRUE),
(6, 'ASSISTANT_TEACHER', 'Assistant Teacher', TRUE),
(7, 'PRT', 'Primary Teacher (PRT)', TRUE),
(8, 'TGT', 'Trained Graduate Teacher (TGT)', TRUE),
(9, 'PGT', 'Post Graduate Teacher (PGT)', TRUE),
(10, 'LIBRARIAN', 'Librarian', TRUE),
(11, 'LAB_ASSISTANT', 'Lab Assistant', TRUE),
(12, 'COUNSELOR', 'Counselor', TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- Inventory Item Types Data
-- =====================================================
INSERT INTO inventory_item_types (id, name, description, category, is_active) VALUES
(1, 'CASUAL_DRESS_1', 'Casual Dress 1 (Pant-Shirt)', 'UNIFORM', TRUE),
(2, 'CASUAL_DRESS_2', 'Casual Dress 2 (Pant-T-Shirt)', 'UNIFORM', TRUE),
(3, 'WINTER_DRESS', 'Winter Dress', 'UNIFORM', TRUE),
(4, 'SHIRT', 'Shirt (Individual)', 'UNIFORM', TRUE),
(5, 'PANT', 'Pant (Individual)', 'UNIFORM', TRUE),
(6, 'T_SHIRT', 'T-Shirt (Individual)', 'UNIFORM', TRUE),
(7, 'TIE', 'Tie', 'ACCESSORY', TRUE),
(8, 'BELT', 'Belt', 'ACCESSORY', TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    category = EXCLUDED.category,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- Inventory Size Types Data
-- =====================================================
INSERT INTO inventory_size_types (id, name, description, sort_order, is_active) VALUES
(1, 'XS', 'Extra Small', 1, TRUE),
(2, 'S', 'Small', 2, TRUE),
(3, 'M', 'Medium', 3, TRUE),
(4, 'L', 'Large', 4, TRUE),
(5, 'XL', 'Extra Large', 5, TRUE),
(6, 'XXL', 'Double Extra Large', 6, TRUE),
(7, 'FREE_SIZE', 'Free Size', 7, TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- Commit transaction
COMMIT;

-- =====================================================
-- Success Message
-- =====================================================
\echo '=========================================='
\echo 'METADATA LOADED SUCCESSFULLY!'
\echo '=========================================='
\echo 'Loaded data:'
\echo '- 5 User types'
\echo '- 5 Session years (2022-23 to 2026-27)'
\echo '- 3 Genders'
\echo '- 16 Classes (Pre-Nursery to Class 12)'
\echo '- 4 Payment types'
\echo '- 5 Payment statuses (with color codes)'
\echo '- 6 Payment methods (with reference requirements)'
\echo '- 5 Leave types'
\echo '- 4 Leave statuses (with color codes and finality flags)'
\echo '- 6 Expense categories'
\echo '- 4 Expense statuses (with color codes and finality flags)'
\echo '- 6 Employment statuses'
\echo '- 9 Qualifications (with level ordering)'
\echo '- 10 Departments'
\echo '- 12 Positions'
\echo '- 8 Inventory item types'
\echo '- 7 Inventory size types'
\echo ''
\echo 'Total: 115 metadata records loaded'
\echo '=========================================='
