-- =====================================================
-- Data Load: inventory_item_types
-- Description: Load inventory item type data
-- =====================================================

-- Insert inventory item types
INSERT INTO inventory_item_types (id, name, description, inventory_item_category_id, is_active) VALUES
(1, 'CASUAL_DRESS_1', 'Casual Dress 1 (Pant-Shirt)', 1, TRUE),
(2, 'CASUAL_DRESS_2', 'Casual Dress 2 (Pant-T-Shirt)', 1, TRUE),
(3, 'WINTER_DRESS', 'Winter Dress', 1, TRUE),
(4, 'SHIRT', 'Shirt (Individual)', 1, TRUE),
(5, 'PANT', 'Pant (Individual)', 1, TRUE),
(6, 'T_SHIRT', 'T-Shirt (Individual)', 1, TRUE),
(7, 'TIE', 'Tie', 2, TRUE),
(8, 'BELT', 'Belt', 2, TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    inventory_item_category_id = EXCLUDED.inventory_item_category_id,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

