-- =====================================================
-- Data Load: inventory_item_types
-- Description: Load inventory item type data
-- =====================================================

-- Insert inventory item types
INSERT INTO inventory_item_types (id, name, description, category, is_active) VALUES
(1, 'CASUAL_DRESS_1', 'Casual Dress 1 (Pant-Shirt)', 'UNIFORM', TRUE),
(2, 'CASUAL_DRESS_2', 'Casual Dress 2 (Pant-T-Shirt)', 'UNIFORM', TRUE),
(3, 'WINTER_DRESS', 'Winter Dress', 'UNIFORM', TRUE),
(4, 'SHIRT', 'Shirt (Individual)', 'UNIFORM', TRUE),
(5, 'PANT', 'Pant (Individual)', 'UNIFORM', TRUE),
(6, 'T_SHIRT', 'T-Shirt (Individual)', 'UNIFORM', TRUE),
(7, 'TIE', 'Tie', 'ACCESSORY', TRUE),
(8, 'BELT', 'Belt', 'ACCESSORY', TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    category = EXCLUDED.category,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

