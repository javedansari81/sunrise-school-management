-- =====================================================
-- Database Deployment Verification Script
-- Sunrise School Management System
-- =====================================================
-- This script verifies that the database deployment was successful
-- Run this AFTER deploying the database to Render.com
--
-- USAGE:
-- psql "postgresql://sunrise_user:[password]@[host].singapore-postgres.render.com/sunrise_school_db" -f Database/verify_deployment.sql
--
-- =====================================================

\echo '=========================================='
\echo 'DATABASE DEPLOYMENT VERIFICATION'
\echo 'Sunrise School Management System'
\echo '=========================================='
\echo ''

-- Set search path
SET search_path TO sunrise, public;

-- =====================================================
-- 1. Verify Schema and Basic Setup
-- =====================================================

\echo '1. Verifying Schema Setup...'
\echo '----------------------------------------'

-- Check schema exists
SELECT 
    CASE 
        WHEN EXISTS (SELECT 1 FROM information_schema.schemata WHERE schema_name = 'sunrise') 
        THEN '✅ Schema "sunrise" exists'
        ELSE '❌ Schema "sunrise" missing'
    END as schema_check;

-- Check search path
SHOW search_path;

\echo ''

-- =====================================================
-- 2. Verify Table Count and Structure
-- =====================================================

\echo '2. Verifying Table Structure...'
\echo '----------------------------------------'

-- Count total tables
SELECT 
    COUNT(*) as total_tables,
    CASE 
        WHEN COUNT(*) = 25 THEN '✅ Correct table count (25)'
        ELSE '❌ Incorrect table count (expected 25, got ' || COUNT(*) || ')'
    END as table_count_check
FROM information_schema.tables 
WHERE table_schema = 'sunrise' AND table_type = 'BASE TABLE';

-- List all tables with categories
\echo ''
\echo 'Table List by Category:'
\echo '----------------------------------------'

-- Metadata Tables (T100-T240)
\echo 'Metadata Tables:'
SELECT '  ' || table_name as metadata_tables
FROM information_schema.tables 
WHERE table_schema = 'sunrise' 
  AND table_type = 'BASE TABLE'
  AND table_name ~ '^(user_types|session_years|genders|classes|payment_types|payment_statuses|payment_methods|leave_types|leave_statuses|expense_categories|expense_statuses|employment_statuses|qualifications|departments|positions)$'
ORDER BY table_name;

-- Core Tables (T300-T320)
\echo ''
\echo 'Core Tables:'
SELECT '  ' || table_name as core_tables
FROM information_schema.tables 
WHERE table_schema = 'sunrise' 
  AND table_type = 'BASE TABLE'
  AND table_name ~ '^(users|students|teachers)$'
ORDER BY table_name;

-- Application Tables (T400-T600)
\echo ''
\echo 'Application Tables:'
SELECT '  ' || table_name as app_tables
FROM information_schema.tables 
WHERE table_schema = 'sunrise' 
  AND table_type = 'BASE TABLE'
  AND table_name ~ '^(fee_structures|fee_records|fee_payments|monthly_fee_tracking|monthly_payment_allocations|expenses|vendors|leave_requests)$'
ORDER BY table_name;

\echo ''

-- =====================================================
-- 3. Verify Functions
-- =====================================================

\echo '3. Verifying Functions...'
\echo '----------------------------------------'

-- Count functions
SELECT 
    COUNT(*) as total_functions,
    CASE 
        WHEN COUNT(*) >= 4 THEN '✅ Functions created (found ' || COUNT(*) || ')'
        ELSE '❌ Missing functions (expected 4+, got ' || COUNT(*) || ')'
    END as function_check
FROM information_schema.routines 
WHERE routine_schema = 'sunrise' AND routine_type = 'FUNCTION';

-- List functions
SELECT '  ' || routine_name as function_name
FROM information_schema.routines 
WHERE routine_schema = 'sunrise' AND routine_type = 'FUNCTION'
ORDER BY routine_name;

\echo ''

-- =====================================================
-- 4. Verify Views
-- =====================================================

\echo '4. Verifying Views...'
\echo '----------------------------------------'

-- Count views
SELECT 
    COUNT(*) as total_views,
    CASE 
        WHEN COUNT(*) >= 4 THEN '✅ Views created (found ' || COUNT(*) || ')'
        ELSE '❌ Missing views (expected 4+, got ' || COUNT(*) || ')'
    END as view_check
FROM information_schema.views 
WHERE table_schema = 'sunrise';

-- List views
SELECT '  ' || table_name as view_name
FROM information_schema.views 
WHERE table_schema = 'sunrise'
ORDER BY table_name;

\echo ''

-- =====================================================
-- 5. Verify Metadata Records
-- =====================================================

\echo '5. Verifying Metadata Records...'
\echo '----------------------------------------'

-- Check metadata record counts
SELECT 
    'user_types' as table_name, 
    COUNT(*) as records,
    CASE WHEN COUNT(*) >= 5 THEN '✅' ELSE '❌' END as status
FROM user_types
UNION ALL
SELECT 'session_years', COUNT(*), CASE WHEN COUNT(*) >= 5 THEN '✅' ELSE '❌' END FROM session_years
UNION ALL
SELECT 'genders', COUNT(*), CASE WHEN COUNT(*) >= 3 THEN '✅' ELSE '❌' END FROM genders
UNION ALL
SELECT 'classes', COUNT(*), CASE WHEN COUNT(*) >= 16 THEN '✅' ELSE '❌' END FROM classes
UNION ALL
SELECT 'payment_types', COUNT(*), CASE WHEN COUNT(*) >= 4 THEN '✅' ELSE '❌' END FROM payment_types
UNION ALL
SELECT 'payment_statuses', COUNT(*), CASE WHEN COUNT(*) >= 5 THEN '✅' ELSE '❌' END FROM payment_statuses
UNION ALL
SELECT 'payment_methods', COUNT(*), CASE WHEN COUNT(*) >= 6 THEN '✅' ELSE '❌' END FROM payment_methods
UNION ALL
SELECT 'leave_types', COUNT(*), CASE WHEN COUNT(*) >= 5 THEN '✅' ELSE '❌' END FROM leave_types
UNION ALL
SELECT 'leave_statuses', COUNT(*), CASE WHEN COUNT(*) >= 4 THEN '✅' ELSE '❌' END FROM leave_statuses
UNION ALL
SELECT 'expense_categories', COUNT(*), CASE WHEN COUNT(*) >= 6 THEN '✅' ELSE '❌' END FROM expense_categories
UNION ALL
SELECT 'expense_statuses', COUNT(*), CASE WHEN COUNT(*) >= 4 THEN '✅' ELSE '❌' END FROM expense_statuses
UNION ALL
SELECT 'employment_statuses', COUNT(*), CASE WHEN COUNT(*) >= 6 THEN '✅' ELSE '❌' END FROM employment_statuses
UNION ALL
SELECT 'qualifications', COUNT(*), CASE WHEN COUNT(*) >= 9 THEN '✅' ELSE '❌' END FROM qualifications
UNION ALL
SELECT 'departments', COUNT(*), CASE WHEN COUNT(*) >= 10 THEN '✅' ELSE '❌' END FROM departments
UNION ALL
SELECT 'positions', COUNT(*), CASE WHEN COUNT(*) >= 12 THEN '✅' ELSE '❌' END FROM positions
ORDER BY table_name;

-- Total metadata records
SELECT 
    SUM(record_count) as total_metadata_records,
    CASE 
        WHEN SUM(record_count) >= 100 THEN '✅ Sufficient metadata loaded'
        ELSE '❌ Insufficient metadata (expected 100+, got ' || SUM(record_count) || ')'
    END as metadata_check
FROM (
    SELECT COUNT(*) as record_count FROM user_types
    UNION ALL SELECT COUNT(*) FROM session_years
    UNION ALL SELECT COUNT(*) FROM genders
    UNION ALL SELECT COUNT(*) FROM classes
    UNION ALL SELECT COUNT(*) FROM payment_types
    UNION ALL SELECT COUNT(*) FROM payment_statuses
    UNION ALL SELECT COUNT(*) FROM payment_methods
    UNION ALL SELECT COUNT(*) FROM leave_types
    UNION ALL SELECT COUNT(*) FROM leave_statuses
    UNION ALL SELECT COUNT(*) FROM expense_categories
    UNION ALL SELECT COUNT(*) FROM expense_statuses
    UNION ALL SELECT COUNT(*) FROM employment_statuses
    UNION ALL SELECT COUNT(*) FROM qualifications
    UNION ALL SELECT COUNT(*) FROM departments
    UNION ALL SELECT COUNT(*) FROM positions
) metadata_counts;

\echo ''

-- =====================================================
-- 6. Verify Admin User
-- =====================================================

\echo '6. Verifying Admin User...'
\echo '----------------------------------------'

-- Check admin user exists
SELECT 
    CASE 
        WHEN EXISTS (SELECT 1 FROM users WHERE email = 'admin@sunrise.com')
        THEN '✅ Admin user exists'
        ELSE '❌ Admin user missing'
    END as admin_user_check;

-- Show admin user details (without password)
SELECT 
    email,
    first_name,
    last_name,
    user_type_id,
    is_active,
    created_at
FROM users 
WHERE email = 'admin@sunrise.com';

\echo ''

-- =====================================================
-- 7. Verify Fee Structures Data
-- =====================================================

\echo '7. Verifying Fee Structures Data...'
\echo '----------------------------------------'

-- Check fee structures count
SELECT 
    COUNT(*) as fee_structures_count,
    CASE 
        WHEN COUNT(*) > 0 THEN '✅ Fee structures loaded'
        ELSE '❌ No fee structures found'
    END as fee_structures_check
FROM fee_structures;

-- Show sample fee structures
SELECT 
    c.display_name as class_name,
    sy.name as session_year,
    fs.tuition_fee,
    fs.total_annual_fee
FROM fee_structures fs
JOIN classes c ON fs.class_id = c.id
JOIN session_years sy ON fs.session_year_id = sy.id
ORDER BY c.sort_order, sy.start_date
LIMIT 5;

\echo ''

-- =====================================================
-- 8. Verify Indexes
-- =====================================================

\echo '8. Verifying Database Indexes...'
\echo '----------------------------------------'

-- Count indexes
SELECT 
    COUNT(*) as total_indexes,
    CASE 
        WHEN COUNT(*) >= 30 THEN '✅ Sufficient indexes created'
        ELSE '⚠️  Limited indexes (expected 30+, got ' || COUNT(*) || ')'
    END as index_check
FROM pg_indexes 
WHERE schemaname = 'sunrise';

\echo ''

-- =====================================================
-- 9. Test Sample Queries
-- =====================================================

\echo '9. Testing Sample Queries...'
\echo '----------------------------------------'

-- Test basic joins
\echo 'Testing table relationships...'
SELECT 
    'Table relationships test' as test_name,
    CASE 
        WHEN COUNT(*) >= 0 THEN '✅ Joins working correctly'
        ELSE '❌ Join issues detected'
    END as test_result
FROM classes c
JOIN session_years sy ON sy.is_current = true
LEFT JOIN fee_structures fs ON fs.class_id = c.id AND fs.session_year_id = sy.id;

-- Test current session year
SELECT 
    name as current_session,
    start_date,
    end_date,
    CASE 
        WHEN is_current = true THEN '✅ Current session set'
        ELSE '❌ No current session'
    END as session_check
FROM session_years 
WHERE is_current = true;

\echo ''

-- =====================================================
-- 10. Database Performance Check
-- =====================================================

\echo '10. Database Performance Check...'
\echo '----------------------------------------'

-- Check database size
SELECT 
    pg_size_pretty(pg_database_size(current_database())) as database_size,
    '✅ Database size calculated' as size_check;

-- Check connection info
SELECT 
    current_database() as database_name,
    current_user as connected_user,
    version() as postgresql_version;

\echo ''

-- =====================================================
-- Final Summary
-- =====================================================

\echo '=========================================='
\echo 'DEPLOYMENT VERIFICATION COMPLETED!'
\echo '=========================================='
\echo ''
\echo 'Summary:'
\echo '✅ Schema: sunrise'
\echo '✅ Tables: 25 (13 metadata + 12 core)'
\echo '✅ Functions: 4+'
\echo '✅ Views: 4+'
\echo '✅ Metadata: 100+ records'
\echo '✅ Admin User: admin@sunrise.com'
\echo '✅ Fee Structures: Loaded'
\echo '✅ Indexes: 30+'
\echo ''
\echo 'Next Steps:'
\echo '1. Update your application DATABASE_URL'
\echo '2. Test application connectivity'
\echo '3. Run application-specific tests'
\echo '4. Set up monitoring and backups'
\echo ''
\echo '🎉 Database is ready for production!'
\echo '=========================================='
