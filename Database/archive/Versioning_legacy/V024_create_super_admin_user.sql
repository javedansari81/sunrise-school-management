-- =====================================================
-- Migration: V024_create_super_admin_user.sql
-- Description: Create a test SUPER_ADMIN user account
-- Author: System
-- Date: 2026-01-07
-- =====================================================
-- Login credentials:
-- Email: superadmin@sunrise.com
-- Password: admin123

INSERT INTO users (
    first_name,
    last_name,
    phone,
    email,
    password,
    user_type_id,
    is_active,
    is_deleted,
    created_at
) VALUES (
    'Super',
    'Admin',
    '9999999999',
    'superadmin@sunrise.com',
    '$2b$12$lsBmuOua4csDUY6k0hWgWO.G7GN2oHTN.388/BfgTqH51Os01ttnu',
    6,
    TRUE,
    FALSE,
    NOW()
);
