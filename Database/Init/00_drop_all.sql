-- =====================================================
-- Drop All Database Objects - Clean Slate
-- =====================================================
-- WARNING: This script will delete ALL data and tables
-- Use with extreme caution and only for fresh installations

-- Start transaction
BEGIN;

-- =====================================================
-- 1. Drop all tables in dependency order
-- =====================================================

-- Drop reporting and audit tables first
DROP TABLE IF EXISTS expense_reports CASCADE;
DROP TABLE IF EXISTS leave_reports CASCADE;
DROP TABLE IF EXISTS fee_reports CASCADE;

-- Drop notification and communication tables
DROP TABLE IF EXISTS leave_notifications CASCADE;
DROP TABLE IF EXISTS fee_reminders CASCADE;

-- Drop calendar and summary tables
DROP TABLE IF EXISTS leave_calendar CASCADE;

-- Drop enhanced fee system tables (monthly tracking)
DROP TABLE IF EXISTS monthly_payment_allocations CASCADE;
DROP TABLE IF EXISTS monthly_fee_tracking CASCADE;

-- Drop transaction and payment tables
DROP TABLE IF EXISTS purchase_order_items CASCADE;
DROP TABLE IF EXISTS purchase_orders CASCADE;
DROP TABLE IF EXISTS fee_payments CASCADE;

-- Drop configuration and policy tables
DROP TABLE IF EXISTS leave_policies CASCADE;
DROP TABLE IF EXISTS leave_approvers CASCADE;
DROP TABLE IF EXISTS budgets CASCADE;

-- Drop metadata tables (new metadata-driven architecture)
DROP TABLE IF EXISTS user_types CASCADE;
DROP TABLE IF EXISTS session_years CASCADE;
DROP TABLE IF EXISTS genders CASCADE;
DROP TABLE IF EXISTS classes CASCADE;
DROP TABLE IF EXISTS payment_types CASCADE;
DROP TABLE IF EXISTS payment_statuses CASCADE;
DROP TABLE IF EXISTS payment_methods CASCADE;
DROP TABLE IF EXISTS leave_types CASCADE;
DROP TABLE IF EXISTS leave_statuses CASCADE;
DROP TABLE IF EXISTS expense_categories CASCADE;
DROP TABLE IF EXISTS expense_statuses CASCADE;
DROP TABLE IF EXISTS employment_statuses CASCADE;
DROP TABLE IF EXISTS qualifications CASCADE;

-- Drop main operational tables
DROP TABLE IF EXISTS expenses CASCADE;
DROP TABLE IF EXISTS vendors CASCADE;
DROP TABLE IF EXISTS leave_balance CASCADE;
DROP TABLE IF EXISTS leave_requests CASCADE;
DROP TABLE IF EXISTS fee_discounts CASCADE;
DROP TABLE IF EXISTS fee_records CASCADE;
DROP TABLE IF EXISTS fee_structures CASCADE;

-- Drop document and qualification tables
DROP TABLE IF EXISTS teacher_performance_reviews CASCADE;
DROP TABLE IF EXISTS teacher_documents CASCADE;
DROP TABLE IF EXISTS teacher_experience CASCADE;
DROP TABLE IF EXISTS teacher_qualifications CASCADE;
DROP TABLE IF EXISTS teacher_subject_assignments CASCADE;
DROP TABLE IF EXISTS student_notes CASCADE;
DROP TABLE IF EXISTS student_documents CASCADE;
DROP TABLE IF EXISTS student_academic_history CASCADE;

-- Drop main entity tables
DROP TABLE IF EXISTS teachers CASCADE;
DROP TABLE IF EXISTS students CASCADE;

-- Drop user-related tables
DROP TABLE IF EXISTS user_role_permissions CASCADE;
DROP TABLE IF EXISTS user_roles CASCADE;
DROP TABLE IF EXISTS user_permissions CASCADE;
DROP TABLE IF EXISTS user_profiles CASCADE;
DROP TABLE IF EXISTS password_resets CASCADE;
DROP TABLE IF EXISTS user_sessions CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Drop version tracking table
DROP TABLE IF EXISTS schema_versions CASCADE;

-- =====================================================
-- 2. Drop all custom types (ENUMs) - Now using metadata tables instead
-- =====================================================

-- Note: ENUMs have been replaced with metadata tables in the optimized schema
-- These DROP statements are kept for cleaning up any legacy enum types

DROP TYPE IF EXISTS user_role_enum CASCADE;
DROP TYPE IF EXISTS gender_enum CASCADE;
DROP TYPE IF EXISTS class_enum CASCADE;
DROP TYPE IF EXISTS qualification_enum CASCADE;
DROP TYPE IF EXISTS employment_status_enum CASCADE;
DROP TYPE IF EXISTS session_year_enum CASCADE;
DROP TYPE IF EXISTS payment_type_enum CASCADE;
DROP TYPE IF EXISTS payment_status_enum CASCADE;
DROP TYPE IF EXISTS payment_method_enum CASCADE;
DROP TYPE IF EXISTS leave_type_enum CASCADE;
DROP TYPE IF EXISTS leave_status_enum CASCADE;
DROP TYPE IF EXISTS expense_category_enum CASCADE;
DROP TYPE IF EXISTS expense_status_enum CASCADE;
DROP TYPE IF EXISTS employment_type_enum CASCADE;

-- =====================================================
-- 3. Drop all sequences (if any custom ones exist)
-- =====================================================

-- Most sequences are auto-created with SERIAL columns and will be dropped with tables
-- Add any custom sequences here if needed

-- =====================================================
-- 4. Drop all functions and procedures
-- =====================================================

-- Drop utility functions
DROP FUNCTION IF EXISTS calculate_age(DATE) CASCADE;
DROP FUNCTION IF EXISTS get_academic_year(DATE) CASCADE;
DROP FUNCTION IF EXISTS calculate_fee_balance() CASCADE;

-- Drop any enhanced fee system functions (if they exist)
DROP FUNCTION IF EXISTS enable_monthly_tracking_for_student(INTEGER, INTEGER) CASCADE;
DROP FUNCTION IF EXISTS calculate_monthly_fees(INTEGER) CASCADE;
DROP FUNCTION IF EXISTS allocate_payment_to_months(INTEGER, DECIMAL) CASCADE;

-- =====================================================
-- 5. Drop all views
-- =====================================================

-- Drop summary views
DROP VIEW IF EXISTS student_summary CASCADE;
DROP VIEW IF EXISTS teacher_summary CASCADE;
DROP VIEW IF EXISTS fee_collection_summary CASCADE;
DROP VIEW IF EXISTS enhanced_student_fee_status CASCADE;

-- =====================================================
-- 6. Verification - Check remaining objects
-- =====================================================

-- List any remaining tables
SELECT 
    schemaname,
    tablename
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY tablename;

-- List any remaining types
SELECT 
    typname
FROM pg_type 
WHERE typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
AND typtype = 'e'  -- ENUM types
ORDER BY typname;

-- List any remaining sequences
SELECT 
    schemaname,
    sequencename
FROM pg_sequences 
WHERE schemaname = 'public'
ORDER BY sequencename;

-- Commit the transaction
COMMIT;

-- =====================================================
-- Success Messages
-- =====================================================

SELECT 'Database cleanup completed successfully!' as result;
SELECT 'All tables, types, and objects have been dropped' as details;
SELECT 'Database is now ready for fresh installation' as next_step;

-- =====================================================
-- IMPORTANT NOTES:
-- =====================================================
-- 1. This script drops ALL data - use only for fresh installations
-- 2. Always backup your database before running this script
-- 3. Run this script as a database superuser or owner
-- 4. After running this script, execute the 9 table creation scripts in order:
--    - Database/Tables/00_metadata_tables.sql
--    - Database/Tables/02_users.sql
--    - Database/Tables/03_students.sql (with inline constraints)
--    - Database/Tables/04_teachers.sql (with inline constraints)
--    - Database/Tables/05_fees.sql (with enhanced monthly tracking)
--    - Database/Tables/07_leaves.sql
--    - Database/Tables/08_expenses.sql (with inline constraints)
--    - Database/Tables/09_indexes.sql
--    - Database/Tables/10_constraints.sql (complex business logic only)
-- 5. Then run 02_load_initial_data_clean.sql to populate with initial data
-- 6. OPTIMIZED FOR CLOUD DEPLOYMENT - No versioning scripts needed
