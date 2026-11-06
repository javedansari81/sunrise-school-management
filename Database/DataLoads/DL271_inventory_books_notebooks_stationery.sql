-- =====================================================
-- Data Load: Inventory Books, Notebooks, and Stationery
-- Description: Load Books, Notebooks, and Stationery items for each class
-- Dependencies: T270_inventory_item_types.sql
-- =====================================================

-- =====================================================
-- BOOKS - One for each class from PG to Class 8
-- =====================================================
INSERT INTO inventory_item_types (id, name, description, inventory_item_category_id, is_active) VALUES
-- PG to UKG
(100, 'BOOKS_PG', 'PG Books', 3, TRUE),
(101, 'BOOKS_LKG', 'LKG Books', 3, TRUE),
(102, 'BOOKS_UKG', 'UKG Books', 3, TRUE),
-- Class 1 to Class 8
(103, 'BOOKS_CLASS_1', 'Class 1 Books', 3, TRUE),
(104, 'BOOKS_CLASS_2', 'Class 2 Books', 3, TRUE),
(105, 'BOOKS_CLASS_3', 'Class 3 Books', 3, TRUE),
(106, 'BOOKS_CLASS_4', 'Class 4 Books', 3, TRUE),
(107, 'BOOKS_CLASS_5', 'Class 5 Books', 3, TRUE),
(108, 'BOOKS_CLASS_6', 'Class 6 Books', 3, TRUE),
(109, 'BOOKS_CLASS_7', 'Class 7 Books', 3, TRUE),
(110, 'BOOKS_CLASS_8', 'Class 8 Books', 3, TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    inventory_item_category_id = EXCLUDED.inventory_item_category_id,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- NOTEBOOKS - One for each class from PG to Class 8
-- =====================================================
INSERT INTO inventory_item_types (id, name, description, inventory_item_category_id, is_active) VALUES
-- PG to UKG
(200, 'NOTEBOOKS_PG', 'PG Notebooks', 4, TRUE),
(201, 'NOTEBOOKS_LKG', 'LKG Notebooks', 4, TRUE),
(202, 'NOTEBOOKS_UKG', 'UKG Notebooks', 4, TRUE),
-- Class 1 to Class 8
(203, 'NOTEBOOKS_CLASS_1', 'Class 1 Notebooks', 4, TRUE),
(204, 'NOTEBOOKS_CLASS_2', 'Class 2 Notebooks', 4, TRUE),
(205, 'NOTEBOOKS_CLASS_3', 'Class 3 Notebooks', 4, TRUE),
(206, 'NOTEBOOKS_CLASS_4', 'Class 4 Notebooks', 4, TRUE),
(207, 'NOTEBOOKS_CLASS_5', 'Class 5 Notebooks', 4, TRUE),
(208, 'NOTEBOOKS_CLASS_6', 'Class 6 Notebooks', 4, TRUE),
(209, 'NOTEBOOKS_CLASS_7', 'Class 7 Notebooks', 4, TRUE),
(210, 'NOTEBOOKS_CLASS_8', 'Class 8 Notebooks', 4, TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    inventory_item_category_id = EXCLUDED.inventory_item_category_id,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- STATIONERY - Only for PG, LKG, and UKG
-- =====================================================
INSERT INTO inventory_item_types (id, name, description, inventory_item_category_id, is_active) VALUES
(300, 'STATIONERY_PG', 'PG Stationery', 5, TRUE),
(301, 'STATIONERY_LKG', 'LKG Stationery', 5, TRUE),
(302, 'STATIONERY_UKG', 'UKG Stationery', 5, TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    inventory_item_category_id = EXCLUDED.inventory_item_category_id,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- =====================================================
-- INDIVIDUAL NOTEBOOK - For buying 1-2 notebooks individually
-- =====================================================
INSERT INTO inventory_item_types (id, name, description, inventory_item_category_id, is_active) VALUES
(211, 'NOTEBOOK_INDIVIDUAL', 'Notebook (Individual)', 4, TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    inventory_item_category_id = EXCLUDED.inventory_item_category_id,
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
INSERT INTO inventory_item_types (id, name, description, inventory_item_category_id, is_active) VALUES
(9, 'WHITE_PANT', 'White Pant (Individual)', 1, TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    inventory_item_category_id = EXCLUDED.inventory_item_category_id,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- Verification message
DO $$
DECLARE
    total_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO total_count
    FROM inventory_item_types
    WHERE inventory_item_category_id IN (3, 4, 5);  -- BOOKS, NOTEBOOKS, STATIONERY

    RAISE NOTICE 'Total Books, Notebooks, and Stationery items: %', total_count;
    RAISE NOTICE 'Blue Pant and White Pant items updated';
END $$;

