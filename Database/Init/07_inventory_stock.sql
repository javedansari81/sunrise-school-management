-- =====================================================
-- Inventory Stock Initialization Script
-- =====================================================
-- This script initializes stock records for all inventory items
-- Sets default thresholds and zero initial quantities
-- =====================================================

-- Insert stock records for all item-size combinations
-- This creates a complete stock tracking matrix

INSERT INTO inventory_stock (
    inventory_item_type_id,
    size_type_id,
    current_quantity,
    minimum_threshold,
    reorder_quantity,
    last_restocked_date,
    last_updated
)
SELECT 
    iit.id AS inventory_item_type_id,
    ist.id AS size_type_id,
    0 AS current_quantity,  -- Start with zero stock
    CASE 
        WHEN iit.category = 'UNIFORM' THEN 20  -- Higher threshold for uniforms
        WHEN iit.category = 'ACCESSORY' THEN 10  -- Lower threshold for accessories
        ELSE 15  -- Default threshold
    END AS minimum_threshold,
    CASE 
        WHEN iit.category = 'UNIFORM' THEN 50  -- Higher reorder for uniforms
        WHEN iit.category = 'ACCESSORY' THEN 30  -- Lower reorder for accessories
        ELSE 40  -- Default reorder quantity
    END AS reorder_quantity,
    NULL AS last_restocked_date,
    CURRENT_TIMESTAMP AS last_updated
FROM 
    inventory_item_types iit
CROSS JOIN 
    inventory_size_types ist
WHERE 
    iit.is_active = TRUE 
    AND ist.is_active = TRUE
    AND NOT EXISTS (
        -- Avoid duplicates if script is run multiple times
        SELECT 1 
        FROM inventory_stock s 
        WHERE s.inventory_item_type_id = iit.id 
        AND s.size_type_id = ist.id
    )
ORDER BY 
    iit.id, ist.sort_order;

-- Verify the initialization
SELECT 
    COUNT(*) AS total_stock_records,
    SUM(CASE WHEN current_quantity = 0 THEN 1 ELSE 0 END) AS zero_stock_items,
    SUM(CASE WHEN current_quantity > 0 THEN 1 ELSE 0 END) AS in_stock_items
FROM inventory_stock;

-- Display summary by item type
SELECT 
    iit.name AS item_type,
    iit.description,
    iit.category,
    COUNT(s.id) AS size_variants,
    SUM(s.current_quantity) AS total_quantity,
    MIN(s.minimum_threshold) AS min_threshold,
    MAX(s.reorder_quantity) AS max_reorder_qty
FROM 
    inventory_item_types iit
LEFT JOIN 
    inventory_stock s ON iit.id = s.inventory_item_type_id
WHERE 
    iit.is_active = TRUE
GROUP BY 
    iit.id, iit.name, iit.description, iit.category
ORDER BY 
    iit.category, iit.name;

