-- =====================================================
-- Master Deployment Script for Sunrise School Management System
-- =====================================================
-- This script deploys the complete database in the correct order
--
-- PREREQUISITES:
-- 1. PostgreSQL database 'sunrise_school_db' must exist
-- 2. User 'sunrise_user' must exist with proper permissions
--
-- USAGE:
-- psql -U sunrise_user -d sunrise_school_db -f Database/deploy_database.sql
--
-- =====================================================

\echo '=========================================='
\echo 'SUNRISE SCHOOL MANAGEMENT SYSTEM'
\echo 'Database Deployment Script'
\echo '=========================================='
\echo ''

-- =====================================================
-- STEP 1: Schema Initialization
-- =====================================================

\echo '=========================================='
\echo 'STEP 1: Schema Initialization'
\echo '=========================================='
\ir Schema/00_create_schema.sql
\echo ''

-- =====================================================
-- STEP 2: Create Metadata Tables
-- =====================================================

\echo '=========================================='
\echo 'STEP 2: Creating Metadata Tables'
\echo '=========================================='

\ir Tables/T100_user_types.sql
\ir Tables/T110_session_years.sql
\ir Tables/T120_genders.sql
\ir Tables/T130_classes.sql
\ir Tables/T140_payment_types.sql
\ir Tables/T150_payment_statuses.sql
\ir Tables/T160_payment_methods.sql
\ir Tables/T170_leave_types.sql
\ir Tables/T180_leave_statuses.sql
\ir Tables/T190_expense_categories.sql
\ir Tables/T200_expense_statuses.sql
\ir Tables/T210_employment_statuses.sql
\ir Tables/T220_qualifications.sql

\echo ''
\echo '✓ All metadata tables created'
\echo ''

-- =====================================================
-- STEP 3: Create Core Tables
-- =====================================================

\echo '=========================================='
\echo 'STEP 3: Creating Core Tables'
\echo '=========================================='

\ir Tables/T300_users.sql
\ir Tables/T310_students.sql
\ir Tables/T320_teachers.sql

\echo ''
\echo '✓ All core tables created'
\echo ''

-- =====================================================
-- STEP 4: Create Fee Management Tables
-- =====================================================

\echo '=========================================='
\echo 'STEP 4: Creating Fee Management Tables'
\echo '=========================================='

\ir Tables/T400_fee_structures.sql
\ir Tables/T410_fee_records.sql
\ir Tables/T415_fee_payments.sql
\ir Tables/T420_monthly_fee_tracking.sql
\ir Tables/T430_monthly_payment_allocations.sql

\echo ''
\echo '✓ All fee management tables created'
\echo ''

-- =====================================================
-- STEP 5: Create Expense Management Tables
-- =====================================================

\echo '=========================================='
\echo 'STEP 5: Creating Expense Management Tables'
\echo '=========================================='

\ir Tables/T500_expenses.sql
\ir Tables/T510_vendors.sql

\echo ''
\echo '✓ All expense management tables created'
\echo ''

-- =====================================================
-- STEP 6: Create Leave Management Tables
-- =====================================================

\echo '=========================================='
\echo 'STEP 6: Creating Leave Management Tables'
\echo '=========================================='

\ir Tables/T600_leave_requests.sql

\echo ''
\echo '✓ All leave management tables created'
\echo ''

-- =====================================================
-- STEP 7: Create Functions
-- =====================================================

\echo '=========================================='
\echo 'STEP 7: Creating Functions'
\echo '=========================================='

\ir Functions/F100_calculate_age.sql
\ir Functions/F110_get_academic_year.sql
\ir Functions/F120_calculate_fee_balance.sql
\ir Functions/F130_enable_monthly_tracking_complete.sql

\echo ''
\echo '✓ All functions created'
\echo ''

-- =====================================================
-- STEP 8: Create Views
-- =====================================================

\echo '=========================================='
\echo 'STEP 8: Creating Views'
\echo '=========================================='

\ir Views/V100_student_summary.sql
\ir Views/V110_teacher_summary.sql
\ir Views/V120_fee_collection_summary.sql
\ir Views/V130_enhanced_student_fee_status.sql

\echo ''
\echo '✓ All views created'
\echo ''

-- =====================================================
-- STEP 9: Load Metadata
-- =====================================================

\echo '=========================================='
\echo 'STEP 9: Loading Metadata'
\echo '=========================================='

\ir Init/01_load_metadata.sql

\echo ''
\echo '✓ Metadata loaded'
\echo ''

-- =====================================================
-- STEP 10: Create Admin User
-- =====================================================

\echo '=========================================='
\echo 'STEP 10: Creating Admin User'
\echo '=========================================='

\ir Init/02_create_admin_user.sql

\echo ''
\echo '✓ Admin user created'
\echo ''

-- =====================================================
-- Success Message
-- =====================================================

\echo ''
\echo '=========================================='
\echo 'DATABASE DEPLOYMENT COMPLETED!'
\echo '=========================================='
\echo ''
\echo 'Database Structure:'
\echo '  - Schema: sunrise'
\echo '  - Tables: 23'
\echo '  - Functions: 3'
\echo '  - Views: 4'
\echo '  - Metadata Records: 78'
\echo '  - Indexes: 26+'
\echo ''
\echo 'Next Steps:'
\echo '  1. Verify deployment: SELECT * FROM schema_versions;'
\echo '  2. Test admin login with credentials from 02_create_admin_user.sql'
\echo '  3. Start the application'
\echo ''
\echo '=========================================='
\echo 'DEPLOYMENT SUCCESSFUL!'
\echo '=========================================='

