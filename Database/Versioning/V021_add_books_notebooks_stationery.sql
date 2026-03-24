-- =====================================================
-- Version: V021
-- Description: Add Books, Notebooks, and Stationery items for each class (PG to Class 8)
-- Date: 2026-03-24
-- Author: System
-- Dependencies: T270_inventory_item_types.sql
-- =====================================================

-- Add Books for each class (IDs: 100-110)
-- Add Notebooks for each class (IDs: 200-210)
-- Add Stationery for each class (IDs: 300-302)

BEGIN;

-- =====================================================
-- BOOKS - One for each class from PG to Class 8
-- =====================================================
INSERT INTO inventory_item_types (id, name, description, category, is_active) VALUES
-- PG to UKG
(100, 'BOOKS_PG', 'PG Books', 'BOOKS', TRUE),
(101, 'BOOKS_LKG', 'LKG Books', 'BOOKS', TRUE),
(102, 'BOOKS_UKG', 'UKG Books', 'BOOKS', TRUE),
-- Class 1 to Class 8
(103, 'BOOKS_CLASS_1', 'Class 1 Books', 'BOOKS', TRUE),
(104, 'BOOKS_CLASS_2', 'Class 2 Books', 'BOOKS', TRUE),
(105, 'BOOKS_CLASS_3', 'Class 3 Books', 'BOOKS', TRUE),
(106, 'BOOKS_CLASS_4', 'Class 4 Books', 'BOOKS', TRUE),
(107, 'BOOKS_CLASS_5', 'Class 5 Books', 'BOOKS', TRUE),
(108, 'BOOKS_CLASS_6', 'Class 6 Books', 'BOOKS', TRUE),
(109, 'BOOKS_CLASS_7', 'Class 7 Books', 'BOOKS', TRUE),
(110, 'BOOKS_CLASS_8', 'Class 8 Books', 'BOOKS', TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    category = EXCLUDED.category,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- NOTEBOOKS - One for each class from PG to Class 8
-- =====================================================
INSERT INTO inventory_item_types (id, name, description, category, is_active) VALUES
-- PG to UKG
(200, 'NOTEBOOKS_PG', 'PG Notebooks', 'NOTEBOOKS', TRUE),
(201, 'NOTEBOOKS_LKG', 'LKG Notebooks', 'NOTEBOOKS', TRUE),
(202, 'NOTEBOOKS_UKG', 'UKG Notebooks', 'NOTEBOOKS', TRUE),
-- Class 1 to Class 8
(203, 'NOTEBOOKS_CLASS_1', 'Class 1 Notebooks', 'NOTEBOOKS', TRUE),
(204, 'NOTEBOOKS_CLASS_2', 'Class 2 Notebooks', 'NOTEBOOKS', TRUE),
(205, 'NOTEBOOKS_CLASS_3', 'Class 3 Notebooks', 'NOTEBOOKS', TRUE),
(206, 'NOTEBOOKS_CLASS_4', 'Class 4 Notebooks', 'NOTEBOOKS', TRUE),
(207, 'NOTEBOOKS_CLASS_5', 'Class 5 Notebooks', 'NOTEBOOKS', TRUE),
(208, 'NOTEBOOKS_CLASS_6', 'Class 6 Notebooks', 'NOTEBOOKS', TRUE),
(209, 'NOTEBOOKS_CLASS_7', 'Class 7 Notebooks', 'NOTEBOOKS', TRUE),
(210, 'NOTEBOOKS_CLASS_8', 'Class 8 Notebooks', 'NOTEBOOKS', TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    category = EXCLUDED.category,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- STATIONERY - Only for PG, LKG, and UKG
-- =====================================================
INSERT INTO inventory_item_types (id, name, description, category, is_active) VALUES
(300, 'STATIONERY_PG', 'PG Stationery', 'STATIONERY', TRUE),
(301, 'STATIONERY_LKG', 'LKG Stationery', 'STATIONERY', TRUE),
(302, 'STATIONERY_UKG', 'UKG Stationery', 'STATIONERY', TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    category = EXCLUDED.category,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- INDIVIDUAL NOTEBOOK - For buying 1-2 notebooks individually
-- =====================================================
INSERT INTO inventory_item_types (id, name, description, category, is_active) VALUES
(211, 'NOTEBOOK_INDIVIDUAL', 'Notebook (Individual)', 'NOTEBOOKS', TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    category = EXCLUDED.category,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- UPDATE PANT ITEMS - Change existing Pant to Blue Pant and add White Pant
-- =====================================================
-- Update existing Pant (ID: 5) to Blue Pant
UPDATE inventory_item_types
SET name = 'BLUE_PANT',
    description = 'Blue Pant (Individual)',
    updated_at = NOW()
WHERE id = 5;

-- Add White Pant
INSERT INTO inventory_item_types (id, name, description, category, is_active) VALUES
(9, 'WHITE_PANT', 'White Pant (Individual)', 'UNIFORM', TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    category = EXCLUDED.category,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- Verification
-- =====================================================
DO $$
DECLARE
    books_count INTEGER;
    notebooks_count INTEGER;
    stationery_count INTEGER;
    individual_notebook_exists BOOLEAN;
    blue_pant_exists BOOLEAN;
    white_pant_exists BOOLEAN;
BEGIN
    -- Check Books
    SELECT COUNT(*) INTO books_count
    FROM inventory_item_types
    WHERE id BETWEEN 100 AND 110 AND category = 'BOOKS';

    -- Check Notebooks (including individual)
    SELECT COUNT(*) INTO notebooks_count
    FROM inventory_item_types
    WHERE (id BETWEEN 200 AND 210 OR id = 211) AND category = 'NOTEBOOKS';

    -- Check Stationery
    SELECT COUNT(*) INTO stationery_count
    FROM inventory_item_types
    WHERE id BETWEEN 300 AND 302 AND category = 'STATIONERY';

    -- Check Individual Notebook
    SELECT EXISTS(SELECT 1 FROM inventory_item_types WHERE id = 211) INTO individual_notebook_exists;

    -- Check Blue Pant
    SELECT EXISTS(SELECT 1 FROM inventory_item_types WHERE id = 5 AND name = 'BLUE_PANT') INTO blue_pant_exists;

    -- Check White Pant
    SELECT EXISTS(SELECT 1 FROM inventory_item_types WHERE id = 9) INTO white_pant_exists;

    IF books_count = 11 THEN
        RAISE NOTICE '✅ Verification: 11 Books items added (PG to Class 8)';
    ELSE
        RAISE WARNING '❌ Verification failed: Expected 11 Books items, found %', books_count;
    END IF;

    IF notebooks_count = 12 THEN
        RAISE NOTICE '✅ Verification: 12 Notebooks items added (PG to Class 8 + Individual)';
    ELSE
        RAISE WARNING '❌ Verification failed: Expected 12 Notebooks items, found %', notebooks_count;
    END IF;

    IF stationery_count = 3 THEN
        RAISE NOTICE '✅ Verification: 3 Stationery items added (PG, LKG, UKG)';
    ELSE
        RAISE WARNING '❌ Verification failed: Expected 3 Stationery items, found %', stationery_count;
    END IF;

    IF individual_notebook_exists THEN
        RAISE NOTICE '✅ Verification: Individual Notebook item added';
    ELSE
        RAISE WARNING '❌ Verification failed: Individual Notebook not found';
    END IF;

    IF blue_pant_exists THEN
        RAISE NOTICE '✅ Verification: Pant updated to Blue Pant';
    ELSE
        RAISE WARNING '❌ Verification failed: Blue Pant not found';
    END IF;

    IF white_pant_exists THEN
        RAISE NOTICE '✅ Verification: White Pant added';
    ELSE
        RAISE WARNING '❌ Verification failed: White Pant not found';
    END IF;

    RAISE NOTICE '✅ Total new inventory items added: %', (books_count + notebooks_count + stationery_count);
END $$;

COMMIT;

-- Display summary
SELECT 
    category,
    COUNT(*) as item_count,
    STRING_AGG(description, ', ' ORDER BY id) as items
FROM inventory_item_types
WHERE category IN ('BOOKS', 'NOTEBOOKS', 'STATIONERY')
GROUP BY category
ORDER BY category;

