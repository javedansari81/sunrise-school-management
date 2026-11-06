-- =====================================================
-- Master Deployment Script for Sunrise School Management System
-- =====================================================
-- Deploys the complete database in dependency order.
--
-- This file is the single list of deployment scripts. It is used by:
--   * psql:  psql -U sunrise_user -d sunrise_school_db -f Database/deploy_database.sql
--   * redeploy_database.py (repository root), which drops the sunrise schema and
--     runs every \ir file below inside one transaction.
--
-- When you add a table, function, view or data script, add it here.
-- When a Versioning migration is not yet reflected in the Tables/ scripts, add
-- it to STEP 12 so fresh deployments match migrated databases.
--
-- PREREQUISITES:
-- 1. PostgreSQL database 'sunrise_school_db' must exist
-- 2. User 'sunrise_user' must exist with proper permissions
-- =====================================================

\echo '=========================================='
\echo 'SUNRISE SCHOOL MANAGEMENT SYSTEM'
\echo 'Database Deployment Script'
\echo '=========================================='
\echo ''

-- =====================================================
-- STEP 1: Schema Initialization
-- =====================================================

\echo 'STEP 1: Schema Initialization'
\ir Schema/00_create_schema.sql
\echo ''

-- =====================================================
-- STEP 2: Metadata and Lookup Tables (T100-T297)
-- =====================================================

\echo 'STEP 2: Metadata and Lookup Tables (T100-T297)'
\ir Tables/T100_user_types.sql
\ir Tables/T105_reversal_reasons.sql
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
\ir Tables/T230_departments.sql
\ir Tables/T240_positions.sql
\ir Tables/T250_transport_types.sql
\ir Tables/T255_transport_type_pricing.sql
\ir Tables/T260_transport_distance_slabs.sql
\ir Tables/T265_inventory_item_category.sql
\ir Tables/T270_inventory_item_types.sql
\ir Tables/T280_inventory_size_types.sql
\ir Tables/T290_attendance_statuses.sql
\ir Tables/T295_attendance_periods.sql
\ir Tables/T297_progression_actions.sql
\echo ''

-- =====================================================
-- STEP 3: Core Tables (T300-T320)
-- =====================================================

\echo 'STEP 3: Core Tables (T300-T320)'
\ir Tables/T300_users.sql
\ir Tables/T310_students.sql
\ir Tables/T315_student_siblings.sql
\ir Tables/T316_student_session_history.sql
\ir Tables/T320_teachers.sql
\echo ''

-- =====================================================
-- STEP 4: Fee and Transport Tables (T400-T470)
-- =====================================================

\echo 'STEP 4: Fee and Transport Tables (T400-T470)'
\ir Tables/T400_fee_structures.sql
\ir Tables/T410_fee_records.sql
\ir Tables/T415_fee_payments.sql
\ir Tables/T416_fee_payment_audit_log.sql
\ir Tables/T420_monthly_fee_tracking.sql
\ir Tables/T430_monthly_payment_allocations.sql
\ir Tables/T440_student_transport_enrollment.sql
\ir Tables/T450_transport_monthly_tracking.sql
\ir Tables/T460_transport_payments.sql
\ir Tables/T470_transport_payment_allocations.sql
\echo ''

-- =====================================================
-- STEP 5: Expense and Leave Tables (T500-T600)
-- =====================================================

\echo 'STEP 5: Expense and Leave Tables (T500-T600)'
\ir Tables/T500_expenses.sql
\ir Tables/T510_vendors.sql
\ir Tables/T600_leave_requests.sql
\echo ''

-- =====================================================
-- STEP 6: Gallery and Inventory Tables (T700-T750)
-- =====================================================

\echo 'STEP 6: Gallery and Inventory Tables (T700-T750)'
\ir Tables/T700_gallery_categories.sql
\ir Tables/T700_inventory_pricing.sql
\ir Tables/T710_gallery_images.sql
\ir Tables/T710_inventory_purchases.sql
\ir Tables/T720_inventory_purchase_items.sql
\ir Tables/T730_inventory_stock.sql
\ir Tables/T740_inventory_stock_procurements.sql
\ir Tables/T750_inventory_stock_procurement_items.sql
\echo ''

-- =====================================================
-- STEP 7: Attendance and Alert Tables (T800-T810)
-- =====================================================

\echo 'STEP 7: Attendance and Alert Tables (T800-T810)'
\ir Tables/T800_alert_types.sql
\ir Tables/T800_attendance_records.sql
\ir Tables/T805_alert_statuses.sql
\ir Tables/T810_alerts.sql
\echo ''

-- =====================================================
-- STEP 8: Functions
-- =====================================================

\echo 'STEP 8: Functions'
\ir Functions/F100_calculate_age.sql
\ir Functions/F110_get_academic_year.sql
\ir Functions/F120_calculate_fee_balance.sql
\ir Functions/F130_enable_monthly_tracking_complete.sql
\ir Functions/F140_calculate_sibling_waiver.sql
\ir Functions/F140_enable_transport_monthly_tracking.sql
\echo ''

-- =====================================================
-- STEP 9: Views
-- =====================================================

\echo 'STEP 9: Views'
\ir Views/V100_student_summary.sql
\ir Views/V110_teacher_summary.sql
\ir Views/V120_fee_collection_summary.sql
\ir Views/V130_enhanced_student_fee_status.sql
\ir Views/V140_enhanced_student_transport_status.sql
\echo ''

-- =====================================================
-- STEP 10: Metadata and Reference Data
-- =====================================================

\echo 'STEP 10: Metadata and Reference Data'
\ir Init/01_load_metadata.sql
\ir DataLoads/D800_alert_types.sql
\ir DataLoads/DL105_reversal_reasons.sql
\ir DataLoads/DL251_transport_types.sql
\ir DataLoads/DL255_transport_type_pricing.sql
\ir DataLoads/DL261_transport_distance_slabs.sql
\ir DataLoads/DL265_inventory_item_category.sql
\ir DataLoads/DL270_inventory_item_types.sql
\ir DataLoads/DL271_inventory_books_notebooks_stationery.sql
\ir DataLoads/DL280_inventory_size_types.sql
\ir DataLoads/DL290_attendance_statuses.sql
\ir DataLoads/DL295_attendance_periods.sql
\ir DataLoads/DL701_gallery_categories.sql
\echo ''

-- =====================================================
-- STEP 11: Admin Users and Initial Data
-- =====================================================

\echo 'STEP 11: Admin Users and Initial Data'
\ir Init/02_create_admin_user.sql
\ir Init/03_create_super_admin_user.sql
\ir Init/03_fee_structures_data.sql
\ir Init/07_inventory_stock.sql
\echo ''

-- =====================================================
-- STEP 12: Migrations not yet folded into the table scripts
-- =====================================================

\echo 'STEP 12: Migrations not yet folded into the table scripts'
\ir Versioning/V033_add_parent_called_fields_to_attendance.sql
\ir Versioning/V034_normalize_inventory_categories.sql
\echo ''

-- =====================================================
-- STEP 13: Multi-tenancy (schools + school_id)
-- =====================================================

\echo 'STEP 13: Multi-tenancy (schools + school_id)'
\ir Versioning/V036_add_schools_and_tenant_columns.sql
\echo ''

\echo '=========================================='
\echo 'DEPLOYMENT SUCCESSFUL!'
\echo '=========================================='
\echo 'Admin login: see Init/02_create_admin_user.sql'
