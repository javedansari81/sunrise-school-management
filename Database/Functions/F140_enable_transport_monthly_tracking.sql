-- =====================================================
-- Function: enable_transport_monthly_tracking
-- Description: Enable monthly tracking for transport enrollment
-- Creates 12 monthly records with service enabled/disabled based on enrollment date
-- Handles re-enrollment: Updates enrollment_id and monthly_amount for unpaid months
-- Dependencies: student_transport_enrollment, transport_monthly_tracking
-- Version: 1.1 (Updated 2025-10-17 - Re-enrollment support)
-- =====================================================

-- Drop existing function
DROP FUNCTION IF EXISTS enable_transport_monthly_tracking(INTEGER, INTEGER, INTEGER);

-- Create function
CREATE OR REPLACE FUNCTION enable_transport_monthly_tracking(
    p_enrollment_id INTEGER,
    p_start_month INTEGER DEFAULT 4,
    p_start_year INTEGER DEFAULT 2025
)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_records_created INTEGER := 0;
    v_enrollment RECORD;
    v_month INTEGER;
    v_year INTEGER;
    v_session_start_year INTEGER; -- Derived from session_years table
    v_month_name VARCHAR(20);
    v_due_date DATE;
    v_is_service_enabled BOOLEAN;
    v_monthly_amount DECIMAL(10,2);
    v_enrollment_month INTEGER;
    v_enrollment_year INTEGER;
    v_current_date DATE;
BEGIN
    -- Get enrollment details
    SELECT
        e.id, e.student_id, e.session_year_id, e.transport_type_id,
        e.enrollment_date, e.monthly_fee
    INTO v_enrollment
    FROM student_transport_enrollment e
    WHERE e.id = p_enrollment_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Enrollment ID % not found', p_enrollment_id;
    END IF;

    -- ALWAYS derive the start year from the session_years table using enrollment's session_year_id
    -- This ensures the year is correct for past, current, or future session years
    SELECT EXTRACT(YEAR FROM sy.start_date)::INTEGER
    INTO v_session_start_year
    FROM session_years sy
    WHERE sy.id = v_enrollment.session_year_id;

    -- If session year not found, raise an error
    IF v_session_start_year IS NULL THEN
        RAISE EXCEPTION 'Session year ID % not found in session_years table', v_enrollment.session_year_id;
    END IF;

    -- Extract enrollment month and year
    v_enrollment_month := EXTRACT(MONTH FROM v_enrollment.enrollment_date);
    v_enrollment_year := EXTRACT(YEAR FROM v_enrollment.enrollment_date);

    -- Initialize month and year using session start year (not the passed parameter)
    v_month := p_start_month;
    v_year := v_session_start_year;

    -- Create 12 monthly tracking records (April to March)
    FOR i IN 1..12 LOOP
        -- Get month name
        v_month_name := TO_CHAR(TO_DATE(v_month::TEXT, 'MM'), 'Month');
        v_month_name := TRIM(v_month_name);

        -- Calculate due date (5th of each month)
        v_due_date := TO_DATE(v_year || '-' || LPAD(v_month::TEXT, 2, '0') || '-05', 'YYYY-MM-DD');

        -- Determine if service should be enabled for this month
        -- Service is enabled only if the month is >= enrollment month
        IF (v_year > v_enrollment_year) OR
           (v_year = v_enrollment_year AND v_month >= v_enrollment_month) THEN
            v_is_service_enabled := TRUE;
            v_monthly_amount := v_enrollment.monthly_fee;
        ELSE
            v_is_service_enabled := FALSE;
            v_monthly_amount := 0.00;
        END IF;

        -- Insert or update monthly tracking record
        -- For re-enrollment: update enrollment_id and monthly_amount if unpaid
        -- This handles transport type changes and re-enrollment scenarios
        INSERT INTO transport_monthly_tracking (
            enrollment_id,
            student_id,
            session_year_id,
            academic_month,
            academic_year,
            month_name,
            is_service_enabled,
            monthly_amount,
            paid_amount,
            due_date,
            payment_status_id,
            late_fee,
            discount_amount,
            created_at
        ) VALUES (
            v_enrollment.id,
            v_enrollment.student_id,
            v_enrollment.session_year_id,
            v_month,
            v_year,
            v_month_name,
            v_is_service_enabled,
            v_monthly_amount,
            0.00,
            v_due_date,
            1, -- Pending status
            0.00,
            0.00,
            NOW()
        )
        ON CONFLICT (student_id, session_year_id, academic_month, academic_year)
        DO UPDATE SET
            -- Update enrollment_id to link to new enrollment (for re-enrollment)
            enrollment_id = EXCLUDED.enrollment_id,
            -- Update monthly_amount only if the month is unpaid (paid_amount = 0)
            -- This handles transport type changes
            monthly_amount = CASE
                WHEN transport_monthly_tracking.paid_amount = 0
                THEN EXCLUDED.monthly_amount
                ELSE transport_monthly_tracking.monthly_amount
            END,
            -- Update service enabled status
            is_service_enabled = EXCLUDED.is_service_enabled,
            -- Update due date
            due_date = EXCLUDED.due_date,
            -- Reset payment status to pending only if unpaid
            payment_status_id = CASE
                WHEN transport_monthly_tracking.paid_amount = 0
                THEN EXCLUDED.payment_status_id
                ELSE transport_monthly_tracking.payment_status_id
            END,
            -- Update timestamp
            updated_at = NOW();

        -- Count as created/updated
        v_records_created := v_records_created + 1;

        -- Move to next month
        v_month := v_month + 1;
        IF v_month > 12 THEN
            v_month := 1;
            v_year := v_year + 1;
        END IF;
    END LOOP;

    RETURN v_records_created;
END;
$$;

-- Add comment
COMMENT ON FUNCTION enable_transport_monthly_tracking(INTEGER, INTEGER, INTEGER) IS
'Enable monthly tracking for transport enrollment. Creates 12 monthly records with service enabled/disabled based on enrollment date. Supports re-enrollment by updating enrollment_id and monthly_amount for unpaid months only.';

