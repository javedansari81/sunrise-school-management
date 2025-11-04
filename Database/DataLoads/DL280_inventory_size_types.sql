-- =====================================================
-- Data Load: inventory_size_types
-- Description: Load inventory size type data
-- =====================================================

-- Insert inventory size types (numeric sizes from 20 to 38)
INSERT INTO inventory_size_types (id, name, description, sort_order, is_active) VALUES
(1, '20', 'Size 20', 1, TRUE),
(2, '22', 'Size 22', 2, TRUE),
(3, '24', 'Size 24', 3, TRUE),
(4, '26', 'Size 26', 4, TRUE),
(5, '28', 'Size 28', 5, TRUE),
(6, '30', 'Size 30', 6, TRUE),
(7, '32', 'Size 32', 7, TRUE),
(8, '34', 'Size 34', 8, TRUE),
(9, '36', 'Size 36', 9, TRUE),
(10, '38', 'Size 38', 10, TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    sort_order = EXCLUDED.sort_order,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

