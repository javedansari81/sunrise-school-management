-- =====================================================
-- Version: V027
-- Description: Add COMBINED_PAYMENT_RECEIVED alert type for combined tuition + transport fee payments
-- Date: 2026-01-30
-- Author: System
-- Dependencies: T800_alert_types.sql
-- =====================================================

-- Add new COMBINED_PAYMENT_RECEIVED alert type (id=13)
-- This alert is triggered when an admin processes a combined payment
-- that includes both tuition fee and transport fee in a single transaction
INSERT INTO alert_types (id, name, description, category, icon, color_code, priority_level, default_expiry_days, requires_acknowledgment) VALUES
(13, 'COMBINED_PAYMENT_RECEIVED', 'Combined tuition and transport fee payment processed', 'FINANCIAL', 'Payments', '#4CAF50', 2, 30, FALSE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    category = EXCLUDED.category,
    icon = EXCLUDED.icon,
    color_code = EXCLUDED.color_code,
    priority_level = EXCLUDED.priority_level,
    default_expiry_days = EXCLUDED.default_expiry_days,
    requires_acknowledgment = EXCLUDED.requires_acknowledgment,
    updated_at = NOW()
WHERE
    alert_types.name IS DISTINCT FROM EXCLUDED.name OR
    alert_types.description IS DISTINCT FROM EXCLUDED.description OR
    alert_types.category IS DISTINCT FROM EXCLUDED.category OR
    alert_types.icon IS DISTINCT FROM EXCLUDED.icon OR
    alert_types.color_code IS DISTINCT FROM EXCLUDED.color_code OR
    alert_types.priority_level IS DISTINCT FROM EXCLUDED.priority_level OR
    alert_types.default_expiry_days IS DISTINCT FROM EXCLUDED.default_expiry_days OR
    alert_types.requires_acknowledgment IS DISTINCT FROM EXCLUDED.requires_acknowledgment;

-- Verification
DO $$
DECLARE
    combined_payment_exists BOOLEAN;
    alert_record RECORD;
BEGIN
    -- Check if COMBINED_PAYMENT_RECEIVED alert type exists
    SELECT EXISTS(
        SELECT 1 FROM alert_types WHERE id = 13 AND name = 'COMBINED_PAYMENT_RECEIVED'
    ) INTO combined_payment_exists;

    IF combined_payment_exists THEN
        RAISE NOTICE '✅ Verification: COMBINED_PAYMENT_RECEIVED alert type (id=13) present';
    ELSE
        RAISE WARNING '❌ Verification failed: COMBINED_PAYMENT_RECEIVED alert type not found';
    END IF;

    -- Display the alert type details
    RAISE NOTICE '';
    RAISE NOTICE '📋 COMBINED_PAYMENT_RECEIVED Alert Type Details:';
    RAISE NOTICE '================================================';
    
    FOR alert_record IN 
        SELECT id, name, description, category, icon, color_code, priority_level
        FROM alert_types
        WHERE id = 13
    LOOP
        RAISE NOTICE 'ID: %', alert_record.id;
        RAISE NOTICE 'Name: %', alert_record.name;
        RAISE NOTICE 'Description: %', alert_record.description;
        RAISE NOTICE 'Category: %', alert_record.category;
        RAISE NOTICE 'Icon: %', alert_record.icon;
        RAISE NOTICE 'Color Code: %', alert_record.color_code;
        RAISE NOTICE 'Priority Level: %', alert_record.priority_level;
    END LOOP;
    
    RAISE NOTICE '================================================';
END $$;

