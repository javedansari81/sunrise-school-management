-- =====================================================
-- Fee Management System Enhancement Scripts
-- =====================================================
-- IMPORTANT: These scripts ENHANCE your existing fee tables
-- They DO NOT replace them - they work together for better functionality
--
-- EXISTING TABLES THAT REMAIN UNCHANGED:
-- ✅ fee_structures - Still used for class-wise fee definitions
-- ✅ fee_payments - Still used for payment transactions
-- ✅ fee_discounts - Still used for scholarships/discounts
-- ✅ fee_reminders - Still used for notifications
-- ✅ fee_reports - Still used for reporting
--
-- NEW ADDITIONS:
-- 🆕 monthly_fee_records - For month-wise tracking
-- 🆕 payment_allocations - Links payments to specific months
-- 🔧 Enhanced fee_records - Additional columns for better tracking
--
-- Run these scripts in sequence to enhance the current system
-- for 9/10 robustness with monthly fee tracking

-- =====================================================
-- Phase 1: Add Monthly Fee Records Table
-- =====================================================

-- Create monthly fee records table for granular month-wise tracking
CREATE TABLE IF NOT EXISTS monthly_fee_records (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    session_year_id INTEGER NOT NULL REFERENCES session_years(id),
    month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
    year INTEGER NOT NULL CHECK (year BETWEEN 2020 AND 2030),
    
    -- Fee Details
    monthly_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    paid_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    balance_amount DECIMAL(10,2) GENERATED ALWAYS AS (monthly_amount - paid_amount) STORED,
    
    -- Status and Dates
    due_date DATE NOT NULL,
    payment_status_id INTEGER REFERENCES payment_statuses(id) DEFAULT 1, -- Default: Pending
    
    -- Additional Charges
    late_fee DECIMAL(10,2) DEFAULT 0.00,
    discount_amount DECIMAL(10,2) DEFAULT 0.00,
    adjustment_amount DECIMAL(10,2) DEFAULT 0.00,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    created_by INTEGER REFERENCES users(id),
    
    -- Ensure unique record per student per month per session
    UNIQUE(student_id, session_year_id, month, year)
);

-- Add comments for documentation
COMMENT ON TABLE monthly_fee_records IS 'Monthly fee tracking for granular payment status';
COMMENT ON COLUMN monthly_fee_records.month IS 'Month number (1=Jan, 2=Feb, ..., 12=Dec)';
COMMENT ON COLUMN monthly_fee_records.year IS 'Calendar year for the fee month';
COMMENT ON COLUMN monthly_fee_records.balance_amount IS 'Auto-calculated: monthly_amount - paid_amount';
COMMENT ON COLUMN monthly_fee_records.payment_status_id IS 'FK to payment_statuses: 1=Pending, 2=Partial, 3=Paid, 4=Overdue';

-- =====================================================
-- Phase 2: Add Payment Allocation Table
-- =====================================================

-- Create payment allocation table to track which payments go to which months
CREATE TABLE IF NOT EXISTS payment_allocations (
    id SERIAL PRIMARY KEY,
    payment_id INTEGER NOT NULL REFERENCES fee_payments(id) ON DELETE CASCADE,
    monthly_fee_record_id INTEGER NOT NULL REFERENCES monthly_fee_records(id) ON DELETE CASCADE,
    allocated_amount DECIMAL(10,2) NOT NULL CHECK (allocated_amount > 0),
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by INTEGER REFERENCES users(id),
    
    -- Ensure no duplicate allocations
    UNIQUE(payment_id, monthly_fee_record_id)
);

COMMENT ON TABLE payment_allocations IS 'Tracks allocation of payments to specific monthly fee records';
COMMENT ON COLUMN payment_allocations.allocated_amount IS 'Amount from payment allocated to this specific month';

-- =====================================================
-- Phase 3: Add Student Promotion Tracking
-- =====================================================

-- Enhance student_academic_history table with more promotion details
ALTER TABLE student_academic_history 
ADD COLUMN IF NOT EXISTS promotion_type VARCHAR(20) DEFAULT 'PROMOTED' 
    CHECK (promotion_type IN ('PROMOTED', 'RETAINED', 'TRANSFERRED', 'GRADUATED'));

ALTER TABLE student_academic_history 
ADD COLUMN IF NOT EXISTS previous_class_id INTEGER REFERENCES classes(id);

ALTER TABLE student_academic_history 
ADD COLUMN IF NOT EXISTS fees_carried_forward DECIMAL(10,2) DEFAULT 0.00;

ALTER TABLE student_academic_history 
ADD COLUMN IF NOT EXISTS promotion_notes TEXT;

COMMENT ON COLUMN student_academic_history.promotion_type IS 'Type of academic transition';
COMMENT ON COLUMN student_academic_history.previous_class_id IS 'Class student was promoted from';
COMMENT ON COLUMN student_academic_history.fees_carried_forward IS 'Outstanding fee amount carried to new session';

-- =====================================================
-- Phase 4: Add Fee Structure Versioning
-- =====================================================

-- Add versioning to fee structures for better tracking
ALTER TABLE fee_structures 
ADD COLUMN IF NOT EXISTS version INTEGER DEFAULT 1;

ALTER TABLE fee_structures 
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;

ALTER TABLE fee_structures 
ADD COLUMN IF NOT EXISTS effective_from DATE DEFAULT CURRENT_DATE;

ALTER TABLE fee_structures 
ADD COLUMN IF NOT EXISTS effective_to DATE;

COMMENT ON COLUMN fee_structures.version IS 'Version number for fee structure changes';
COMMENT ON COLUMN fee_structures.effective_from IS 'Date from which this fee structure is effective';
COMMENT ON COLUMN fee_structures.effective_to IS 'Date until which this fee structure is effective';

-- =====================================================
-- Phase 5: Create Indexes for Performance
-- =====================================================

-- Indexes for monthly_fee_records
CREATE INDEX IF NOT EXISTS idx_monthly_fee_records_student_session 
    ON monthly_fee_records(student_id, session_year_id);

CREATE INDEX IF NOT EXISTS idx_monthly_fee_records_month_year 
    ON monthly_fee_records(month, year);

CREATE INDEX IF NOT EXISTS idx_monthly_fee_records_due_date 
    ON monthly_fee_records(due_date);

CREATE INDEX IF NOT EXISTS idx_monthly_fee_records_status 
    ON monthly_fee_records(payment_status_id);

CREATE INDEX IF NOT EXISTS idx_monthly_fee_records_balance 
    ON monthly_fee_records(balance_amount) WHERE balance_amount > 0;

-- Indexes for payment_allocations
CREATE INDEX IF NOT EXISTS idx_payment_allocations_payment 
    ON payment_allocations(payment_id);

CREATE INDEX IF NOT EXISTS idx_payment_allocations_monthly_record 
    ON payment_allocations(monthly_fee_record_id);

-- Indexes for enhanced academic history
CREATE INDEX IF NOT EXISTS idx_academic_history_promotion_type 
    ON student_academic_history(promotion_type);

CREATE INDEX IF NOT EXISTS idx_academic_history_fees_carried 
    ON student_academic_history(fees_carried_forward) WHERE fees_carried_forward > 0;

-- =====================================================
-- Phase 6: Create Views for Easy Querying
-- =====================================================

-- View for student fee summary
CREATE OR REPLACE VIEW student_fee_summary AS
SELECT 
    s.id as student_id,
    s.admission_number,
    s.first_name,
    s.last_name,
    c.display_name as class_name,
    sy.name as session_year,
    COUNT(mfr.id) as total_months,
    COUNT(CASE WHEN mfr.payment_status_id = 3 THEN 1 END) as paid_months,
    COUNT(CASE WHEN mfr.payment_status_id = 1 THEN 1 END) as pending_months,
    COUNT(CASE WHEN mfr.payment_status_id = 4 THEN 1 END) as overdue_months,
    SUM(mfr.monthly_amount) as total_annual_fee,
    SUM(mfr.paid_amount) as total_paid,
    SUM(mfr.balance_amount) as total_balance,
    SUM(mfr.late_fee) as total_late_fee
FROM students s
JOIN classes c ON s.class_id = c.id
JOIN session_years sy ON s.session_year_id = sy.id
LEFT JOIN monthly_fee_records mfr ON s.id = mfr.student_id AND s.session_year_id = mfr.session_year_id
GROUP BY s.id, s.admission_number, s.first_name, s.last_name, c.display_name, sy.name;

COMMENT ON VIEW student_fee_summary IS 'Comprehensive fee summary for each student';

-- View for overdue fees
CREATE OR REPLACE VIEW overdue_fees_summary AS
SELECT 
    s.id as student_id,
    s.admission_number,
    s.first_name || ' ' || s.last_name as student_name,
    c.display_name as class_name,
    mfr.month,
    mfr.year,
    mfr.monthly_amount,
    mfr.paid_amount,
    mfr.balance_amount,
    mfr.due_date,
    CURRENT_DATE - mfr.due_date as days_overdue,
    mfr.late_fee
FROM students s
JOIN classes c ON s.class_id = c.id
JOIN monthly_fee_records mfr ON s.id = mfr.student_id
WHERE mfr.payment_status_id = 4 -- Overdue status
ORDER BY mfr.due_date ASC;

COMMENT ON VIEW overdue_fees_summary IS 'All overdue fee records with student details';

-- =====================================================
-- Phase 7: Create Triggers for Automatic Updates
-- =====================================================

-- Function to update payment status based on paid amount
CREATE OR REPLACE FUNCTION update_monthly_fee_status()
RETURNS TRIGGER AS $$
BEGIN
    -- Update payment status based on paid amount
    IF NEW.paid_amount >= NEW.monthly_amount THEN
        NEW.payment_status_id = 3; -- Paid
    ELSIF NEW.paid_amount > 0 THEN
        NEW.payment_status_id = 2; -- Partial
    ELSIF NEW.due_date < CURRENT_DATE THEN
        NEW.payment_status_id = 4; -- Overdue
    ELSE
        NEW.payment_status_id = 1; -- Pending
    END IF;
    
    -- Update timestamp
    NEW.updated_at = NOW();
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for automatic status updates
CREATE TRIGGER trigger_update_monthly_fee_status
    BEFORE UPDATE ON monthly_fee_records
    FOR EACH ROW
    EXECUTE FUNCTION update_monthly_fee_status();

COMMENT ON FUNCTION update_monthly_fee_status() IS 'Automatically updates payment status based on paid amount';

-- =====================================================
-- Phase 8: Data Migration (Optional)
-- =====================================================

-- Function to migrate existing fee_records to monthly_fee_records
-- Run this ONLY if you want to migrate existing data
/*
CREATE OR REPLACE FUNCTION migrate_existing_fee_records()
RETURNS INTEGER AS $$
DECLARE
    record_count INTEGER := 0;
    fee_record RECORD;
    monthly_amount DECIMAL(10,2);
    month_num INTEGER;
BEGIN
    -- Loop through existing fee records
    FOR fee_record IN 
        SELECT fr.*, fs.total_annual_fee 
        FROM fee_records fr
        JOIN students s ON fr.student_id = s.id
        JOIN fee_structures fs ON s.class_id = fs.class_id AND fr.session_year_id = fs.session_year_id
        WHERE fr.payment_type_id = 1 -- Monthly payments only
    LOOP
        -- Calculate monthly amount
        monthly_amount := fee_record.total_annual_fee / 12;
        
        -- Create 12 monthly records
        FOR month_num IN 1..12 LOOP
            INSERT INTO monthly_fee_records (
                student_id, session_year_id, month, year,
                monthly_amount, paid_amount, due_date, payment_status_id
            ) VALUES (
                fee_record.student_id,
                fee_record.session_year_id,
                month_num,
                EXTRACT(YEAR FROM fee_record.due_date),
                monthly_amount,
                CASE WHEN month_num = 1 THEN fee_record.paid_amount ELSE 0 END,
                fee_record.due_date + INTERVAL '1 month' * (month_num - 1),
                CASE WHEN month_num = 1 AND fee_record.paid_amount > 0 THEN 2 ELSE 1 END
            ) ON CONFLICT (student_id, session_year_id, month, year) DO NOTHING;
            
            record_count := record_count + 1;
        END LOOP;
    END LOOP;
    
    RETURN record_count;
END;
$$ LANGUAGE plpgsql;

-- Uncomment and run this to migrate existing data
-- SELECT migrate_existing_fee_records();
*/

-- =====================================================
-- Phase 9: Monthly Fee Generation Functions
-- =====================================================

-- Function to generate monthly fee records for a student
CREATE OR REPLACE FUNCTION generate_monthly_fees_for_student(
    p_student_id INTEGER,
    p_session_year_id INTEGER,
    p_start_month INTEGER DEFAULT 4, -- April (academic year start)
    p_start_year INTEGER DEFAULT NULL
)
RETURNS INTEGER AS $$
DECLARE
    student_record RECORD;
    fee_structure_record RECORD;
    monthly_amount DECIMAL(10,2);
    current_month INTEGER;
    current_year INTEGER;
    due_date DATE;
    records_created INTEGER := 0;
    month_counter INTEGER := 0;
BEGIN
    -- Get student details
    SELECT s.*, c.display_name as class_name
    INTO student_record
    FROM students s
    JOIN classes c ON s.class_id = c.id
    WHERE s.id = p_student_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Student with ID % not found', p_student_id;
    END IF;

    -- Get fee structure for student's class
    SELECT * INTO fee_structure_record
    FROM fee_structures
    WHERE class_id = student_record.class_id
    AND session_year_id = p_session_year_id
    AND is_active = TRUE
    ORDER BY version DESC
    LIMIT 1;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Fee structure not found for class % and session %',
            student_record.class_name, p_session_year_id;
    END IF;

    -- Calculate monthly amount
    monthly_amount := fee_structure_record.total_annual_fee / 12;

    -- Set starting year
    current_year := COALESCE(p_start_year, EXTRACT(YEAR FROM CURRENT_DATE));
    current_month := p_start_month;

    -- Generate 12 monthly records (April to March academic year)
    FOR month_counter IN 0..11 LOOP
        -- Calculate due date (typically 10th of each month)
        due_date := DATE(current_year || '-' || LPAD(current_month::TEXT, 2, '0') || '-10');

        -- Insert monthly fee record
        INSERT INTO monthly_fee_records (
            student_id,
            session_year_id,
            month,
            year,
            monthly_amount,
            due_date,
            payment_status_id,
            created_by
        ) VALUES (
            p_student_id,
            p_session_year_id,
            current_month,
            current_year,
            monthly_amount,
            due_date,
            1, -- Pending status
            1  -- System user
        ) ON CONFLICT (student_id, session_year_id, month, year) DO NOTHING;

        -- Check if record was actually inserted
        IF FOUND THEN
            records_created := records_created + 1;
        END IF;

        -- Move to next month
        current_month := current_month + 1;
        IF current_month > 12 THEN
            current_month := 1;
            current_year := current_year + 1;
        END IF;
    END LOOP;

    RETURN records_created;
END;
$$ LANGUAGE plpgsql;

-- Function to generate monthly fees for all students in a session
CREATE OR REPLACE FUNCTION generate_monthly_fees_for_session(
    p_session_year_id INTEGER,
    p_start_month INTEGER DEFAULT 4,
    p_start_year INTEGER DEFAULT NULL
)
RETURNS TABLE(
    student_id INTEGER,
    student_name TEXT,
    class_name TEXT,
    records_created INTEGER
) AS $$
DECLARE
    student_record RECORD;
    created_count INTEGER;
BEGIN
    -- Loop through all active students
    FOR student_record IN
        SELECT s.id, s.first_name || ' ' || s.last_name as name, c.display_name as class
        FROM students s
        JOIN classes c ON s.class_id = c.id
        WHERE s.session_year_id = p_session_year_id
        AND s.is_active = TRUE
        ORDER BY c.sort_order, s.first_name
    LOOP
        -- Generate monthly fees for this student
        SELECT generate_monthly_fees_for_student(
            student_record.id,
            p_session_year_id,
            p_start_month,
            p_start_year
        ) INTO created_count;

        -- Return result for this student
        student_id := student_record.id;
        student_name := student_record.name;
        class_name := student_record.class;
        records_created := created_count;

        RETURN NEXT;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Function for mid-year admissions (creates records for remaining months only)
CREATE OR REPLACE FUNCTION generate_monthly_fees_from_admission_date(
    p_student_id INTEGER,
    p_session_year_id INTEGER,
    p_admission_date DATE
)
RETURNS INTEGER AS $$
DECLARE
    admission_month INTEGER;
    admission_year INTEGER;
    academic_year_end_month INTEGER := 3; -- March
    academic_year_end_year INTEGER;
BEGIN
    -- Extract month and year from admission date
    admission_month := EXTRACT(MONTH FROM p_admission_date);
    admission_year := EXTRACT(YEAR FROM p_admission_date);

    -- Calculate academic year end year
    IF admission_month >= 4 THEN
        academic_year_end_year := admission_year + 1;
    ELSE
        academic_year_end_year := admission_year;
    END IF;

    -- Generate monthly fees from admission month to March
    RETURN generate_monthly_fees_for_student(
        p_student_id,
        p_session_year_id,
        admission_month,
        admission_year
    );
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION generate_monthly_fees_for_student IS 'Generates 12 monthly fee records for a specific student';
COMMENT ON FUNCTION generate_monthly_fees_for_session IS 'Generates monthly fee records for all students in a session';
COMMENT ON FUNCTION generate_monthly_fees_from_admission_date IS 'Generates monthly fees for mid-year admissions from admission date';
