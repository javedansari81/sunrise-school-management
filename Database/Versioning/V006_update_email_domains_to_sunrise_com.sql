-- Update email domains from sunrise.edu and sunriseschool.edu to sunrise.com
-- This script updates all email fields across all tables to use @sunrise.com domain

-- Start transaction
BEGIN;

-- Update users table
UPDATE users 
SET email = REPLACE(REPLACE(email, '@sunrise.edu', '@sunrise.com'), '@sunriseschool.edu', '@sunrise.com'),
    updated_at = NOW()
WHERE email LIKE '%@sunrise.edu' OR email LIKE '%@sunriseschool.edu';

-- Update students table - main email
UPDATE students 
SET email = REPLACE(REPLACE(email, '@sunrise.edu', '@sunrise.com'), '@sunriseschool.edu', '@sunrise.com'),
    updated_at = NOW()
WHERE email LIKE '%@sunrise.edu' OR email LIKE '%@sunriseschool.edu';

-- Update students table - father email
UPDATE students 
SET father_email = REPLACE(REPLACE(father_email, '@sunrise.edu', '@sunrise.com'), '@sunriseschool.edu', '@sunrise.com'),
    updated_at = NOW()
WHERE father_email LIKE '%@sunrise.edu' OR father_email LIKE '%@sunriseschool.edu';

-- Update students table - mother email
UPDATE students 
SET mother_email = REPLACE(REPLACE(mother_email, '@sunrise.edu', '@sunrise.com'), '@sunriseschool.edu', '@sunrise.com'),
    updated_at = NOW()
WHERE mother_email LIKE '%@sunrise.edu' OR mother_email LIKE '%@sunriseschool.edu';

-- Update students table - guardian email
UPDATE students 
SET guardian_email = REPLACE(REPLACE(guardian_email, '@sunrise.edu', '@sunrise.com'), '@sunriseschool.edu', '@sunrise.com'),
    updated_at = NOW()
WHERE guardian_email LIKE '%@sunrise.edu' OR guardian_email LIKE '%@sunriseschool.edu';

-- Update teachers table
UPDATE teachers 
SET email = REPLACE(REPLACE(email, '@sunrise.edu', '@sunrise.com'), '@sunriseschool.edu', '@sunrise.com'),
    updated_at = NOW()
WHERE email LIKE '%@sunrise.edu' OR email LIKE '%@sunriseschool.edu';

-- Update vendors table
UPDATE vendors 
SET email = REPLACE(REPLACE(email, '@sunrise.edu', '@sunrise.com'), '@sunriseschool.edu', '@sunrise.com'),
    updated_at = NOW()
WHERE email LIKE '%@sunrise.edu' OR email LIKE '%@sunriseschool.edu';

-- Show summary of changes
SELECT 'users' as table_name, COUNT(*) as updated_count 
FROM users 
WHERE email LIKE '%@sunrise.com'
UNION ALL
SELECT 'students_main_email', COUNT(*) 
FROM students 
WHERE email LIKE '%@sunrise.com'
UNION ALL
SELECT 'students_father_email', COUNT(*) 
FROM students 
WHERE father_email LIKE '%@sunrise.com'
UNION ALL
SELECT 'students_mother_email', COUNT(*) 
FROM students 
WHERE mother_email LIKE '%@sunrise.com'
UNION ALL
SELECT 'students_guardian_email', COUNT(*) 
FROM students 
WHERE guardian_email LIKE '%@sunrise.com'
UNION ALL
SELECT 'teachers', COUNT(*) 
FROM teachers 
WHERE email LIKE '%@sunrise.com'
UNION ALL
SELECT 'vendors', COUNT(*) 
FROM vendors 
WHERE email LIKE '%@sunrise.com';

-- Commit transaction
COMMIT;

-- Verification queries (run these after the update to verify changes)
-- SELECT 'users' as table_name, email FROM users WHERE email LIKE '%@sunrise.com';
-- SELECT 'students' as table_name, email, father_email, mother_email, guardian_email FROM students WHERE email LIKE '%@sunrise.com' OR father_email LIKE '%@sunrise.com' OR mother_email LIKE '%@sunrise.com' OR guardian_email LIKE '%@sunrise.com';
-- SELECT 'teachers' as table_name, email FROM teachers WHERE email LIKE '%@sunrise.com';
-- SELECT 'vendors' as table_name, email FROM vendors WHERE email LIKE '%@sunrise.com';
