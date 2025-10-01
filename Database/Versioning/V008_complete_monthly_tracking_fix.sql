-- Complete Monthly Tracking Fix
-- This script fixes all issues with the monthly tracking functionality

-- =====================================================
-- Step 1: Fix the enable_monthly_tracking_for_record function
-- =====================================================

CREATE OR REPLACE FUNCTION enable_monthly_tracking_for_record(
    p_fee_record_id INTEGER,
    p_start_month INTEGER DEFAULT 4, -- April
    p_start_year INTEGER DEFAULT NULL
)
RETURNS INTEGER AS $$
DECLARE
    fee_record RECORD;
    monthly_amount DECIMAL(10,2);
    current_month INTEGER;
    current_year INTEGER;
    due_date DATE;
    records_created INTEGER := 0;
    month_counter INTEGER := 0;
    month_names TEXT[] := ARRAY['January','February','March','April','May','June',
                               'July','August','September','October','November','December'];
    existing_count INTEGER;
BEGIN
    -- Get fee record details
    SELECT fr.*, fs.total_annual_fee
    INTO fee_record
    FROM fee_records fr
    LEFT JOIN fee_structures fs ON fr.student_id IN (
        SELECT id FROM students WHERE class_id = fs.class_id AND session_year_id = fs.session_year_id
    )
    WHERE fr.id = p_fee_record_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Fee record with ID % not found', p_fee_record_id;
    END IF;
    
    -- Check if monthly tracking is already enabled
    IF fee_record.is_monthly_tracked = TRUE THEN
        -- Count existing records
        SELECT COUNT(*) INTO existing_count
        FROM monthly_fee_tracking 
        WHERE fee_record_id = p_fee_record_id;
        
        RETURN existing_count;
    END IF;
    
    -- Calculate monthly amount
    monthly_amount := COALESCE(fee_record.total_annual_fee, fee_record.total_amount) / 12;
    
    -- Set starting year
    current_year := COALESCE(p_start_year, EXTRACT(YEAR FROM CURRENT_DATE));
    current_month := p_start_month;
    
    -- Create 12 monthly tracking records
    FOR month_counter IN 0..11 LOOP
        -- Calculate due date
        due_date := DATE(current_year || '-' || LPAD(current_month::TEXT, 2, '0') || '-10');
        
        -- Check if record already exists
        SELECT COUNT(*) INTO existing_count
        FROM monthly_fee_tracking 
        WHERE fee_record_id = p_fee_record_id 
        AND academic_month = current_month 
        AND academic_year = current_year;
        
        -- Insert only if record doesn't exist
        IF existing_count = 0 THEN
            INSERT INTO monthly_fee_tracking (
                fee_record_id,
                student_id,
                session_year_id,
                academic_month,
                academic_year,
                month_name,
                monthly_amount,
                due_date,
                payment_status_id
            ) VALUES (
                p_fee_record_id,
                fee_record.student_id,
                fee_record.session_year_id,
                current_month,
                current_year,
                month_names[current_month],
                monthly_amount,
                due_date,
                1 -- Pending
            );
            
            records_created := records_created + 1;
        END IF;
        
        -- Move to next month
        current_month := current_month + 1;
        IF current_month > 12 THEN
            current_month := 1;
            current_year := current_year + 1;
        END IF;
    END LOOP;
    
    -- Mark fee record as monthly tracked
    UPDATE fee_records 
    SET is_monthly_tracked = TRUE 
    WHERE id = p_fee_record_id;
    
    RETURN records_created;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION enable_monthly_tracking_for_record IS 'Safely enables monthly tracking for existing fee records with proper record counting';

-- =====================================================
-- Step 2: Fix the enhanced_student_fee_status view
-- =====================================================

-- Drop existing view if it exists
DROP VIEW IF EXISTS enhanced_student_fee_status CASCADE;

-- Create the updated view with proper monthly tracking logic
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
    
    -- Monthly tracking data (if available)
    COALESCE(monthly_stats.total_months_tracked, 0) as total_months_tracked,
    COALESCE(monthly_stats.paid_months, 0) as paid_months,
    COALESCE(monthly_stats.pending_months, 0) as pending_months,
    COALESCE(monthly_stats.overdue_months, 0) as overdue_months,
    COALESCE(monthly_stats.monthly_total, 0) as monthly_total,
    COALESCE(monthly_stats.monthly_paid, 0) as monthly_paid,
    COALESCE(monthly_stats.monthly_balance, 0) as monthly_balance,
    
    -- Collection percentage
    CASE 
        WHEN fr.total_amount > 0 THEN 
            ROUND((fr.paid_amount * 100.0 / fr.total_amount), 2)
        ELSE 0 
    END as collection_percentage,
    
    -- Has monthly tracking enabled - FIXED LOGIC
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

WHERE s.is_active = true
  AND (s.is_deleted = false OR s.is_deleted IS NULL);

COMMENT ON VIEW enhanced_student_fee_status IS 'Enhanced student fee summary - Fixed to properly handle monthly tracking status';

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_enhanced_fee_status_session_year 
ON students(session_year_id) WHERE is_active = true AND (is_deleted = false OR is_deleted IS NULL);

CREATE INDEX IF NOT EXISTS idx_enhanced_fee_status_class 
ON students(class_id) WHERE is_active = true AND (is_deleted = false OR is_deleted IS NULL);

-- Grant permissions
GRANT SELECT ON enhanced_student_fee_status TO PUBLIC;

-- =====================================================
-- Step 3: Test the fix
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
    total_months_tracked,
    fee_record_id
FROM enhanced_student_fee_status 
WHERE session_year = '2025-26'
LIMIT 5;
