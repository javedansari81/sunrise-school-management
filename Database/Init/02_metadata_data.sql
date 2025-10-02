-- =====================================================
-- Optimized Metadata Initialization for Cloud Deployment
-- =====================================================
-- This script populates all metadata tables with complete reference data
-- for the Sunrise National Public School Management System
--
-- FEATURES:
-- - Complete data for Indian education system (Nursery to Class 12)
-- - Consistent UPPER_SNAKE_CASE values for backend integration
-- - User-friendly display names for UI
-- - Logical display ordering for dropdowns
-- - Comprehensive fee management support
-- - Complete leave and expense management categories
--
-- Primary keys are manually assigned (non-auto-increment)

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
(1, 'MALE', 'Male gender', TRUE),
(2, 'FEMALE', 'Female gender', TRUE),
(3, 'OTHER', 'Other gender identity', TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- Classes Data (Complete Indian Education System)
-- =====================================================
INSERT INTO classes (id, name, description, display_name, sort_order, is_active) VALUES
(1, 'PRE_NURSERY', 'Pre-primary education for ages 2-3 years', 'Pre-Nursery', 1, TRUE),
(2, 'NURSERY', 'Pre-primary education for ages 3-4 years', 'Nursery', 2, TRUE),
(3, 'LKG', 'Lower Kindergarten for ages 4-5 years', 'Lower KG', 3, TRUE),
(4, 'UKG', 'Upper Kindergarten for ages 5-6 years', 'Upper KG', 4, TRUE),
(5, 'CLASS_1', 'Primary education - Grade 1 (ages 6-7)', 'Class 1', 5, TRUE),
(6, 'CLASS_2', 'Primary education - Grade 2 (ages 7-8)', 'Class 2', 6, TRUE),
(7, 'CLASS_3', 'Primary education - Grade 3 (ages 8-9)', 'Class 3', 7, TRUE),
(8, 'CLASS_4', 'Primary education - Grade 4 (ages 9-10)', 'Class 4', 8, TRUE),
(9, 'CLASS_5', 'Primary education - Grade 5 (ages 10-11)', 'Class 5', 9, TRUE),
(10, 'CLASS_6', 'Middle school - Grade 6 (ages 11-12)', 'Class 6', 10, TRUE),
(11, 'CLASS_7', 'Middle school - Grade 7 (ages 12-13)', 'Class 7', 11, TRUE),
(12, 'CLASS_8', 'Middle school - Grade 8 (ages 13-14)', 'Class 8', 12, TRUE),
(13, 'CLASS_9', 'Secondary education - Grade 9 (ages 14-15)', 'Class 9', 13, TRUE),
(14, 'CLASS_10', 'Secondary education - Grade 10 (ages 15-16)', 'Class 10', 14, TRUE),
(15, 'CLASS_11', 'Higher secondary - Grade 11 (ages 16-17)', 'Class 11', 15, TRUE),
(16, 'CLASS_12', 'Higher secondary - Grade 12 (ages 17-18)', 'Class 12', 16, TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    display_name = EXCLUDED.display_name,
    sort_order = EXCLUDED.sort_order,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- Payment Types Data (Complete Fee Management Support)
-- =====================================================
INSERT INTO payment_types (id, name, description, is_active) VALUES
(1, 'MONTHLY', 'Monthly payment frequency (12 installments per year)', TRUE),
(2, 'QUARTERLY', 'Quarterly payment frequency (4 installments per year)', TRUE),
(3, 'HALF_YEARLY', 'Half yearly payment frequency (2 installments per year)', TRUE),
(4, 'YEARLY', 'Annual payment frequency (1 installment per year)', TRUE),
(5, 'ONE_TIME', 'One-time payment (admission fees, etc.)', TRUE),
(6, 'CUSTOM', 'Custom payment schedule', TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- Payment Statuses Data (Complete Status Management)
-- =====================================================
INSERT INTO payment_statuses (id, name, description, color_code, is_active) VALUES
(1, 'PENDING', 'Payment is pending', '#FFA500', TRUE),
(2, 'PARTIAL', 'Partial payment received', '#FFD700', TRUE),
(3, 'PAID', 'Payment completed in full', '#28A745', TRUE),
(4, 'OVERDUE', 'Payment is overdue', '#DC3545', TRUE),
(5, 'CANCELLED', 'Payment cancelled', '#6C757D', TRUE),
(6, 'REFUNDED', 'Payment refunded', '#17A2B8', TRUE),
(7, 'FAILED', 'Payment failed', '#DC3545', TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    color_code = EXCLUDED.color_code,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- Payment Methods Data (Indian Payment Systems)
-- =====================================================
INSERT INTO payment_methods (id, name, description, requires_reference, is_active) VALUES
(1, 'CASH', 'Cash payment at school office', FALSE, TRUE),
(2, 'CHEQUE', 'Cheque payment (requires cheque number)', TRUE, TRUE),
(3, 'BANK_TRANSFER', 'Direct bank transfer (NEFT/RTGS)', TRUE, TRUE),
(4, 'UPI', 'UPI payment (PhonePe, GPay, Paytm, etc.)', TRUE, TRUE),
(5, 'DEBIT_CARD', 'Debit card payment', TRUE, TRUE),
(6, 'CREDIT_CARD', 'Credit card payment', TRUE, TRUE),
(7, 'NET_BANKING', 'Internet banking payment', TRUE, TRUE),
(8, 'DEMAND_DRAFT', 'Demand draft payment', TRUE, TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    requires_reference = EXCLUDED.requires_reference,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- Leave Types Data (Teachers and Students)
-- =====================================================
INSERT INTO leave_types (id, name, description, max_days_per_year, requires_medical_certificate, is_active) VALUES
(1, 'SICK_LEAVE', 'Medical leave for illness', 15, TRUE, TRUE),
(2, 'CASUAL_LEAVE', 'General casual leave for personal work', 12, FALSE, TRUE),
(3, 'EMERGENCY_LEAVE', 'Emergency situations (family emergency, etc.)', 5, FALSE, TRUE),
(4, 'MEDICAL_LEAVE', 'Extended medical leave (surgery, recovery)', 30, TRUE, TRUE),
(5, 'PERSONAL_LEAVE', 'Personal reasons (family functions, etc.)', 10, FALSE, TRUE),
(6, 'MATERNITY_LEAVE', 'Maternity leave for female staff', 180, TRUE, TRUE),
(7, 'PATERNITY_LEAVE', 'Paternity leave for male staff', 15, FALSE, TRUE),
(8, 'STUDY_LEAVE', 'Educational purposes and training', 20, FALSE, TRUE),
(9, 'BEREAVEMENT_LEAVE', 'Death in family', 7, FALSE, TRUE),
(10, 'COMPENSATORY_LEAVE', 'Compensation for extra work/holidays', 15, FALSE, TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    max_days_per_year = EXCLUDED.max_days_per_year,
    requires_medical_certificate = EXCLUDED.requires_medical_certificate,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- Leave Statuses Data (Complete Workflow)
-- =====================================================
INSERT INTO leave_statuses (id, name, description, color_code, is_final, is_active) VALUES
(1, 'PENDING', 'Leave application pending approval', '#FFC107', FALSE, TRUE),
(2, 'APPROVED', 'Leave application approved by authority', '#28A745', TRUE, TRUE),
(3, 'REJECTED', 'Leave application rejected', '#DC3545', TRUE, TRUE),
(4, 'CANCELLED', 'Leave application cancelled by applicant', '#6C757D', TRUE, TRUE),
(5, 'WITHDRAWN', 'Leave withdrawn after approval', '#17A2B8', TRUE, TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    color_code = EXCLUDED.color_code,
    is_final = EXCLUDED.is_final,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- Expense Categories Data (Comprehensive School Operations)
-- =====================================================
INSERT INTO expense_categories (id, name, description, budget_limit, requires_approval, is_active) VALUES
(1, 'SALARY', 'Staff salaries and wages', 2000000.00, TRUE, TRUE),
(2, 'INFRASTRUCTURE', 'Building construction and major repairs', 500000.00, TRUE, TRUE),
(3, 'MAINTENANCE', 'Regular maintenance and minor repairs', 100000.00, TRUE, TRUE),
(4, 'UTILITIES', 'Electricity, water, gas, internet, phone bills', 50000.00, FALSE, TRUE),
(5, 'OFFICE_SUPPLIES', 'Stationery, printing, office materials', 25000.00, FALSE, TRUE),
(6, 'ACADEMIC_SUPPLIES', 'Teaching materials, books, educational resources', 60000.00, FALSE, TRUE),
(7, 'FURNITURE_EQUIPMENT', 'Desks, chairs, computers, projectors', 200000.00, TRUE, TRUE),
(8, 'TRANSPORTATION', 'School bus, vehicle maintenance, fuel', 75000.00, TRUE, TRUE),
(9, 'EVENTS_ACTIVITIES', 'Annual day, sports day, cultural events', 30000.00, TRUE, TRUE),
(10, 'MARKETING_ADMISSION', 'Advertising, brochures, admission campaigns', 20000.00, TRUE, TRUE),
(11, 'STAFF_DEVELOPMENT', 'Training, workshops, professional development', 40000.00, TRUE, TRUE),
(12, 'SPORTS_EQUIPMENT', 'Sports materials, playground equipment', 35000.00, TRUE, TRUE),
(13, 'LIBRARY_RESOURCES', 'Books, magazines, digital resources', 25000.00, FALSE, TRUE),
(14, 'LABORATORY_SUPPLIES', 'Science lab equipment, chemicals, apparatus', 80000.00, TRUE, TRUE),
(15, 'SECURITY_SERVICES', 'Security guards, CCTV, safety equipment', 45000.00, TRUE, TRUE),
(16, 'CLEANING_HYGIENE', 'Cleaning supplies, sanitizers, housekeeping', 30000.00, FALSE, TRUE),
(17, 'MEDICAL_HEALTH', 'First aid, health checkups, medical supplies', 20000.00, FALSE, TRUE),
(18, 'INSURANCE', 'Building, vehicle, staff insurance premiums', 50000.00, TRUE, TRUE),
(19, 'LEGAL_COMPLIANCE', 'Legal fees, licenses, regulatory compliance', 25000.00, TRUE, TRUE),
(20, 'MISCELLANEOUS', 'Other miscellaneous expenses', 15000.00, TRUE, TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    budget_limit = EXCLUDED.budget_limit,
    requires_approval = EXCLUDED.requires_approval,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- Expense Statuses Data (Complete Expense Workflow)
-- =====================================================
INSERT INTO expense_statuses (id, name, description, color_code, is_final, is_active) VALUES
(1, 'PENDING', 'Expense request pending approval', '#FFC107', FALSE, TRUE),
(2, 'APPROVED', 'Expense request approved, ready for payment', '#28A745', FALSE, TRUE),
(3, 'REJECTED', 'Expense request rejected', '#DC3545', TRUE, TRUE),
(4, 'PAID', 'Expense payment completed', '#007BFF', TRUE, TRUE),
(5, 'CANCELLED', 'Expense request cancelled', '#6C757D', TRUE, TRUE),
(6, 'ON_HOLD', 'Expense request on hold', '#FD7E14', FALSE, TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    color_code = EXCLUDED.color_code,
    is_final = EXCLUDED.is_final,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- Employment Statuses Data (Teaching and Non-Teaching Staff)
-- =====================================================
INSERT INTO employment_statuses (id, name, description, is_active) VALUES
(1, 'FULL_TIME', 'Full-time permanent employee with benefits', TRUE),
(2, 'PART_TIME', 'Part-time employee (less than 40 hours/week)', TRUE),
(3, 'CONTRACT', 'Contract-based employee for specific period', TRUE),
(4, 'SUBSTITUTE', 'Substitute teacher for temporary replacement', TRUE),
(5, 'PROBATION', 'New employee on probation period', TRUE),
(6, 'INTERN', 'Student teacher or intern', TRUE),
(7, 'CONSULTANT', 'External consultant or specialist', TRUE),
(8, 'RETIRED', 'Retired employee (for records)', FALSE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- Qualifications Data (Indian Education System)
-- =====================================================
INSERT INTO qualifications (id, name, description, level_order, is_active) VALUES
(1, 'HIGH_SCHOOL', '10th standard (Secondary School Certificate)', 1, TRUE),
(2, 'HIGHER_SECONDARY', '12th standard (Higher Secondary Certificate)', 2, TRUE),
(3, 'CERTIFICATE', 'Certificate course (6 months to 1 year)', 3, TRUE),
(4, 'DIPLOMA', 'Diploma qualification (2-3 years)', 4, TRUE),
(5, 'BACHELOR', 'Bachelor''s degree (B.A., B.Sc., B.Com., B.Ed., etc.)', 5, TRUE),
(6, 'MASTER', 'Master''s degree (M.A., M.Sc., M.Com., M.Ed., etc.)', 6, TRUE),
(7, 'M_PHIL', 'Master of Philosophy degree', 7, TRUE),
(8, 'PHD', 'Doctor of Philosophy (Ph.D.)', 8, TRUE),
(9, 'POST_DOC', 'Post-doctoral research', 9, TRUE),
(10, 'PROFESSIONAL', 'Professional qualifications (CA, CS, CMA, etc.)', 5, TRUE),
(11, 'OTHER', 'Other qualifications not listed above', 10, TRUE)
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
SELECT 'Optimized metadata tables populated successfully!' as result;
SELECT 'Complete data for Sunrise National Public School Management System' as details;

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

-- Show sample data for key tables
SELECT 'SAMPLE CLASSES:' as info, name, display_name, sort_order
FROM classes WHERE is_active = TRUE ORDER BY sort_order LIMIT 5;

SELECT 'SAMPLE PAYMENT METHODS:' as info, name, requires_reference
FROM payment_methods WHERE is_active = TRUE LIMIT 5;

SELECT 'CURRENT SESSION YEAR:' as info, name, start_date, end_date
FROM session_years WHERE is_current = TRUE;
