-- =====================================================
-- Row-level security on every school-owned table
-- =====================================================
-- Runs last, after the seed data, so the seed scripts write without a school
-- setting. See Functions/F900_tenant_row_level_security.sql.
-- =====================================================

SELECT enable_tenant_row_level_security();
