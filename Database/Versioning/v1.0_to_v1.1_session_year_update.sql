-- =====================================================
-- Version 1.0 to 1.1 Migration: Session Year Updates
-- =====================================================
-- This script adds support for 2022-23 session year and updates constraints

-- Start transaction
BEGIN;

-- =====================================================
-- 1. Update CHECK constraints to include 2022-23 session year
-- =====================================================

-- Students table - Update session year constraint
ALTER TABLE students 
DROP CONSTRAINT IF EXISTS chk_students_session_year,
ADD CONSTRAINT chk_students_session_year CHECK (session_year IN ('2022-23', '2023-24', '2024-25', '2025-26', '2026-27'));

-- Fee Structures table - Update session year constraint
ALTER TABLE fee_structures 
DROP CONSTRAINT IF EXISTS chk_fee_structures_session_year,
ADD CONSTRAINT chk_fee_structures_session_year CHECK (session_year IN ('2022-23', '2023-24', '2024-25', '2025-26', '2026-27'));

-- Fee Records table - Update session year constraint
ALTER TABLE fee_records 
DROP CONSTRAINT IF EXISTS chk_fee_records_session_year,
ADD CONSTRAINT chk_fee_records_session_year CHECK (session_year IN ('2022-23', '2023-24', '2024-25', '2025-26', '2026-27'));

-- Student Academic History table - Update session year constraint
ALTER TABLE student_academic_history 
DROP CONSTRAINT IF EXISTS chk_student_academic_history_session_year,
ADD CONSTRAINT chk_student_academic_history_session_year CHECK (session_year IN ('2022-23', '2023-24', '2024-25', '2025-26', '2026-27'));

-- Teacher Subject Assignments table - Update session year constraint
ALTER TABLE teacher_subject_assignments 
DROP CONSTRAINT IF EXISTS chk_teacher_subject_assignments_session_year,
ADD CONSTRAINT chk_teacher_subject_assignments_session_year CHECK (session_year IN ('2022-23', '2023-24', '2024-25', '2025-26', '2026-27'));

-- Fee Discounts table - Update session year constraint
ALTER TABLE fee_discounts 
DROP CONSTRAINT IF EXISTS chk_fee_discounts_session_year,
ADD CONSTRAINT chk_fee_discounts_session_year CHECK (session_year IN ('2022-23', '2023-24', '2024-25', '2025-26', '2026-27'));

-- Leave Balance table - Update academic year constraint
ALTER TABLE leave_balance 
DROP CONSTRAINT IF EXISTS chk_leave_balance_academic_year,
ADD CONSTRAINT chk_leave_balance_academic_year CHECK (academic_year IN ('2022-23', '2023-24', '2024-25', '2025-26', '2026-27'));

-- Holiday Calendar table - Update academic year constraint
ALTER TABLE holiday_calendar 
DROP CONSTRAINT IF EXISTS chk_holiday_calendar_academic_year,
ADD CONSTRAINT chk_holiday_calendar_academic_year CHECK (academic_year IN ('2022-23', '2023-24', '2024-25', '2025-26', '2026-27'));

-- Budgets table - Update budget year constraint
ALTER TABLE budgets 
DROP CONSTRAINT IF EXISTS chk_budgets_budget_year,
ADD CONSTRAINT chk_budgets_budget_year CHECK (budget_year IN ('2022-23', '2023-24', '2024-25', '2025-26', '2026-27'));

-- Expenses table - Update budget year constraint
ALTER TABLE expenses 
DROP CONSTRAINT IF EXISTS chk_expenses_budget_year,
ADD CONSTRAINT chk_expenses_budget_year CHECK (budget_year IN ('2022-23', '2023-24', '2024-25', '2025-26', '2026-27'));

-- Expense Categories table - Update budget year constraint
ALTER TABLE expense_categories 
DROP CONSTRAINT IF EXISTS chk_expense_categories_budget_year,
ADD CONSTRAINT chk_expense_categories_budget_year CHECK (budget_year IN ('2022-23', '2023-24', '2024-25', '2025-26', '2026-27'));

-- =====================================================
-- 2. Add sample fee structure for 2022-23 if needed
-- =====================================================

-- Insert fee structures for 2022-23 session (optional)
INSERT INTO fee_structures (
    class_name, session_year, tuition_fee, admission_fee, development_fee, activity_fee,
    transport_fee, library_fee, lab_fee, exam_fee, other_fee, total_annual_fee, created_at
) VALUES 
('PG', '2022-23', 16000, 1800, 1200, 800, 2500, 400, 0, 400, 400, 23500, NOW()),
('LKG', '2022-23', 20000, 1800, 1200, 1000, 2500, 500, 0, 500, 500, 28000, NOW()),
('UKG', '2022-23', 22000, 1800, 1200, 1000, 2500, 500, 0, 500, 500, 30000, NOW()),
('Class 1', '2022-23', 24000, 2200, 1800, 1200, 3000, 700, 400, 700, 700, 34700, NOW()),
('Class 2', '2022-23', 26000, 2200, 1800, 1200, 3000, 700, 400, 700, 700, 36700, NOW()),
('Class 3', '2022-23', 28000, 2200, 1800, 1200, 3000, 900, 700, 900, 900, 39600, NOW()),
('Class 4', '2022-23', 30000, 2200, 1800, 1200, 3000, 900, 700, 900, 900, 41600, NOW()),
('Class 5', '2022-23', 32000, 2200, 1800, 1200, 3000, 900, 900, 900, 900, 43800, NOW()),
('Class 6', '2022-23', 34000, 2700, 2200, 1800, 3500, 1100, 1100, 1100, 1100, 48600, NOW()),
('Class 7', '2022-23', 36000, 2700, 2200, 1800, 3500, 1100, 1100, 1100, 1100, 50600, NOW()),
('Class 8', '2022-23', 38000, 2700, 2200, 1800, 3500, 1100, 1100, 1100, 1100, 52600, NOW())
ON CONFLICT (class_name, session_year) DO NOTHING;

-- =====================================================
-- 3. Update version tracking
-- =====================================================

-- Create version tracking table if it doesn't exist
CREATE TABLE IF NOT EXISTS schema_versions (
    id SERIAL PRIMARY KEY,
    version VARCHAR(10) NOT NULL,
    description TEXT,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    applied_by VARCHAR(100) DEFAULT current_user
);

-- Insert version record
INSERT INTO schema_versions (version, description) 
VALUES ('1.1', 'Added support for 2022-23 session year and updated all related constraints')
ON CONFLICT DO NOTHING;

-- =====================================================
-- 4. Verification queries
-- =====================================================

-- Verify updated constraints
SELECT 
    tc.table_name,
    tc.constraint_name,
    cc.check_clause
FROM information_schema.table_constraints tc
JOIN information_schema.check_constraints cc ON tc.constraint_name = cc.constraint_name
WHERE tc.table_schema = 'public' 
AND tc.constraint_type = 'CHECK'
AND cc.check_clause LIKE '%2022-23%'
ORDER BY tc.table_name, tc.constraint_name;

-- Verify fee structures for 2022-23
SELECT 
    class_name,
    session_year,
    total_annual_fee
FROM fee_structures 
WHERE session_year = '2022-23'
ORDER BY 
    CASE class_name
        WHEN 'PG' THEN 1
        WHEN 'LKG' THEN 2
        WHEN 'UKG' THEN 3
        ELSE 4 + CAST(SUBSTRING(class_name FROM 'Class (\d+)') AS INTEGER)
    END;

-- Check version history
SELECT * FROM schema_versions ORDER BY applied_at DESC;

-- Commit the transaction
COMMIT;

-- Success message
SELECT 'Version 1.0 to 1.1 migration completed successfully!' as result;
SELECT 'Added support for 2022-23 session year across all tables' as details;
