-- =====================================================
-- Version: V020
-- Description: Add new alert types for Inventory Management and Expense Management
-- Date: 2025-12-12
-- Author: System
-- Dependencies: T800_alert_types.sql
-- =====================================================

-- Add new Inventory Management alert types (50-59)
-- Using conditional update to only modify records when values actually change
INSERT INTO alert_types (id, name, description, category, icon, color_code, priority_level, default_expiry_days, requires_acknowledgment) VALUES
(51, 'INVENTORY_PURCHASE_CREATED', 'Inventory purchase recorded', 'ADMINISTRATIVE', 'ShoppingCart', '#4CAF50', 2, 30, FALSE),
(52, 'INVENTORY_STOCK_PROCURED', 'Inventory stock procured', 'ADMINISTRATIVE', 'LocalShipping', '#2196F3', 2, 30, FALSE)
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

-- Add new Expense Management alert types (60-69)
-- Using conditional update to only modify records when values actually change
INSERT INTO alert_types (id, name, description, category, icon, color_code, priority_level, default_expiry_days, requires_acknowledgment) VALUES
(60, 'EXPENSE_CREATED', 'New expense created', 'FINANCIAL', 'Receipt', '#2196F3', 2, 30, FALSE),
(61, 'EXPENSE_APPROVED', 'Expense approved', 'FINANCIAL', 'CheckCircle', '#4CAF50', 2, 30, FALSE),
(62, 'EXPENSE_REJECTED', 'Expense rejected', 'FINANCIAL', 'Cancel', '#F44336', 3, 30, FALSE),
(63, 'EXPENSE_PAID', 'Expense marked as paid', 'FINANCIAL', 'AccountBalanceWallet', '#4CAF50', 2, 30, FALSE)
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

-- Verification with detailed reporting
DO $$
DECLARE
    inventory_count INTEGER;
    expense_count INTEGER;
    alert_record RECORD;
    records_inserted INTEGER := 0;
    records_updated INTEGER := 0;
    records_unchanged INTEGER := 0;
BEGIN
    -- Check Inventory alert types
    SELECT COUNT(*) INTO inventory_count
    FROM alert_types
    WHERE id IN (51, 52);

    -- Check Expense Management alert types
    SELECT COUNT(*) INTO expense_count
    FROM alert_types
    WHERE id IN (60, 61, 62, 63);

    IF inventory_count = 2 THEN
        RAISE NOTICE '✅ Verification: 2 Inventory Management alert types present';
    ELSE
        RAISE WARNING '❌ Verification failed: Expected 2 Inventory alert types, found %', inventory_count;
    END IF;

    IF expense_count = 4 THEN
        RAISE NOTICE '✅ Verification: 4 Expense Management alert types present';
    ELSE
        RAISE WARNING '❌ Verification failed: Expected 4 Expense alert types, found %', expense_count;
    END IF;

    RAISE NOTICE 'ℹ️ Total alert types verified: %', inventory_count + expense_count;
    RAISE NOTICE '';
    RAISE NOTICE '📊 Update Summary:';
    RAISE NOTICE '  - Records with actual changes will have updated_at timestamp modified';
    RAISE NOTICE '  - Records with no changes will retain original updated_at timestamp';
    RAISE NOTICE '  - This ensures minimal database writes and accurate change tracking';
END $$;

-- Display newly added alert types
DO $$
DECLARE
    alert_record RECORD;
BEGIN
    RAISE NOTICE '📋 Newly Added Alert Types:';
    RAISE NOTICE '================================';
    
    FOR alert_record IN 
        SELECT id, name, description, category, priority_level
        FROM alert_types
        WHERE id IN (51, 52, 60, 61, 62, 63)
        ORDER BY id
    LOOP
        RAISE NOTICE 'ID: % | Name: % | Category: % | Priority: %', 
            alert_record.id, 
            alert_record.name, 
            alert_record.category,
            alert_record.priority_level;
    END LOOP;
    
    RAISE NOTICE '================================';
END $$;

