-- =====================================================
-- Fix Monthly Tracking Functionality
-- Issue: Views not handling soft delete columns properly
-- Date: 2025-08-04
-- =====================================================

-- First, let's check if the soft delete columns exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'students' AND column_name = 'is_deleted'
    ) THEN
        RAISE NOTICE 'Adding is_deleted column to students table...';
        ALTER TABLE students ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE;
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'students' AND column_name = 'deleted_date'
    ) THEN
        RAISE NOTICE 'Adding deleted_date column to students table...';
        ALTER TABLE students ADD COLUMN deleted_date TIMESTAMP WITH TIME ZONE;
    END IF;
END $$;

-- Update existing records to ensure is_deleted is FALSE
UPDATE students 
SET is_deleted = FALSE 
WHERE is_deleted IS NULL;

-- Create indexes if they don't exist
CREATE INDEX IF NOT EXISTS idx_students_is_deleted ON students(is_deleted);
CREATE INDEX IF NOT EXISTS idx_students_deleted_date ON students(deleted_date);

-- =====================================================
-- Fix the enhanced_student_fee_status view
-- =====================================================

-- Drop existing view
DROP VIEW IF EXISTS enhanced_student_fee_status CASCADE;

-- Create the updated view with proper soft delete handling
CREATE OR REPLACE VIEW enhanced_student_fee_status AS
SELECT 
    s.id as student_id,
    s.admission_number,
    s.first_name || ' ' || s.last_name as student_name,
    c.display_name as class_name,
    sy.name as session_year,
    
    -- From existing fee_records
    fr.id as fee_record_id,
    fr.total_amount as annual_fee,
    fr.paid_amount as total_paid,
    fr.balance_amount as total_balance,
    
    -- Monthly tracking statistics
    COALESCE(monthly_stats.total_months_tracked, 0) as total_months_tracked,
    COALESCE(monthly_stats.paid_months, 0) as paid_months,
    COALESCE(monthly_stats.pending_months, 0) as pending_months,
    COALESCE(monthly_stats.overdue_months, 0) as overdue_months,
    COALESCE(monthly_stats.monthly_total, 0) as monthly_total,
    COALESCE(monthly_stats.monthly_paid, 0) as monthly_paid,
    COALESCE(monthly_stats.monthly_balance, 0) as monthly_balance,
    
    -- Collection percentage
    CASE 
        WHEN COALESCE(monthly_stats.monthly_total, 0) > 0 THEN
            ROUND((COALESCE(monthly_stats.monthly_paid, 0) / monthly_stats.monthly_total) * 100, 2)
        WHEN fr.total_amount > 0 THEN
            ROUND((fr.paid_amount / fr.total_amount) * 100, 2)
        ELSE 0
    END as collection_percentage,
    
    -- Has monthly tracking enabled
    CASE 
        WHEN monthly_stats.total_months_tracked > 0 THEN true
        WHEN fr.is_monthly_tracked = true THEN true
        ELSE false
    END as has_monthly_tracking

FROM students s
LEFT JOIN classes c ON s.class_id = c.id
LEFT JOIN session_years sy ON s.session_year_id = sy.id
LEFT JOIN fee_records fr ON s.id = fr.student_id AND s.session_year_id = fr.session_year_id
LEFT JOIN (
    -- Subquery to get monthly tracking statistics
    SELECT 
        mft.student_id,
        mft.session_year_id,
        COUNT(*) as total_months_tracked,
        COUNT(CASE WHEN ps.name = 'PAID' THEN 1 END) as paid_months,
        COUNT(CASE WHEN ps.name = 'PENDING' THEN 1 END) as pending_months,
        COUNT(CASE WHEN ps.name = 'OVERDUE' THEN 1 END) as overdue_months,
        SUM(mft.monthly_amount) as monthly_total,
        SUM(mft.paid_amount) as monthly_paid,
        SUM(mft.balance_amount) as monthly_balance
    FROM monthly_fee_tracking mft
    LEFT JOIN payment_statuses ps ON mft.payment_status_id = ps.id
    GROUP BY mft.student_id, mft.session_year_id
) monthly_stats ON s.id = monthly_stats.student_id AND s.session_year_id = monthly_stats.session_year_id

-- CRITICAL FIX: Properly exclude soft-deleted students
WHERE s.is_active = true 
  AND (s.is_deleted = false OR s.is_deleted IS NULL);

COMMENT ON VIEW enhanced_student_fee_status IS 'Enhanced student fee summary - Fixed to handle soft delete columns';

-- Grant permissions
GRANT SELECT ON enhanced_student_fee_status TO PUBLIC;

-- =====================================================
-- Test the fix
-- =====================================================

-- Check if the view is working
SELECT 
    'enhanced_student_fee_status' as view_name,
    COUNT(*) as total_students,
    COUNT(CASE WHEN has_monthly_tracking THEN 1 END) as students_with_tracking
FROM enhanced_student_fee_status 
WHERE session_year = '2025-26';

-- Show some sample data
SELECT 
    student_id,
    student_name,
    class_name,
    has_monthly_tracking,
    total_months_tracked
FROM enhanced_student_fee_status 
WHERE session_year = '2025-26'
LIMIT 5;

-- =====================================================
-- Success message
-- =====================================================
SELECT 'Monthly tracking fix applied successfully! The enhanced_student_fee_status view now properly excludes soft-deleted students.' as status;
