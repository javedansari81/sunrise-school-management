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
    v_session_start_year INTEGER; -- Derived from session_years table
    -- Sibling waiver variables
    v_sibling_count INTEGER;
    v_birth_order INTEGER;
    v_waiver_percentage DECIMAL(5,2);
    v_waiver_reason TEXT;
    v_original_monthly_fee DECIMAL(10,2);
    v_waived_monthly_fee DECIMAL(10,2);
    v_original_total_fee DECIMAL(10,2);
    v_waived_total_fee DECIMAL(10,2);
BEGIN
    -- ALWAYS derive the start year from the session_years table
    -- This ensures the year is correct for past, current, or future session years
    -- Never use current date as it can lead to incorrect year calculations
    SELECT EXTRACT(YEAR FROM sy.start_date)::INTEGER
    INTO v_session_start_year
    FROM session_years sy
    WHERE sy.id = p_session_year_id;

    -- If session year not found, raise an error - session year must exist in the database
    IF v_session_start_year IS NULL THEN
        RAISE EXCEPTION 'Session year ID % not found in session_years table', p_session_year_id;
    END IF;

    -- Loop through each student ID
    FOREACH v_student_id IN ARRAY p_student_ids
    LOOP
        v_fee_record_created := FALSE;
        v_monthly_records_created := 0;

        BEGIN
            -- Get student details (including date_of_birth for sibling birth order calculation)
            SELECT
                s.id,
                s.first_name || ' ' || s.last_name as full_name,
                s.class_id,
                s.session_year_id,
                s.date_of_birth
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

            -- Check for sibling waiver
            v_waiver_percentage := 0.00;
            v_waiver_reason := NULL;
            v_birth_order := 1;

            -- Get sibling information for this student
            -- IMPORTANT: Only count siblings who are ACTIVE and in the SAME SESSION YEAR
            -- This ensures discounts are only applied when siblings are actually studying together
            -- in the same academic year (e.g., if sibling left school or not yet promoted, no discount)
            SELECT COUNT(*) INTO v_sibling_count
            FROM student_siblings ss
            INNER JOIN students sibling_student ON sibling_student.id = ss.sibling_student_id
            WHERE ss.student_id = v_student_id
              AND ss.is_active = TRUE
              AND sibling_student.session_year_id = p_session_year_id
              AND sibling_student.is_active = TRUE
              AND (sibling_student.is_deleted = FALSE OR sibling_student.is_deleted IS NULL);

            -- Add 1 for the current student to get total siblings count
            v_sibling_count := v_sibling_count + 1;

            -- If student has siblings in the same session year, calculate waiver dynamically
            IF v_sibling_count > 1 THEN
                -- Calculate birth order for this student among siblings in the same session year
                -- Birth order = count of older siblings in same session + 1
                -- Older siblings have earlier date_of_birth
                SELECT COUNT(*) + 1 INTO v_birth_order
                FROM student_siblings ss
                INNER JOIN students sibling_student ON sibling_student.id = ss.sibling_student_id
                WHERE ss.student_id = v_student_id
                  AND ss.is_active = TRUE
                  AND sibling_student.session_year_id = p_session_year_id
                  AND sibling_student.is_active = TRUE
                  AND (sibling_student.is_deleted = FALSE OR sibling_student.is_deleted IS NULL)
                  AND sibling_student.date_of_birth < v_student.date_of_birth;

                -- Calculate waiver percentage using the database function
                v_waiver_percentage := calculate_sibling_fee_waiver(v_sibling_count, v_birth_order);

                -- Get waiver reason text
                IF v_waiver_percentage > 0 THEN
                    v_waiver_reason := get_waiver_reason_text(v_sibling_count, v_birth_order, v_waiver_percentage);
                END IF;
            END IF;

            -- Check if fee record already exists
            SELECT
                fr.id,
                fr.total_amount,
                fr.original_total_amount,
                fr.is_monthly_tracked
            INTO v_fee_record
            FROM fee_records fr
            WHERE fr.student_id = v_student_id
              AND fr.session_year_id = p_session_year_id;

            IF FOUND THEN
                -- Fee record exists
                v_fee_record_id := v_fee_record.id;
                v_fee_record_created := FALSE;

                -- Use original_total_amount if available (pre-waiver amount), otherwise use total_amount
                -- This ensures we always calculate waiver from the original fee, not a previously waived amount
                v_original_total_fee := COALESCE(v_fee_record.original_total_amount, v_fee_record.total_amount);
                v_original_monthly_fee := ROUND(v_original_total_fee / 12, 2);

                -- Apply sibling waiver if applicable
                IF v_waiver_percentage > 0 THEN
                    v_waived_monthly_fee := ROUND(v_original_monthly_fee * (100 - v_waiver_percentage) / 100, 2);
                    v_waived_total_fee := v_waived_monthly_fee * 12;
                ELSE
                    v_waived_monthly_fee := v_original_monthly_fee;
                    v_waived_total_fee := v_original_total_fee;
                END IF;

                v_monthly_fee := v_waived_monthly_fee;

                -- Update fee record with sibling waiver info
                UPDATE fee_records
                SET is_monthly_tracked = TRUE,
                    has_sibling_waiver = (v_waiver_percentage > 0),
                    sibling_waiver_percentage = v_waiver_percentage,
                    original_total_amount = CASE WHEN v_waiver_percentage > 0 THEN v_original_total_fee ELSE NULL END,
                    total_amount = v_waived_total_fee,
                    balance_amount = v_waived_total_fee - COALESCE(paid_amount, 0),
                    updated_at = NOW()
                WHERE id = v_fee_record_id;
            ELSE
                -- Fee record doesn't exist, create it
                -- First, get fee structure for this class and session
                SELECT
                    fs.id,
                    fs.total_annual_fee
                INTO v_fee_structure
                FROM fee_structures fs
                WHERE fs.class_id = v_student.class_id
                  AND fs.session_year_id = p_session_year_id
                LIMIT 1;

                IF NOT FOUND THEN
                    -- No fee structure found, use default
                    v_original_monthly_fee := 1000.00; -- Default monthly fee
                ELSE
                    v_original_monthly_fee := ROUND(v_fee_structure.total_annual_fee / 12, 2);
                END IF;

                v_original_total_fee := v_original_monthly_fee * 12;

                -- Apply sibling waiver if applicable
                IF v_waiver_percentage > 0 THEN
                    v_waived_monthly_fee := ROUND(v_original_monthly_fee * (100 - v_waiver_percentage) / 100, 2);
                    v_waived_total_fee := v_waived_monthly_fee * 12;
                ELSE
                    v_waived_monthly_fee := v_original_monthly_fee;
                    v_waived_total_fee := v_original_total_fee;
                END IF;

                v_monthly_fee := v_waived_monthly_fee;

                -- Create fee record with sibling waiver info
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
                    has_sibling_waiver,
                    sibling_waiver_percentage,
                    original_total_amount,
                    is_active,
                    created_at
                ) VALUES (
                    v_student_id,
                    p_session_year_id,
                    v_student.class_id,
                    v_waived_total_fee, -- Annual fee after waiver
                    0.00,
                    v_waived_total_fee, -- Balance = Total initially
                    2, -- Monthly payment type
                    1, -- Pending status
                    DATE(v_session_start_year || '-' || LPAD(p_start_month::TEXT, 2, '0') || '-10'), -- Due date: 10th of start month
                    TRUE, -- Enable monthly tracking
                    (v_waiver_percentage > 0), -- Has sibling waiver
                    v_waiver_percentage,
                    CASE WHEN v_waiver_percentage > 0 THEN v_original_total_fee ELSE NULL END,
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
                -- Records already exist, check if waiver has changed
                DECLARE
                    v_old_waiver_percentage DECIMAL(5,2);
                    v_updated_count INTEGER := 0;
                    v_new_monthly_amount DECIMAL(10,2);
                    v_original_amount DECIMAL(10,2);
                BEGIN
                    -- Get the waiver percentage from existing records
                    SELECT COALESCE(mft.fee_waiver_percentage, 0)
                    INTO v_old_waiver_percentage
                    FROM monthly_fee_tracking mft
                    WHERE mft.student_id = v_student_id
                      AND mft.session_year_id = p_session_year_id
                    LIMIT 1;

                    -- Check if waiver has changed
                    IF v_old_waiver_percentage != v_waiver_percentage THEN
                        -- Waiver has changed, update unpaid records
                        -- Get original monthly amount (before any waiver)
                        -- Priority: 1) fee_records.original_total_amount, 2) fee_structure, 3) monthly_tracking, 4) default

                        -- First try to get from fee_records.original_total_amount
                        SELECT COALESCE(fr.original_total_amount, fr.total_amount) / 12
                        INTO v_original_amount
                        FROM fee_records fr
                        WHERE fr.student_id = v_student_id
                          AND fr.session_year_id = p_session_year_id
                          AND COALESCE(fr.original_total_amount, fr.total_amount) > 0;

                        -- If fee_records doesn't have valid original amount, get from fee structure
                        IF v_original_amount IS NULL OR v_original_amount = 0 THEN
                            SELECT fs.total_annual_fee / 12
                            INTO v_original_amount
                            FROM fee_structures fs
                            WHERE fs.class_id = v_student.class_id
                              AND fs.session_year_id = p_session_year_id
                            LIMIT 1;
                        END IF;

                        -- If still no valid amount, get from monthly tracking
                        IF v_original_amount IS NULL OR v_original_amount = 0 THEN
                            SELECT COALESCE(mft.original_monthly_amount, mft.monthly_amount)
                            INTO v_original_amount
                            FROM monthly_fee_tracking mft
                            WHERE mft.student_id = v_student_id
                              AND mft.session_year_id = p_session_year_id
                              AND COALESCE(mft.original_monthly_amount, mft.monthly_amount) > 0
                            LIMIT 1;
                        END IF;

                        -- If still no amount found, use default
                        IF v_original_amount IS NULL OR v_original_amount = 0 THEN
                            v_original_amount := 1000.00; -- Default monthly fee
                        END IF;

                        -- Calculate new monthly amount with updated waiver
                        IF v_waiver_percentage > 0 THEN
                            v_new_monthly_amount := ROUND(v_original_amount * (100 - v_waiver_percentage) / 100, 2);
                        ELSE
                            v_new_monthly_amount := v_original_amount;
                        END IF;

                        -- Update unpaid monthly tracking records
                        UPDATE monthly_fee_tracking mft
                        SET monthly_amount = v_new_monthly_amount,
                            original_monthly_amount = v_original_amount,
                            fee_waiver_percentage = v_waiver_percentage,
                            waiver_reason = v_waiver_reason,
                            updated_at = NOW()
                        WHERE mft.student_id = v_student_id
                          AND mft.session_year_id = p_session_year_id
                          AND mft.payment_status_id = 1; -- Only update unpaid records

                        GET DIAGNOSTICS v_updated_count = ROW_COUNT;

                        -- Also update the fee_records table with new totals
                        DECLARE
                            v_new_total_amount DECIMAL(10,2);
                            v_original_total_amount DECIMAL(10,2);
                            v_current_paid_amount DECIMAL(10,2);
                        BEGIN
                            -- Calculate original annual total (sum of all original monthly amounts)
                            SELECT SUM(COALESCE(mft.original_monthly_amount, mft.monthly_amount))
                            INTO v_original_total_amount
                            FROM monthly_fee_tracking mft
                            WHERE mft.student_id = v_student_id
                              AND mft.session_year_id = p_session_year_id;

                            -- Calculate new annual total using waiver percentage
                            -- total_amount = original_total_amount * (100 - waiver_percentage) / 100
                            IF v_waiver_percentage > 0 THEN
                                v_new_total_amount := ROUND(v_original_total_amount * (100 - v_waiver_percentage) / 100, 2);
                            ELSE
                                v_new_total_amount := v_original_total_amount;
                            END IF;

                            -- Get current paid amount from fee_records
                            SELECT COALESCE(fr.paid_amount, 0)
                            INTO v_current_paid_amount
                            FROM fee_records fr
                            WHERE fr.student_id = v_student_id
                              AND fr.session_year_id = p_session_year_id;

                            -- Update fee_records with new totals
                            UPDATE fee_records fr
                            SET total_amount = v_new_total_amount,
                                original_total_amount = v_original_total_amount,
                                balance_amount = v_new_total_amount - v_current_paid_amount,
                                has_sibling_waiver = (v_waiver_percentage > 0),
                                sibling_waiver_percentage = v_waiver_percentage,
                                updated_at = NOW()
                            WHERE fr.student_id = v_student_id
                              AND fr.session_year_id = p_session_year_id;
                        END;

                        -- Return success with update information
                        student_id := v_student_id;
                        student_name := v_student_name;
                        fee_record_id := v_fee_record_id;
                        fee_record_created := v_fee_record_created;
                        monthly_records_created := v_updated_count;
                        success := TRUE;
                        message := 'Waiver updated from ' || v_old_waiver_percentage || '% to ' || v_waiver_percentage || '% (' || v_updated_count || ' unpaid records updated)';
                        RETURN NEXT;
                        CONTINUE;
                    ELSE
                        -- Waiver hasn't changed, records already exist
                        student_id := v_student_id;
                        student_name := v_student_name;
                        fee_record_id := v_fee_record_id;
                        fee_record_created := v_fee_record_created;
                        monthly_records_created := 0;
                        success := TRUE;
                        message := 'Monthly tracking already enabled (' || v_existing_count || ' records exist, waiver unchanged)';
                        RETURN NEXT;
                        CONTINUE;
                    END IF;
                END;
            END IF;
            
            -- Create 12 monthly tracking records (April to March)
            FOR i IN 1..12
            LOOP
                v_month := v_academic_months[i];
                v_month_name := v_month_names[i];
                
                -- Calculate year using session start year (April-December = start_year, January-March = start_year+1)
                -- Uses v_session_start_year derived from session_years table for accuracy
                IF v_month >= 4 THEN
                    v_year := v_session_start_year;
                ELSE
                    v_year := v_session_start_year + 1;
                END IF;
                
                -- Calculate due date (10th of each month)
                v_due_date := DATE(v_year || '-' || LPAD(v_month::TEXT, 2, '0') || '-10');
                
                -- Insert monthly tracking record with sibling waiver info
                INSERT INTO monthly_fee_tracking (
                    fee_record_id,
                    student_id,
                    session_year_id,
                    academic_month,
                    academic_year,
                    month_name,
                    monthly_amount,
                    original_monthly_amount,
                    fee_waiver_percentage,
                    waiver_reason,
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
                    v_monthly_fee, -- Waived monthly amount
                    CASE WHEN v_waiver_percentage > 0 THEN v_original_monthly_fee ELSE NULL END,
                    v_waiver_percentage,
                    v_waiver_reason,
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

