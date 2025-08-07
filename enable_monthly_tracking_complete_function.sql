-- Complete Enable Monthly Tracking Function
-- This function handles the complete workflow including fee record creation
-- Run this SQL script directly against your database

CREATE OR REPLACE FUNCTION enable_monthly_tracking_complete(
    p_student_ids INTEGER[],
    p_session_year_id INTEGER DEFAULT 4,
    p_start_month INTEGER DEFAULT 4,
    p_start_year INTEGER DEFAULT NULL
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
    student_record RECORD;
    v_fee_record_id INTEGER;  -- Renamed to avoid column name conflict
    fee_structure_record RECORD;
    monthly_amount DECIMAL(10,2);
    current_month INTEGER;
    current_year INTEGER;
    due_date DATE;
    records_created INTEGER := 0;
    month_counter INTEGER := 0;
    month_names TEXT[] := ARRAY['January','February','March','April','May','June',
                               'July','August','September','October','November','December'];
    existing_count INTEGER;
    fee_created BOOLEAN := FALSE;
BEGIN
    -- Set starting year
    current_year := COALESCE(p_start_year, EXTRACT(YEAR FROM CURRENT_DATE));
    
    -- Process each student
    FOR student_record IN 
        SELECT s.id, s.first_name || ' ' || s.last_name as name, s.class_id
        FROM students s 
        WHERE s.id = ANY(p_student_ids) 
        AND s.is_active = true 
        AND (s.is_deleted = false OR s.is_deleted IS NULL)
    LOOP
        fee_created := FALSE;
        records_created := 0;
        
        -- Check if student already has a fee record for this session
        SELECT fr.id INTO v_fee_record_id
        FROM fee_records fr
        WHERE fr.student_id = student_record.id
        AND fr.session_year_id = p_session_year_id;

        -- If no fee record exists, create one
        IF v_fee_record_id IS NULL THEN
            -- Get fee structure for student's class
            SELECT fs.* INTO fee_structure_record
            FROM fee_structures fs
            WHERE fs.class_id = student_record.class_id 
            AND fs.session_year_id = p_session_year_id;
            
            IF fee_structure_record IS NULL THEN
                -- Return error for this student
                student_id := student_record.id;
                student_name := student_record.name;
                fee_record_id := NULL;
                fee_record_created := FALSE;
                monthly_records_created := 0;
                success := FALSE;
                message := 'No fee structure found for student class';
                RETURN NEXT;
                CONTINUE;
            END IF;
            
            -- Create fee record (balance_amount will be calculated automatically)
            INSERT INTO fee_records (
                student_id,
                session_year_id,
                payment_type_id,
                payment_status_id,
                payment_method_id,
                fee_structure_id,
                is_monthly_tracked,
                total_amount,
                paid_amount,
                due_date,
                remarks,
                created_at
            ) VALUES (
                student_record.id,
                p_session_year_id,
                1, -- Monthly payment type
                1, -- Pending status
                1, -- Default payment method
                fee_structure_record.id,
                TRUE, -- Enable monthly tracking
                fee_structure_record.total_annual_fee,
                0,
                DATE(current_year || '-04-30'), -- April 30th due date
                'Auto-created for monthly tracking',
                NOW()
            ) RETURNING id INTO v_fee_record_id;

            fee_created := TRUE;
        ELSE
            -- Update existing fee record to enable monthly tracking
            UPDATE fee_records
            SET is_monthly_tracked = TRUE
            WHERE id = v_fee_record_id;

            -- Get fee structure for monthly amount calculation
            SELECT fs.* INTO fee_structure_record
            FROM fee_structures fs
            JOIN fee_records fr ON fs.id = fr.fee_structure_id
            WHERE fr.id = v_fee_record_id;
            
            IF fee_structure_record IS NULL THEN
                -- Fallback: get by class and session
                SELECT fs.* INTO fee_structure_record
                FROM fee_structures fs
                WHERE fs.class_id = student_record.class_id 
                AND fs.session_year_id = p_session_year_id;
            END IF;
        END IF;
        
        -- Calculate monthly amount
        monthly_amount := COALESCE(fee_structure_record.total_annual_fee, 50000) / 12;
        
        -- Create 12 monthly tracking records
        current_month := p_start_month;
        FOR month_counter IN 0..11 LOOP
            -- Calculate due date
            due_date := DATE(current_year || '-' || LPAD(current_month::TEXT, 2, '0') || '-10');
            
            -- Check if record already exists
            SELECT COUNT(*) INTO existing_count
            FROM monthly_fee_tracking mft
            WHERE mft.fee_record_id = v_fee_record_id
            AND mft.academic_month = current_month
            AND mft.academic_year = current_year;
            
            -- Insert only if record doesn't exist (balance_amount is auto-calculated)
            IF existing_count = 0 THEN
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
                    created_at
                ) VALUES (
                    v_fee_record_id,
                    student_record.id,
                    p_session_year_id,
                    current_month,
                    current_year,
                    month_names[current_month],
                    monthly_amount,
                    0,
                    due_date,
                    1, -- Pending
                    NOW()
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
        
        -- Return success result for this student
        student_id := student_record.id;
        student_name := student_record.name;
        fee_record_id := v_fee_record_id;  -- Use the local variable
        fee_record_created := fee_created;
        monthly_records_created := records_created;
        success := TRUE;
        message := CASE
            WHEN fee_created THEN 'Fee record created and monthly tracking enabled'
            ELSE 'Monthly tracking enabled for existing fee record'
        END;
        RETURN NEXT;
        
    END LOOP;
    
    RETURN;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION enable_monthly_tracking_complete IS 'Complete monthly tracking enablement including fee record creation';

-- Test the function exists
SELECT 'Function created successfully!' as status 
WHERE EXISTS (
    SELECT 1 FROM pg_proc 
    WHERE proname = 'enable_monthly_tracking_complete'
);
