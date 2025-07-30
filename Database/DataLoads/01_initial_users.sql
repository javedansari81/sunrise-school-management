-- =====================================================
-- Initial Users and Admin Accounts
-- =====================================================

-- Insert default admin user
INSERT INTO users (
    email, hashed_password, first_name, last_name, phone, role, is_active, is_verified, created_at
) VALUES (
    'admin@sunriseschool.edu',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsHjxstm6', -- password: admin123
    'Admin',
    'User',
    '9876543210',
    'admin',
    true,
    true,
    NOW()
) ON CONFLICT (email) DO NOTHING;

-- Insert principal user
INSERT INTO users (
    email, hashed_password, first_name, last_name, phone, role, is_active, is_verified, created_at
) VALUES (
    'principal@sunriseschool.edu',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3L3jzjvG4u', -- password: admin123
    'Dr. Rajesh',
    'Kumar',
    '9876543211',
    'admin',
    true,
    true,
    NOW()
) ON CONFLICT (email) DO NOTHING;

-- Insert sample teacher users
INSERT INTO users (
    email, hashed_password, first_name, last_name, phone, role, is_active, is_verified, created_at
) VALUES 
(
    'priya.sharma@sunriseschool.edu',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3L3jzjvG4u', -- password: admin123
    'Priya',
    'Sharma',
    '9876543212',
    'teacher',
    true,
    true,
    NOW()
),
(
    'amit.patel@sunriseschool.edu',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3L3jzjvG4u', -- password: admin123
    'Amit',
    'Patel',
    '9876543213',
    'teacher',
    true,
    true,
    NOW()
),
(
    'sunita.gupta@sunriseschool.edu',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3L3jzjvG4u', -- password: admin123
    'Sunita',
    'Gupta',
    '9876543214',
    'teacher',
    true,
    true,
    NOW()
),
(
    'rahul.singh@sunriseschool.edu',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3L3jzjvG4u', -- password: admin123
    'Rahul',
    'Singh',
    '9876543215',
    'teacher',
    true,
    true,
    NOW()
),
(
    'meera.joshi@sunriseschool.edu',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3L3jzjvG4u', -- password: admin123
    'Meera',
    'Joshi',
    '9876543216',
    'teacher',
    true,
    true,
    NOW()
) ON CONFLICT (email) DO NOTHING;

-- Insert sample parent users
INSERT INTO users (
    email, hashed_password, first_name, last_name, phone, role, is_active, is_verified, created_at
) VALUES 
(
    'rajesh.sharma@gmail.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3L3jzjvG4u', -- password: admin123
    'Rajesh',
    'Sharma',
    '9876543220',
    'parent',
    true,
    true,
    NOW()
),
(
    'anita.patel@gmail.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3L3jzjvG4u', -- password: admin123
    'Anita',
    'Patel',
    '9876543221',
    'parent',
    true,
    true,
    NOW()
),
(
    'suresh.kumar@gmail.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3L3jzjvG4u', -- password: admin123
    'Suresh',
    'Kumar',
    '9876543222',
    'parent',
    true,
    true,
    NOW()
) ON CONFLICT (email) DO NOTHING;

-- Insert user profiles for admin users
INSERT INTO user_profiles (
    user_id, date_of_birth, gender, address, city, state, postal_code, country, created_at
) VALUES 
(
    (SELECT id FROM users WHERE email = 'admin@sunriseschool.edu'),
    '1980-01-15',
    'Male',
    '123 School Admin Block, Education District',
    'Mumbai',
    'Maharashtra',
    '400001',
    'India',
    NOW()
),
(
    (SELECT id FROM users WHERE email = 'principal@sunriseschool.edu'),
    '1975-05-20',
    'Male',
    '456 Principal Residence, School Campus',
    'Mumbai',
    'Maharashtra',
    '400001',
    'India',
    NOW()
) ON CONFLICT (user_id) DO NOTHING;

-- Insert default permissions for admin users
INSERT INTO user_permissions (user_id, permission_name, granted, granted_at) VALUES
-- Admin user permissions
((SELECT id FROM users WHERE email = 'admin@sunriseschool.edu'), 'manage_users', true, NOW()),
((SELECT id FROM users WHERE email = 'admin@sunriseschool.edu'), 'manage_students', true, NOW()),
((SELECT id FROM users WHERE email = 'admin@sunriseschool.edu'), 'manage_teachers', true, NOW()),
((SELECT id FROM users WHERE email = 'admin@sunriseschool.edu'), 'manage_fees', true, NOW()),
((SELECT id FROM users WHERE email = 'admin@sunriseschool.edu'), 'manage_expenses', true, NOW()),
((SELECT id FROM users WHERE email = 'admin@sunriseschool.edu'), 'view_reports', true, NOW()),
((SELECT id FROM users WHERE email = 'admin@sunriseschool.edu'), 'manage_attendance', true, NOW()),
((SELECT id FROM users WHERE email = 'admin@sunriseschool.edu'), 'approve_leaves', true, NOW()),

-- Principal user permissions
((SELECT id FROM users WHERE email = 'principal@sunriseschool.edu'), 'manage_students', true, NOW()),
((SELECT id FROM users WHERE email = 'principal@sunriseschool.edu'), 'manage_teachers', true, NOW()),
((SELECT id FROM users WHERE email = 'principal@sunriseschool.edu'), 'view_reports', true, NOW()),
((SELECT id FROM users WHERE email = 'principal@sunriseschool.edu'), 'approve_leaves', true, NOW()),
((SELECT id FROM users WHERE email = 'principal@sunriseschool.edu'), 'approve_expenses', true, NOW())
ON CONFLICT (user_id, permission_name) DO NOTHING;

-- Comments
COMMENT ON TABLE users IS 'Initial admin and sample user accounts for system setup';

-- Display created users
SELECT 
    id,
    email,
    first_name,
    last_name,
    role,
    is_active,
    created_at
FROM users 
ORDER BY role, created_at;
