-- =====================================================
-- Create Test Student User: javed.ansari81@gmail.com
-- =====================================================
-- This script creates a test student user for dashboard testing
-- Password: Sunrise@001 (hashed)

-- First, create the user account
INSERT INTO users (
    first_name, 
    last_name, 
    email, 
    hashed_password, 
    phone, 
    user_type_id, 
    is_active, 
    is_verified,
    created_at
) VALUES (
    'Javed',
    'Ansari',
    'javed.ansari81@gmail.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsHjxstm6', -- Sunrise@001
    '7842350875',
    3, -- STUDENT role (from user_types table)
    true,
    true,
    NOW()
) ON CONFLICT (email) DO UPDATE SET
    user_type_id = EXCLUDED.user_type_id,
    is_active = EXCLUDED.is_active,
    is_verified = EXCLUDED.is_verified,
    updated_at = NOW();

-- Get the user ID for the student record
DO $$
DECLARE
    user_id_var INTEGER;
    class_id_var INTEGER;
    session_year_id_var INTEGER;
    gender_id_var INTEGER;
BEGIN
    -- Get the user ID
    SELECT id INTO user_id_var FROM users WHERE email = 'javed.ansari81@gmail.com';
    
    -- Get a valid class ID (first available class)
    SELECT id INTO class_id_var FROM classes WHERE is_active = true LIMIT 1;
    
    -- Get current session year ID
    SELECT id INTO session_year_id_var FROM session_years WHERE is_active = true ORDER BY start_date DESC LIMIT 1;
    
    -- Get male gender ID
    SELECT id INTO gender_id_var FROM genders WHERE name = 'Male' LIMIT 1;
    
    -- Create the student record
    INSERT INTO students (
        user_id,
        admission_number,
        first_name,
        last_name,
        date_of_birth,
        gender_id,
        class_id,
        session_year_id,
        roll_number,
        section,
        phone,
        email,
        address,
        city,
        state,
        postal_code,
        father_name,
        father_phone,
        father_email,
        mother_name,
        mother_phone,
        mother_email,
        emergency_contact_name,
        emergency_contact_phone,
        emergency_contact_relation,
        admission_date,
        is_active,
        created_at
    ) VALUES (
        user_id_var,
        'STU2024001',
        'Javed',
        'Ansari',
        '2008-03-15',
        gender_id_var,
        class_id_var,
        session_year_id_var,
        1,
        'A',
        '7842350875',
        'javed.ansari81@gmail.com',
        '123 Test Street, Test City',
        'Test City',
        'Test State',
        '123456',
        'Mohammad Ansari',
        '7842350876',
        'mohammad.ansari@gmail.com',
        'Fatima Ansari',
        '7842350877',
        'fatima.ansari@gmail.com',
        'Mohammad Ansari',
        '7842350876',
        'Father',
        '2024-01-01',
        true,
        NOW()
    ) ON CONFLICT (user_id) DO UPDATE SET
        email = EXCLUDED.email,
        phone = EXCLUDED.phone,
        is_active = EXCLUDED.is_active,
        updated_at = NOW();
        
    RAISE NOTICE 'Test student user created successfully:';
    RAISE NOTICE 'Email: javed.ansari81@gmail.com';
    RAISE NOTICE 'Password: Sunrise@001';
    RAISE NOTICE 'Role: STUDENT';
    RAISE NOTICE 'User ID: %', user_id_var;
END $$;

-- Verify the user was created correctly
SELECT 
    u.id as user_id,
    u.first_name,
    u.last_name,
    u.email,
    ut.name as user_type,
    u.is_active,
    s.admission_number,
    s.roll_number,
    c.name as class_name,
    s.section
FROM users u
JOIN user_types ut ON u.user_type_id = ut.id
LEFT JOIN students s ON u.id = s.user_id
LEFT JOIN classes c ON s.class_id = c.id
WHERE u.email = 'javed.ansari81@gmail.com';
