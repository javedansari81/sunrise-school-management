-- =====================================================
-- V005: Per-school email domain (Phase 5)
-- =====================================================
-- Generated student and teacher emails used the fixed domain sunrise.com for
-- every school. The domain is now the school setting user.email_domain
-- (default "<school code>.<BASE_DOMAIN>", see app/services/school_settings.py).
-- Sunrise keeps sunrise.com, so existing logins and new ones match.
--
-- Not copied to new schools: a school created from the Sunrise template must
-- not generate sunrise.com addresses.
-- =====================================================

INSERT INTO school_settings (school_id, key, value, description)
SELECT id, 'user.email_domain', 'sunrise.com',
       'Domain of generated student and teacher emails'
FROM schools WHERE code = 'sunrise'
ON CONFLICT (school_id, key) DO NOTHING;
