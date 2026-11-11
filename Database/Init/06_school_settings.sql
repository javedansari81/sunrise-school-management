-- =====================================================
-- Default school: general settings (same as migration V005)
-- =====================================================
-- user.email_domain: domain of generated student and teacher emails.
-- Sunrise keeps sunrise.com. Not copied to new schools.
-- =====================================================

INSERT INTO school_settings (school_id, key, value, description)
SELECT id, 'user.email_domain', 'sunrise.com',
       'Domain of generated student and teacher emails'
FROM schools WHERE code = 'sunrise'
ON CONFLICT (school_id, key) DO NOTHING;
