-- =====================================================
-- Function: enable_monthly_tracking_complete
-- Description: Complete monthly tracking enablement for students
--              Creates fee records if needed and generates 12 monthly tracking records
-- Parameters: 
--   p_student_ids INTEGER[] - Array of student IDs
--   p_session_year_id INTEGER - Session year ID (e.g., 4 for 2025-26)
--   p_start_month INTEGER - Starting academic month (default: 4 for April)
--   p_start_year INTEGER - Starting academic year (e.g., 2025)
-- Returns: TABLE with results for each student
-- Dependencies: students, fee_records, fee_structures, monthly_fee_tracking
-- =====================================================

-- Drop existing function
DROP FUNCTION IF EXISTS enable_monthly_tracking_complete(INTEGER[], INTEGER, INTEGER, INTEGER);

-- Create function
CREATE OR REPLACE FUNCTION enable_monthly_tracking_complete(
    p_student_ids INTEGER[],
    p_session_year_id INTEGER,
    p_start_month INTEGER DEFAULT 4,
    p_start_year INTEGER DEFAULT EXTRACT(YEAR FROM CURRENT_DATE)::INTEGER
)
RETURNS TABLE(
    student_id INTEGER,
    student_name TEXT,
    fee_record_id INTEGER,
    fee_record_created BOOLEAN,
    monthly_records_created INTEGER,
    success BOOLEAN,
    message TEXT
) AS $$
DECLARE
    v_student_id INTEGER;
    v_student RECORD;
    v_fee_record RECORD;
    v_fee_structure RECORD;
    v_fee_record_id INTEGER;
    v_fee_record_created BOOLEAN;
    v_monthly_records_created INTEGER;
    v_student_name TEXT;
    v_monthly_fee DECIMAL(10,2);
    v_month INTEGER;
    v_year INTEGER;
    v_month_name TEXT;
    v_due_date DATE;
    v_academic_months INTEGER[] := ARRAY[4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3];
    v_month_names TEXT[] := ARRAY['April', 'May', 'June', 'July', 'August', 'September', 
                                    'October', 'November', 'December', 'January', 'February', 'March'];
    v_existing_count INTEGER;
BEGIN
    -- Loop through each student ID
    FOREACH v_student_id IN ARRAY p_student_ids
    LOOP
        v_fee_record_created := FALSE;
        v_monthly_records_created := 0;
        
        BEGIN
            -- Get student details
            SELECT 
                s.id,
                s.first_name || ' ' || s.last_name as full_name,
                s.class_id,
                s.session_year_id
            INTO v_student
            FROM students s
            WHERE s.id = v_student_id;
            
            IF NOT FOUND THEN
                -- Student not found
                student_id := v_student_id;
                student_name := 'Unknown';
                fee_record_id := NULL;
                fee_record_created := FALSE;
                monthly_records_created := 0;
                success := FALSE;
                message := 'Student not found';
                RETURN NEXT;
                CONTINUE;
            END IF;
            
            v_student_name := v_student.full_name;
            
            -- Check if fee record already exists
            SELECT 
                fr.id,
                fr.total_amount,
                fr.is_monthly_tracked
            INTO v_fee_record
            FROM fee_records fr
            WHERE fr.student_id = v_student_id
              AND fr.session_year_id = p_session_year_id;
            
            IF FOUND THEN
                -- Fee record exists
                v_fee_record_id := v_fee_record.id;
                v_fee_record_created := FALSE;
                
                -- Update to enable monthly tracking if not already enabled
                IF NOT v_fee_record.is_monthly_tracked THEN
                    UPDATE fee_records
                    SET is_monthly_tracked = TRUE,
                        updated_at = NOW()
                    WHERE id = v_fee_record_id;
                END IF;
                
                -- Calculate monthly fee from annual fee
                v_monthly_fee := ROUND(v_fee_record.total_amount / 12, 2);
            ELSE
                -- Fee record doesn't exist, create it
                -- First, get fee structure for this class and session
                SELECT
                    fs.id,
                    fs.amount
                INTO v_fee_structure
                FROM fee_structures fs
                WHERE fs.class_id = v_student.class_id
                  AND fs.session_year_id = p_session_year_id
                  AND fs.is_active = TRUE
                LIMIT 1;

                IF NOT FOUND THEN
                    -- No fee structure found, use default
                    v_monthly_fee := 1000.00; -- Default monthly fee
                ELSE
                    v_monthly_fee := ROUND(v_fee_structure.amount / 12, 2);
                END IF;
                
                -- Create fee record
                INSERT INTO fee_records (
                    student_id,
                    session_year_id,
                    class_id,
                    total_amount,
                    paid_amount,
                    balance_amount,
                    payment_type_id,
                    payment_status_id,
                    due_date,
                    is_monthly_tracked,
                    is_active,
                    created_at
                ) VALUES (
                    v_student_id,
                    p_session_year_id,
                    v_student.class_id,
                    v_monthly_fee * 12, -- Annual fee
                    0.00,
                    v_monthly_fee * 12, -- Balance = Total initially
                    2, -- Monthly payment type
                    1, -- Pending status
                    DATE(p_start_year || '-' || LPAD(p_start_month::TEXT, 2, '0') || '-10'), -- Due date: 10th of start month
                    TRUE, -- Enable monthly tracking
                    TRUE,
                    NOW()
                )
                RETURNING id INTO v_fee_record_id;
                
                v_fee_record_created := TRUE;
            END IF;
            
            -- Check if monthly tracking records already exist
            SELECT COUNT(*)
            INTO v_existing_count
            FROM monthly_fee_tracking mft
            WHERE mft.student_id = v_student_id
              AND mft.session_year_id = p_session_year_id;
            
            IF v_existing_count > 0 THEN
                -- Records already exist, don't create duplicates
                student_id := v_student_id;
                student_name := v_student_name;
                fee_record_id := v_fee_record_id;
                fee_record_created := v_fee_record_created;
                monthly_records_created := 0;
                success := TRUE;
                message := 'Monthly tracking already enabled (' || v_existing_count || ' records exist)';
                RETURN NEXT;
                CONTINUE;
            END IF;
            
            -- Create 12 monthly tracking records (April to March)
            FOR i IN 1..12
            LOOP
                v_month := v_academic_months[i];
                v_month_name := v_month_names[i];
                
                -- Calculate year (April-December = start_year, January-March = start_year+1)
                IF v_month >= 4 THEN
                    v_year := p_start_year;
                ELSE
                    v_year := p_start_year + 1;
                END IF;
                
                -- Calculate due date (10th of each month)
                v_due_date := DATE(v_year || '-' || LPAD(v_month::TEXT, 2, '0') || '-10');
                
                -- Insert monthly tracking record
                INSERT INTO monthly_fee_tracking (
                    fee_record_id,
                    student_id,
                    session_year_id,
                    academic_month,
                    academic_year,
                    month_name,
                    monthly_amount,
                    paid_amount,
                    due_date,
                    payment_status_id,
                    late_fee,
                    discount_amount,
                    created_at
                ) VALUES (
                    v_fee_record_id,
                    v_student_id,
                    p_session_year_id,
                    v_month,
                    v_year,
                    v_month_name,
                    v_monthly_fee,
                    0.00, -- Initially unpaid
                    v_due_date,
                    1, -- Pending status
                    0.00, -- No late fee initially
                    0.00, -- No discount initially
                    NOW()
                ); -- Remove ON CONFLICT for now to avoid ambiguous column reference
                
                -- Increment counter if insert was successful
                IF FOUND THEN
                    v_monthly_records_created := v_monthly_records_created + 1;
                END IF;
            END LOOP;
            
            -- Return success result
            student_id := v_student_id;
            student_name := v_student_name;
            fee_record_id := v_fee_record_id;
            fee_record_created := v_fee_record_created;
            monthly_records_created := v_monthly_records_created;
            success := TRUE;
            message := 'Monthly tracking enabled successfully';
            RETURN NEXT;
            
        EXCEPTION WHEN OTHERS THEN
            -- Handle any errors for this student
            student_id := v_student_id;
            student_name := COALESCE(v_student_name, 'Unknown');
            fee_record_id := NULL;
            fee_record_created := FALSE;
            monthly_records_created := 0;
            success := FALSE;
            message := 'Error: ' || SQLERRM;
            RETURN NEXT;
        END;
    END LOOP;
    
    RETURN;
END;
$$ LANGUAGE plpgsql;

-- Add comment
COMMENT ON FUNCTION enable_monthly_tracking_complete(INTEGER[], INTEGER, INTEGER, INTEGER) IS 
'Complete monthly tracking enablement: creates fee records if needed and generates 12 monthly tracking records (April-March) for each student';

