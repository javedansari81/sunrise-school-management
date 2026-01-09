-- =====================================================
-- Migration: V023_add_super_admin_user_type.sql
-- Description: Add SUPER_ADMIN user type to the user_types metadata table
-- Author: System
-- Date: 2026-01-07
-- =====================================================

-- Start transaction
BEGIN;

-- =====================================================
-- Add SUPER_ADMIN User Type
-- =====================================================
INSERT INTO user_types (id, name, description, is_active) VALUES
(6, 'SUPER_ADMIN', 'Super Administrator with elevated privileges', TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- Commit transaction
COMMIT;

-- =====================================================
-- Success Message
-- =====================================================
\echo '=========================================='
\echo 'Migration V023 completed successfully!'
\echo 'Added SUPER_ADMIN user type (id=6)'
\echo '=========================================='

