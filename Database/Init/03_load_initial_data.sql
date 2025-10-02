-- =====================================================
-- Load Initial Data - Optimized for Cloud Deployment
-- =====================================================
-- This script loads essential initial data using pure SQL
-- Run this AFTER all table creation scripts have been executed
--
-- PREREQUISITES:
-- 1. All 9 table creation scripts must be executed first
-- 2. Metadata tables must be populated with reference data
-- 3. Database must have the optimized schema with inline constraints

-- Start transaction
BEGIN;

-- =====================================================
-- 1. Verify tables exist
-- =====================================================

-- Check if required tables exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users') THEN
        RAISE EXCEPTION 'Users table does not exist. Create tables first!';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'user_types') THEN
        RAISE EXCEPTION 'Metadata tables do not exist. Run metadata table creation script first!';
    END IF;
    RAISE NOTICE 'Table verification passed - proceeding with data load';
END $$;

-- =====================================================
-- 2. Create admin user (metadata-driven with foreign keys)
-- =====================================================

INSERT INTO users (
    first_name, last_name, phone, email, password, user_type_id, is_active, created_at
) VALUES (
    'Admin',
    'User',
    '7842350875',
    'admin@sunriseschool.edu',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsHjxstm6', -- password: admin123
    (SELECT id FROM user_types WHERE value = 'ADMIN' LIMIT 1),
    true,
    NOW()
) ON CONFLICT (email) DO UPDATE SET
    user_type_id = EXCLUDED.user_type_id,
    updated_at = NOW();

-- =====================================================
-- 3. Create schema_versions table and update version
-- =====================================================

CREATE TABLE IF NOT EXISTS schema_versions (
    id SERIAL PRIMARY KEY,
    version VARCHAR(10) NOT NULL,
    description TEXT,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    applied_by VARCHAR(100) DEFAULT current_user
);

INSERT INTO schema_versions (version, description)
VALUES ('2.1', 'Initial data load completed with optimized metadata-driven structure')
ON CONFLICT DO NOTHING;

-- =====================================================
-- 4. Verification queries
-- =====================================================

-- Show what was created
SELECT 'VERIFICATION RESULTS:' as status;

SELECT 'Users created' as table_name, COUNT(*) as count FROM users;

-- Show admin user
SELECT
    'ADMIN USER:' as info,
    u.email,
    u.first_name || ' ' || u.last_name as name,
    ut.name as user_type
FROM users u
LEFT JOIN user_types ut ON u.user_type_id = ut.id
WHERE u.email = 'admin@sunriseschool.edu';

-- Commit the transaction
COMMIT;

-- Final success message
SELECT 'SUCCESS: Optimized initial data load completed!' as result;
SELECT 'Sample data created with metadata-driven foreign key relationships' as details;
SELECT 'You can now test the API endpoints with the sample data' as next_step;
