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
(1, 'ADMIN', 'System Administrator with full access to all features', TRUE),
(2, 'TEACHER', 'Teaching staff member with access to academic features', TRUE),
(3, 'STUDENT', 'Student enrolled in the school with limited access', TRUE),
(4, 'STAFF', 'Non-teaching staff member with administrative access', TRUE),
(5, 'PARENT', 'Parent or guardian of a student with view-only access', TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- Session Years Data (Indian Academic Calendar: April to March)
-- =====================================================
INSERT INTO session_years (id, name, description, start_date, end_date, is_current, is_active) VALUES
(1, '2022-23', 'Academic session from April 2022 to March 2023', '2022-04-01', '2023-03-31', FALSE, TRUE),
(2, '2023-24', 'Academic session from April 2023 to March 2024', '2023-04-01', '2024-03-31', FALSE, TRUE),
(3, '2024-25', 'Academic session from April 2024 to March 2025', '2024-04-01', '2025-03-31', TRUE, TRUE),
(4, '2025-26', 'Academic session from April 2025 to March 2026', '2025-04-01', '2026-03-31', FALSE, TRUE),
(5, '2026-27', 'Academic session from April 2026 to March 2027', '2026-04-01', '2027-03-31', FALSE, TRUE)
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
(1, 'PRE_NURSERY', 'Pre-Nursery', 1, TRUE),
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
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- Payment Types Data
-- =====================================================
INSERT INTO payment_types (id, name, description, is_active) VALUES
(1, 'MONTHLY', 'Monthly fee payment', TRUE),
(2, 'QUARTERLY', 'Quarterly fee payment', TRUE),
(3, 'ANNUAL', 'Annual fee payment', TRUE),
(4, 'ONE_TIME', 'One-time fee payment', TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- Payment Statuses Data
-- =====================================================
INSERT INTO payment_statuses (id, name, description, is_active) VALUES
(1, 'PENDING', 'Payment is pending', TRUE),
(2, 'PAID', 'Payment completed successfully', TRUE),
(3, 'PARTIAL', 'Partial payment made', TRUE),
(4, 'OVERDUE', 'Payment is overdue', TRUE),
(5, 'CANCELLED', 'Payment was cancelled', TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- Payment Methods Data
-- =====================================================
INSERT INTO payment_methods (id, name, description, is_active) VALUES
(1, 'CASH', 'Cash payment', TRUE),
(2, 'UPI', 'UPI payment (PhonePe, GPay, etc.)', TRUE),
(3, 'BANK_TRANSFER', 'Bank transfer/NEFT/RTGS', TRUE),
(4, 'CHEQUE', 'Cheque payment', TRUE),
(5, 'CARD', 'Credit/Debit card payment', TRUE),
(6, 'ONLINE', 'Online payment gateway', TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- Leave Types Data
-- =====================================================
INSERT INTO leave_types (id, name, description, max_days_per_year, requires_medical_certificate, is_active) VALUES
(1, 'SICK', 'Sick leave', 12, TRUE, TRUE),
(2, 'CASUAL', 'Casual leave', 15, FALSE, TRUE),
(3, 'EMERGENCY', 'Emergency leave', 5, FALSE, TRUE),
(4, 'MATERNITY', 'Maternity leave', 180, TRUE, TRUE),
(5, 'PATERNITY', 'Paternity leave', 15, FALSE, TRUE)
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
INSERT INTO leave_statuses (id, name, description, is_active) VALUES
(1, 'PENDING', 'Leave request is pending approval', TRUE),
(2, 'APPROVED', 'Leave request has been approved', TRUE),
(3, 'REJECTED', 'Leave request has been rejected', TRUE),
(4, 'CANCELLED', 'Leave request was cancelled', TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- Expense Categories Data
-- =====================================================
INSERT INTO expense_categories (id, name, description, budget_limit, requires_approval, is_active) VALUES
(1, 'STATIONERY', 'Office and classroom stationery', 50000.00, TRUE, TRUE),
(2, 'MAINTENANCE', 'Building and equipment maintenance', 100000.00, TRUE, TRUE),
(3, 'UTILITIES', 'Electricity, water, internet bills', 75000.00, TRUE, TRUE),
(4, 'TRANSPORT', 'Transportation and fuel expenses', 30000.00, TRUE, TRUE),
(5, 'EVENTS', 'School events and celebrations', 25000.00, TRUE, TRUE),
(6, 'EQUIPMENT', 'Educational equipment and supplies', 150000.00, TRUE, TRUE)
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
INSERT INTO expense_statuses (id, name, description, is_active) VALUES
(1, 'PENDING', 'Expense is pending approval', TRUE),
(2, 'APPROVED', 'Expense has been approved', TRUE),
(3, 'REJECTED', 'Expense has been rejected', TRUE),
(4, 'PAID', 'Expense has been paid', TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
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
\echo '- 5 Payment statuses'
\echo '- 6 Payment methods'
\echo '- 5 Leave types'
\echo '- 4 Leave statuses'
\echo '- 6 Expense categories'
\echo '- 4 Expense statuses'
\echo ''
\echo 'Total: 57 metadata records loaded'
\echo '=========================================='
