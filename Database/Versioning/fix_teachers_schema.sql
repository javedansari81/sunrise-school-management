-- =====================================================
-- Fix Teachers Table Schema Mismatch
-- Add missing columns to match the SQLAlchemy model
-- =====================================================

-- For SQLite (if using SQLite database)
-- SQLite doesn't support IF NOT EXISTS for ADD COLUMN, so we use a different approach

-- Add missing columns to teachers table (SQLite compatible)
-- Note: Run each ALTER TABLE statement separately if any fail

-- Add bio column
ALTER TABLE teachers ADD COLUMN bio TEXT DEFAULT '';

-- Add specializations column
ALTER TABLE teachers ADD COLUMN specializations TEXT DEFAULT '[]';

-- Add certifications column
ALTER TABLE teachers ADD COLUMN certifications TEXT DEFAULT '[]';

-- Add img column
ALTER TABLE teachers ADD COLUMN img TEXT DEFAULT '';

-- For PostgreSQL (if using PostgreSQL database)
-- Uncomment the following lines and comment out the SQLite version above:

-- ALTER TABLE teachers ADD COLUMN IF NOT EXISTS bio TEXT;
-- ALTER TABLE teachers ADD COLUMN IF NOT EXISTS specializations TEXT;
-- ALTER TABLE teachers ADD COLUMN IF NOT EXISTS certifications TEXT;
-- ALTER TABLE teachers ADD COLUMN IF NOT EXISTS img TEXT;

-- Update existing records with default values (works for both SQLite and PostgreSQL)
UPDATE teachers SET
    bio = COALESCE(bio, ''),
    specializations = COALESCE(specializations, '[]'),
    certifications = COALESCE(certifications, '[]'),
    img = COALESCE(img, '')
WHERE bio IS NULL OR specializations IS NULL OR certifications IS NULL OR img IS NULL;

-- Verify the changes (PostgreSQL only - comment out for SQLite)
-- SELECT column_name, data_type, is_nullable
-- FROM information_schema.columns
-- WHERE table_name = 'teachers'
-- AND column_name IN ('bio', 'specializations', 'certifications', 'img')
-- ORDER BY column_name;
