-- Fix for the enable_monthly_tracking_for_record function
-- This addresses the issue with record counting when using ON CONFLICT DO NOTHING

-- Drop and recreate the function with improved logic
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
