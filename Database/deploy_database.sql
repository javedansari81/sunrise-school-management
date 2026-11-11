-- =====================================================
-- Master deployment script: School Management System (multi-tenant baseline)
-- =====================================================
-- Deploys the complete schema in dependency order. This file is the single
-- list of deployment scripts, used by:
--
--   * redeploy_database.py (repository root): drops the schema named by
--     DB_SCHEMA in sunrise-backend-fastapi/.env and runs every \ir file
--     below inside one transaction. Other schemas in the database are untouched.
--   * psql:  psql "<database url>" -v schema=school -f Database/deploy_database.sql
--
-- All scripts use unqualified names; the schema is chosen here, never inside
-- a script, and the database-wide search_path is never changed.
--
-- Adding a table, function, view or data script: add an \ir line for it.
-- Changing an existing database: add a migration to Database/Versioning/.
-- =====================================================

\set ON_ERROR_STOP on
\if :{?schema}
\else
    \set schema school
\endif

CREATE SCHEMA IF NOT EXISTS :"schema";
SET search_path TO :"schema";

\echo 'Deploying into schema' :schema

-- =====================================================
-- STEP 1: Schema bookkeeping
-- =====================================================
\echo 'STEP 1: Schema bookkeeping'
\ir Schema/00_create_schema.sql

-- =====================================================
-- STEP 2: Tenants (T010-T020)
-- =====================================================
\echo 'STEP 2: Tenants (T010-T020)'
\ir Tables/T010_schools.sql
\ir Tables/T020_school_settings.sql

-- =====================================================
-- STEP 3: Lookup tables (T100-T297)
-- =====================================================
\echo 'STEP 3: Lookup tables (T100-T297)'
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
\ir Tables/T265_inventory_item_category.sql
\ir Tables/T270_inventory_item_types.sql
\ir Tables/T280_inventory_size_types.sql
\ir Tables/T290_attendance_statuses.sql
\ir Tables/T295_attendance_periods.sql
\ir Tables/T297_progression_actions.sql

-- =====================================================
-- STEP 4: Core tables (T300-T320)
-- =====================================================
\echo 'STEP 4: Core tables (T300-T320)'
\ir Tables/T300_users.sql
\ir Tables/T310_students.sql
\ir Tables/T315_student_siblings.sql
\ir Tables/T316_student_session_history.sql
\ir Tables/T320_teachers.sql

-- =====================================================
-- STEP 5: Unified fee module (T900-T950)
-- =====================================================
\echo 'STEP 5: Unified fee module (T900-T950)'
\ir Tables/T900_fee_heads.sql
\ir Tables/T905_fee_structures.sql
\ir Tables/T910_fee_structure_items.sql
\ir Tables/T915_concession_rules.sql
\ir Tables/T920_student_fee_plans.sql
\ir Tables/T925_student_concessions.sql
\ir Tables/T930_student_dues.sql
\ir Tables/T935_receipt_sequences.sql
\ir Tables/T940_payments.sql
\ir Tables/T945_payment_allocations.sql
\ir Tables/T950_fee_audit_log.sql

-- =====================================================
-- STEP 5b: Transport operations module (T960-T985)
-- =====================================================
\echo 'STEP 5b: Transport operations module (T960-T985)'
\ir Tables/T960_transport_types.sql
\ir Tables/T965_vehicles.sql
\ir Tables/T970_routes.sql
\ir Tables/T972_route_stops.sql
\ir Tables/T975_transport_rates.sql
\ir Tables/T980_student_transport_assignments.sql
\ir Tables/T985_transport_assignment_pauses.sql

-- =====================================================
-- STEP 6: Expense and leave tables (T500-T600)
-- =====================================================
\echo 'STEP 6: Expense and leave tables (T500-T600)'
\ir Tables/T500_expenses.sql
\ir Tables/T510_vendors.sql
\ir Tables/T600_leave_requests.sql

-- =====================================================
-- STEP 7: Gallery and inventory tables (T700-T750)
-- =====================================================
\echo 'STEP 7: Gallery and inventory tables (T700-T750)'
\ir Tables/T700_gallery_categories.sql
\ir Tables/T700_inventory_pricing.sql
\ir Tables/T710_gallery_images.sql
\ir Tables/T710_inventory_purchases.sql
\ir Tables/T720_inventory_purchase_items.sql
\ir Tables/T730_inventory_stock.sql
\ir Tables/T740_inventory_stock_procurements.sql
\ir Tables/T750_inventory_stock_procurement_items.sql

-- =====================================================
-- STEP 8: Attendance and alert tables (T800-T810)
-- =====================================================
\echo 'STEP 8: Attendance and alert tables (T800-T810)'
\ir Tables/T800_alert_types.sql
\ir Tables/T800_attendance_records.sql
\ir Tables/T805_alert_statuses.sql
\ir Tables/T810_alerts.sql

-- =====================================================
-- STEP 9: Functions
-- =====================================================
\echo 'STEP 9: Functions'
\ir Functions/F140_calculate_sibling_waiver.sql

-- =====================================================
-- STEP 10: Default school (Sunrise, school 1) and reference data
-- =====================================================
\echo 'STEP 10: Default school (Sunrise, school 1) and reference data'
\ir Init/00_create_default_school.sql
\ir Init/01_load_metadata.sql
\ir DataLoads/D800_alert_types.sql
\ir DataLoads/DL105_reversal_reasons.sql
\ir DataLoads/DL265_inventory_item_category.sql
\ir DataLoads/DL270_inventory_item_types.sql
\ir DataLoads/DL271_inventory_books_notebooks_stationery.sql
\ir DataLoads/DL280_inventory_size_types.sql
\ir DataLoads/DL290_attendance_statuses.sql
\ir DataLoads/DL295_attendance_periods.sql
\ir DataLoads/DL701_gallery_categories.sql
\ir Init/02_create_admin_user.sql
\ir Init/03_create_super_admin_user.sql
\ir Init/04_fee_module_defaults.sql
\ir Init/05_transport_defaults.sql
\ir Init/07_inventory_stock.sql
\ir Init/99_finish_default_school.sql

\echo 'DEPLOYMENT SUCCESSFUL'
