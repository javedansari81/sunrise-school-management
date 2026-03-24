-- =====================================================
-- Data Load: inventory_item_category
-- Description: Load inventory category data
-- =====================================================

-- Insert inventory item categories
INSERT INTO inventory_item_category (id, name, description, display_order, is_active) VALUES
(1, 'UNIFORM', 'School Uniforms', 1, TRUE),
(2, 'ACCESSORY', 'Uniform Accessories', 2, TRUE),
(3, 'BOOKS', 'School Books', 3, TRUE),
(4, 'NOTEBOOKS', 'School Notebooks', 4, TRUE),
(5, 'STATIONERY', 'School Stationery', 5, TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    display_order = EXCLUDED.display_order,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

