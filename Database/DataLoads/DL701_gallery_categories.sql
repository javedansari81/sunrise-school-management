-- =====================================================
-- Data Load: gallery_categories
-- Description: Initial data for gallery categories
-- Dependencies: T700_gallery_categories.sql
-- =====================================================

-- Insert gallery categories
INSERT INTO gallery_categories (id, name, description, icon, display_order, is_active) VALUES
(1, 'Independence Day', 'Independence Day celebrations and patriotic events', 'Flag', 1, TRUE),
(2, 'School Premises', 'School building, classrooms, and facilities', 'School', 2, TRUE),
(3, 'First Day of School', 'First day memories and new student orientation', 'CalendarToday', 3, TRUE),
(4, 'Sports Day', 'Annual sports day events and athletic activities', 'SportsBasketball', 4, TRUE),
(5, 'Annual Function', 'Annual day celebrations and cultural programs', 'TheaterComedy', 5, TRUE),
(6, 'Republic Day', 'Republic Day celebrations and parade', 'EmojiFlags', 6, TRUE),
(7, 'Science Exhibition', 'Science fair and student projects', 'Science', 7, TRUE),
(8, 'Cultural Events', 'Cultural programs, dance, and music events', 'MusicNote', 8, TRUE),
(9, 'Classroom Activities', 'Daily classroom activities and learning', 'MenuBook', 9, TRUE),
(10, 'Teachers Day', 'Teachers Day celebrations and appreciation', 'Person', 10, TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    icon = EXCLUDED.icon,
    display_order = EXCLUDED.display_order,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- Verify insertion
DO $$
DECLARE
    record_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO record_count FROM gallery_categories;
    RAISE NOTICE 'Gallery Categories loaded: % records', record_count;
END $$;

