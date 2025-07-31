-- =====================================================
-- Delete All Tables for Render Database - Metadata Migration
-- =====================================================
-- This script is specifically for deleting old table structure
-- from your render database to prepare for metadata-driven architecture
-- Run this on your render database before creating new structure

-- WARNING: This will delete ALL data and tables
-- Make sure you have a backup if needed

-- Start transaction
BEGIN;

-- =====================================================
-- 1. Drop all existing tables in dependency order
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
DROP TYPE IF EXISTS class_enum CASCADE;
DROP TYPE IF EXISTS qualification_enum CASCADE;
DROP TYPE IF EXISTS employment_status_enum CASCADE;
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
-- Drop any remaining sequences that might exist
DROP SEQUENCE IF EXISTS users_id_seq CASCADE;
DROP SEQUENCE IF EXISTS students_id_seq CASCADE;
DROP SEQUENCE IF EXISTS teachers_id_seq CASCADE;
DROP SEQUENCE IF EXISTS fee_structures_id_seq CASCADE;
DROP SEQUENCE IF EXISTS fee_records_id_seq CASCADE;
DROP SEQUENCE IF EXISTS fee_payments_id_seq CASCADE;
DROP SEQUENCE IF EXISTS leave_requests_id_seq CASCADE;
DROP SEQUENCE IF EXISTS expenses_id_seq CASCADE;

-- =====================================================
-- 4. Verification - Check remaining objects
-- =====================================================

-- List any remaining tables
SELECT 
    'Remaining tables:' as info,
    schemaname,
    tablename
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY tablename;

-- List any remaining types
SELECT 
    'Remaining custom types:' as info,
    typname
FROM pg_type 
WHERE typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
AND typtype = 'e'  -- ENUM types
ORDER BY typname;

-- List any remaining sequences
SELECT 
    'Remaining sequences:' as info,
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

SELECT 'Render database cleanup completed successfully!' as result;
SELECT 'All old tables, types, and objects have been dropped' as details;
SELECT 'Database is now ready for new metadata-driven structure' as next_step;

-- =====================================================
-- NEXT STEPS:
-- =====================================================
-- 1. Run the new metadata table creation scripts
-- 2. Run the new main table creation scripts with foreign keys
-- 3. Load initial metadata data
-- 4. Update your backend application to use new structure
