-- =====================================================
-- V004: Remove the pre-redesign fee and transport tables (Phase 4)
-- =====================================================
-- The app now bills, collects and reports through the unified fee module
-- (V002) and the transport operations module (V003). The old tables are not
-- migrated (decision 1). Sunrise's old transport price list was already
-- carried over as transport_rates by V003.
--
-- 1. Refuses to run while an old payment table still holds payments, so real
--    money records are never dropped by accident. Delete them by hand first if
--    they are only test data.
-- 2. Drops the functions that only served the old tables.
-- 3. Drops the 13 old tables (their id sequences go with them).
--
-- Kept: calculate_sibling_fee_waiver and get_waiver_reason_text (used by the
-- student sibling code), and payment_types (a shared system list).
-- =====================================================

-- 1. Guard
DO $$
DECLARE
    fee_count BIGINT;
    transport_count BIGINT;
BEGIN
    SELECT COUNT(*) INTO fee_count FROM fee_payments;
    SELECT COUNT(*) INTO transport_count FROM transport_payments;
    IF fee_count > 0 OR transport_count > 0 THEN
        RAISE EXCEPTION 'Old payment tables still hold payments (fee_payments: %, transport_payments: %). '
                        'Remove them by hand if they are test data, then run this migration again.',
                        fee_count, transport_count;
    END IF;
END $$;

-- 2. Functions of the old fee and transport code (by name, whatever their arguments)
DROP TRIGGER IF EXISTS trg_calculate_fee_balance ON fee_records;
DO $$
DECLARE
    f RECORD;
BEGIN
    FOR f IN
        SELECT p.oid::regprocedure AS signature
        FROM pg_proc p JOIN pg_namespace n ON n.oid = p.pronamespace
        WHERE n.nspname = current_schema()
          AND p.proname IN ('enable_monthly_tracking_complete', 'enable_transport_monthly_tracking',
                            'calculate_fee_balance')
    LOOP
        EXECUTE 'DROP FUNCTION ' || f.signature;
    END LOOP;
END $$;

-- 3. Tables (one statement, so their foreign keys to each other do not matter)
DROP TABLE
    transport_payment_allocations,
    transport_payments,
    transport_monthly_tracking,
    student_transport_enrollment,
    transport_distance_slabs,
    transport_type_pricing,
    legacy_transport_types,
    monthly_payment_allocations,
    monthly_fee_tracking,
    fee_payment_audit_log,
    fee_payments,
    fee_records,
    legacy_fee_structures;
