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
DROP TABLE IF EXISTS attendance_reports CASCADE;
DROP TABLE IF EXISTS fee_reports CASCADE;
DROP TABLE IF EXISTS user_audit_log CASCADE;

-- Drop notification and communication tables
DROP TABLE IF EXISTS leave_notifications CASCADE;
DROP TABLE IF EXISTS attendance_notifications CASCADE;
DROP TABLE IF EXISTS fee_reminders CASCADE;

-- Drop calendar and summary tables
DROP TABLE IF EXISTS leave_calendar CASCADE;
DROP TABLE IF EXISTS attendance_summary CASCADE;
DROP TABLE IF EXISTS holiday_calendar CASCADE;

-- Drop transaction and payment tables
DROP TABLE IF EXISTS purchase_order_items CASCADE;
DROP TABLE IF EXISTS purchase_orders CASCADE;
DROP TABLE IF EXISTS fee_payments CASCADE;

-- Drop configuration and policy tables
DROP TABLE IF EXISTS attendance_settings CASCADE;
DROP TABLE IF EXISTS leave_policies CASCADE;
DROP TABLE IF EXISTS leave_approvers CASCADE;
DROP TABLE IF EXISTS budgets CASCADE;
DROP TABLE IF EXISTS expense_categories CASCADE;

-- Drop main operational tables
DROP TABLE IF EXISTS expenses CASCADE;
DROP TABLE IF EXISTS vendors CASCADE;
DROP TABLE IF EXISTS leave_balance CASCADE;
DROP TABLE IF EXISTS leave_requests CASCADE;
DROP TABLE IF EXISTS teacher_attendance CASCADE;
DROP TABLE IF EXISTS student_attendance CASCADE;
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
DROP TABLE IF EXISTS user_permissions CASCADE;
DROP TABLE IF EXISTS user_profiles CASCADE;
DROP TABLE IF EXISTS email_verification_tokens CASCADE;
DROP TABLE IF EXISTS password_reset_tokens CASCADE;
DROP TABLE IF EXISTS user_sessions CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Drop version tracking table
DROP TABLE IF EXISTS schema_versions CASCADE;

-- =====================================================
-- 2. Drop all custom types (ENUMs)
-- =====================================================

DROP TYPE IF EXISTS user_role_enum CASCADE;
DROP TYPE IF EXISTS gender_enum CASCADE;
DROP TYPE IF EXISTS session_year_enum CASCADE;
DROP TYPE IF EXISTS payment_type_enum CASCADE;
DROP TYPE IF EXISTS payment_status_enum CASCADE;
DROP TYPE IF EXISTS payment_method_enum CASCADE;
DROP TYPE IF EXISTS leave_type_enum CASCADE;
DROP TYPE IF EXISTS leave_status_enum CASCADE;
DROP TYPE IF EXISTS attendance_status_enum CASCADE;
DROP TYPE IF EXISTS expense_category_enum CASCADE;
DROP TYPE IF EXISTS expense_status_enum CASCADE;
DROP TYPE IF EXISTS employment_type_enum CASCADE;

-- =====================================================
-- 3. Drop all sequences (if any custom ones exist)
-- =====================================================

-- Most sequences are auto-created with SERIAL columns and will be dropped with tables
-- Add any custom sequences here if needed

-- =====================================================
-- 4. Drop all functions and procedures (if any)
-- =====================================================

-- Add any custom functions or stored procedures here
-- Example:
-- DROP FUNCTION IF EXISTS calculate_fee_balance() CASCADE;
-- DROP FUNCTION IF EXISTS generate_attendance_report() CASCADE;

-- =====================================================
-- 5. Drop all views (if any)
-- =====================================================

-- Add any views here
-- Example:
-- DROP VIEW IF EXISTS student_fee_summary CASCADE;
-- DROP VIEW IF EXISTS teacher_attendance_summary CASCADE;

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
-- 4. After running this script, run 01_create_database.sql to recreate the schema
-- 5. Then run 02_load_initial_data.sql to populate with initial data
