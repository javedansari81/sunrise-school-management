-- =====================================================
-- Table: school_settings
-- Description: Per-school key/value settings (receipt prefix, WhatsApp
--              templates, late fee rules, Cloudinary folder, ...)
-- Dependencies: schools
-- =====================================================

DROP TABLE IF EXISTS school_settings CASCADE;

CREATE TABLE school_settings (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL REFERENCES schools(id),
    key VARCHAR(100) NOT NULL,
    value TEXT,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT school_settings_school_key_unique UNIQUE (school_id, key)
);

COMMENT ON TABLE school_settings IS 'Per-school key/value settings (receipt prefix, WhatsApp templates, late fee rules, ...)';
