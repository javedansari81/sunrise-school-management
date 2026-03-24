-- =====================================================
-- Migration: V034 - Normalize Inventory Categories
-- Description: Replace string category column with foreign key to inventory_item_category table
-- Dependencies: T265_inventory_item_category.sql, DL265_inventory_item_category.sql
-- =====================================================

-- Step 1: Add new inventory_item_category_id column (nullable initially)
ALTER TABLE inventory_item_types
ADD COLUMN inventory_item_category_id INTEGER;

-- Step 2: Migrate existing category data to new column
-- Map string categories to their corresponding IDs
UPDATE inventory_item_types
SET inventory_item_category_id = CASE
    WHEN category = 'UNIFORM' THEN 1
    WHEN category = 'ACCESSORY' THEN 2
    WHEN category = 'BOOKS' THEN 3
    WHEN category = 'NOTEBOOKS' THEN 4
    WHEN category = 'STATIONERY' THEN 5
    ELSE NULL
END;

-- Step 3: Verify migration (all rows should have a category_id)
DO $$
DECLARE
    null_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO null_count
    FROM inventory_item_types
    WHERE inventory_item_category_id IS NULL AND is_active = TRUE;
    
    IF null_count > 0 THEN
        RAISE EXCEPTION 'Migration failed: % active items have NULL category_id', null_count;
    END IF;
    
    RAISE NOTICE 'Migration verification passed: All active items have valid category_id';
END $$;

-- Step 4: Make the column NOT NULL
ALTER TABLE inventory_item_types
ALTER COLUMN inventory_item_category_id SET NOT NULL;

-- Step 5: Add foreign key constraint
ALTER TABLE inventory_item_types
ADD CONSTRAINT fk_inventory_item_types_category
FOREIGN KEY (inventory_item_category_id)
REFERENCES inventory_item_category(id)
ON DELETE RESTRICT;

-- Step 6: Add index for better query performance
CREATE INDEX idx_inventory_item_types_category_id
ON inventory_item_types(inventory_item_category_id);

-- Step 7: Drop the old category column
ALTER TABLE inventory_item_types
DROP COLUMN category;

-- Step 8: Add comment
COMMENT ON COLUMN inventory_item_types.inventory_item_category_id IS 'Foreign key to inventory_item_category table';

-- Migration complete
-- Note: Run this script AFTER:
--   1. T265_inventory_item_category.sql (table creation)
--   2. DL265_inventory_item_category.sql (data load)

