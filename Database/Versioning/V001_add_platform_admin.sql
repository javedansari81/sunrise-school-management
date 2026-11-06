-- =====================================================
-- V001: Platform admin role
-- =====================================================
-- Platform admins manage schools (create, edit, suspend). They belong to no
-- school: users.school_id is NULL for them and only for them.
--
-- Also in the baseline: Tables/T300_users.sql, Init/01_load_metadata.sql
-- =====================================================

INSERT INTO user_types (id, name, description, is_active)
VALUES (7, 'PLATFORM_ADMIN', 'Platform administrator: manages schools, belongs to no school', TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

ALTER TABLE users ALTER COLUMN school_id DROP NOT NULL;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'users_school_matches_user_type') THEN
        ALTER TABLE users ADD CONSTRAINT users_school_matches_user_type
            CHECK ((user_type_id = 7) = (school_id IS NULL));
    END IF;
END $$;

-- Platform admin emails are unique among platform admins
CREATE UNIQUE INDEX IF NOT EXISTS users_platform_email_active_unique
ON users (email)
WHERE school_id IS NULL AND (is_deleted = FALSE OR is_deleted IS NULL);

COMMENT ON COLUMN users.school_id IS 'School (tenant) this user belongs to. NULL only for platform admins (user type 7)';
