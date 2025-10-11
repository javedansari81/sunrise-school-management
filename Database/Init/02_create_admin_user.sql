-- =====================================================
-- Create Admin User for Sunrise School Management System
-- =====================================================
-- This script creates the default admin user for system access
-- Run this AFTER loading metadata
--
-- USAGE:
-- psql -U sunrise_user -d sunrise_school_db -f Database/Init/02_create_admin_user.sql

-- Start transaction
BEGIN;

-- =====================================================
-- Create Default Admin User
-- =====================================================
INSERT INTO users (
    first_name,
    last_name,
    phone,
    email,
    password,
    user_type_id,
    is_active,
    created_at
) VALUES (
    'Admin',
    'User',
    '7842350875',
    'admin@sunrise.com',
    '$2b$12$lsBmuOua4csDUY6k0hWgWO.G7GN2oHTN.388/BfgTqH51Os01ttnu', -- password: admin123 (corrected hash)
    (SELECT id FROM user_types WHERE name = 'ADMIN' LIMIT 1),
    true,
    NOW()
) ON CONFLICT (email) DO UPDATE SET
    password = EXCLUDED.password,
    user_type_id = EXCLUDED.user_type_id,
    updated_at = NOW();

-- Commit transaction
COMMIT;

-- =====================================================
-- Success Message
-- =====================================================
\echo '=========================================='
\echo 'ADMIN USER CREATED SUCCESSFULLY!'
\echo '=========================================='
\echo 'Login credentials:'
\echo 'Email: admin@sunrise.com'
\echo 'Password: admin123'
\echo ''
\echo 'IMPORTANT: Change the default password after first login!'
\echo '=========================================='
