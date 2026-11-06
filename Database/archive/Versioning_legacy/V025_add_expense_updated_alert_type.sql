-- =====================================================
-- Version: V025
-- Description: Add EXPENSE_UPDATED alert type for expense update notifications
-- Date: 2026-01-09
-- Author: System
-- Dependencies: T800_alert_types.sql
-- =====================================================

-- Add new EXPENSE_UPDATED alert type (id=64)
-- This alert is triggered when an admin updates a pending expense
-- Notification is sent to SUPER_ADMIN users for approval workflow
INSERT INTO alert_types (id, name, description, category, icon, color_code, priority_level, default_expiry_days, requires_acknowledgment) VALUES
(64, 'EXPENSE_UPDATED', 'Expense has been updated', 'FINANCIAL', 'Edit', '#FF9800', 2, 30, FALSE)
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
    expense_updated_exists BOOLEAN;
    alert_record RECORD;
BEGIN
    -- Check if EXPENSE_UPDATED alert type exists
    SELECT EXISTS(
        SELECT 1 FROM alert_types WHERE id = 64 AND name = 'EXPENSE_UPDATED'
    ) INTO expense_updated_exists;

    IF expense_updated_exists THEN
        RAISE NOTICE '✅ Verification: EXPENSE_UPDATED alert type (id=64) present';
    ELSE
        RAISE WARNING '❌ Verification failed: EXPENSE_UPDATED alert type not found';
    END IF;

    -- Display the alert type details
    RAISE NOTICE '';
    RAISE NOTICE '📋 EXPENSE_UPDATED Alert Type Details:';
    RAISE NOTICE '=====================================';
    
    FOR alert_record IN 
        SELECT id, name, description, category, icon, color_code, priority_level
        FROM alert_types
        WHERE id = 64
    LOOP
        RAISE NOTICE 'ID: %', alert_record.id;
        RAISE NOTICE 'Name: %', alert_record.name;
        RAISE NOTICE 'Description: %', alert_record.description;
        RAISE NOTICE 'Category: %', alert_record.category;
        RAISE NOTICE 'Icon: %', alert_record.icon;
        RAISE NOTICE 'Color Code: %', alert_record.color_code;
        RAISE NOTICE 'Priority Level: %', alert_record.priority_level;
    END LOOP;
    
    RAISE NOTICE '=====================================';
END $$;

