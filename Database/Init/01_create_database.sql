-- =====================================================
-- Complete Database Creation Script
-- =====================================================
-- This script creates the entire Sunrise School Management database schema

-- Start transaction
BEGIN;

-- =====================================================
-- 1. Create all tables in dependency order
-- =====================================================

-- Note: In PostgreSQL, \i command requires absolute paths or relative to current directory
-- For manual execution, run each table creation script individually:
-- psql -d your_database -f ../Tables/02_users.sql
-- psql -d your_database -f ../Tables/03_students.sql
-- etc.

-- For this script, we'll include the essential table creation inline
-- Users and Authentication Tables (Essential core)
-- (Include essential table definitions here or reference the individual files)

-- =====================================================
-- 2. Create version tracking table
-- =====================================================

CREATE TABLE IF NOT EXISTS schema_versions (
    id SERIAL PRIMARY KEY,
    version VARCHAR(10) NOT NULL,
    description TEXT,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    applied_by VARCHAR(100) DEFAULT current_user
);

-- Insert initial version
INSERT INTO schema_versions (version, description) 
VALUES ('1.0', 'Initial database schema creation with all core tables');

-- =====================================================
-- 3. Create additional utility functions (optional)
-- =====================================================

-- Function to calculate age from date of birth
CREATE OR REPLACE FUNCTION calculate_age(birth_date DATE)
RETURNS INTEGER AS $$
BEGIN
    RETURN EXTRACT(YEAR FROM AGE(birth_date));
END;
$$ LANGUAGE plpgsql;

-- Function to get academic year from date
CREATE OR REPLACE FUNCTION get_academic_year(input_date DATE DEFAULT CURRENT_DATE)
RETURNS VARCHAR(10) AS $$
DECLARE
    year_start INTEGER;
    year_end INTEGER;
BEGIN
    -- Academic year starts in April
    IF EXTRACT(MONTH FROM input_date) >= 4 THEN
        year_start := EXTRACT(YEAR FROM input_date);
        year_end := year_start + 1;
    ELSE
        year_end := EXTRACT(YEAR FROM input_date);
        year_start := year_end - 1;
    END IF;
    
    RETURN year_start || '-' || RIGHT(year_end::TEXT, 2);
END;
$$ LANGUAGE plpgsql;

-- Function to calculate fee balance
CREATE OR REPLACE FUNCTION calculate_fee_balance()
RETURNS TRIGGER AS $$
BEGIN
    NEW.balance_amount := NEW.total_amount - NEW.paid_amount;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for automatic balance calculation
CREATE TRIGGER trigger_calculate_fee_balance
    BEFORE INSERT OR UPDATE ON fee_records
    FOR EACH ROW
    EXECUTE FUNCTION calculate_fee_balance();

-- =====================================================
-- 4. Create useful views
-- =====================================================

-- Student summary view
CREATE OR REPLACE VIEW student_summary AS
SELECT 
    s.id,
    s.admission_number,
    s.first_name || ' ' || s.last_name AS full_name,
    s.class,
    s.section,
    s.session_year,
    s.father_name,
    s.father_phone,
    s.mother_name,
    s.mother_phone,
    s.is_active,
    calculate_age(s.date_of_birth) AS age
FROM students s;

-- Teacher summary view
CREATE OR REPLACE VIEW teacher_summary AS
SELECT 
    t.id,
    t.employee_id,
    t.first_name || ' ' || t.last_name AS full_name,
    t.position,
    t.department,
    t.class_teacher_of,
    t.employment_type,
    t.experience_years,
    t.is_active,
    calculate_age(t.date_of_birth) AS age
FROM teachers t;

-- Fee collection summary view
CREATE OR REPLACE VIEW fee_collection_summary AS
SELECT 
    fr.session_year,
    s.class,
    COUNT(*) AS total_students,
    SUM(fr.total_amount) AS total_fees,
    SUM(fr.paid_amount) AS collected_amount,
    SUM(fr.balance_amount) AS pending_amount,
    ROUND((SUM(fr.paid_amount) * 100.0 / NULLIF(SUM(fr.total_amount), 0)), 2) AS collection_percentage
FROM fee_records fr
JOIN students s ON fr.student_id = s.id
GROUP BY fr.session_year, s.class;

-- =====================================================
-- 5. Grant permissions (adjust as needed)
-- =====================================================

-- Grant permissions to application user (replace 'app_user' with your actual username)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;

-- =====================================================
-- 6. Verification queries
-- =====================================================

-- Count tables created
SELECT 
    'Tables Created' AS object_type,
    COUNT(*) AS count
FROM information_schema.tables 
WHERE table_schema = 'public'
AND table_type = 'BASE TABLE'

UNION ALL

-- Count views created
SELECT 
    'Views Created' AS object_type,
    COUNT(*) AS count
FROM information_schema.views 
WHERE table_schema = 'public'

UNION ALL

-- Count functions created
SELECT 
    'Functions Created' AS object_type,
    COUNT(*) AS count
FROM information_schema.routines 
WHERE routine_schema = 'public'
AND routine_type = 'FUNCTION'

UNION ALL

-- Count indexes created
SELECT 
    'Indexes Created' AS object_type,
    COUNT(*) AS count
FROM pg_indexes 
WHERE schemaname = 'public';

-- List all tables
SELECT 
    tablename,
    CASE 
        WHEN tablename LIKE '%users%' THEN 'Authentication'
        WHEN tablename LIKE '%student%' THEN 'Student Management'
        WHEN tablename LIKE '%teacher%' THEN 'Teacher Management'
        WHEN tablename LIKE '%fee%' THEN 'Fee Management'
        WHEN tablename LIKE '%attendance%' THEN 'Attendance Management'
        WHEN tablename LIKE '%leave%' THEN 'Leave Management'
        WHEN tablename LIKE '%expense%' OR tablename LIKE '%vendor%' OR tablename LIKE '%purchase%' THEN 'Expense Management'
        ELSE 'Other'
    END AS category
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY category, tablename;

-- Commit the transaction
COMMIT;

-- =====================================================
-- Success Messages
-- =====================================================

SELECT 'Database schema created successfully!' AS result;
SELECT 'All tables, indexes, constraints, and views have been created' AS details;
SELECT 'Next step: Run 02_load_initial_data.sql to populate with initial data' AS next_step;
