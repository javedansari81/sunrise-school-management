-- =====================================================
-- SAFE Fee Management Enhancement Scripts
-- =====================================================
-- These scripts ENHANCE your existing system without breaking anything
-- All existing tables and data remain intact
-- 
-- WHAT THIS DOES:
-- ✅ Adds new monthly tracking capability
-- ✅ Enhances existing tables with additional columns
-- ✅ Keeps all your current data and functionality
-- ✅ Provides backward compatibility
--
-- WHAT THIS DOESN'T DO:
-- ❌ Delete any existing tables
-- ❌ Remove any existing data
-- ❌ Break current functionality
-- ❌ Require immediate migration

-- =====================================================
-- Step 1: Enhance Existing fee_records Table
-- =====================================================

-- Add new columns to existing fee_records table for better tracking
ALTER TABLE fee_records 
ADD COLUMN IF NOT EXISTS fee_structure_id INTEGER REFERENCES fee_structures(id);

ALTER TABLE fee_records 
ADD COLUMN IF NOT EXISTS is_monthly_tracked BOOLEAN DEFAULT FALSE;

ALTER TABLE fee_records 
ADD COLUMN IF NOT EXISTS academic_month INTEGER CHECK (academic_month BETWEEN 1 AND 12);

ALTER TABLE fee_records 
ADD COLUMN IF NOT EXISTS academic_year INTEGER;

COMMENT ON COLUMN fee_records.fee_structure_id IS 'Links to the fee structure used for this record';
COMMENT ON COLUMN fee_records.is_monthly_tracked IS 'Whether this record uses monthly tracking';
COMMENT ON COLUMN fee_records.academic_month IS 'Academic month (4=April, 5=May, etc.)';
COMMENT ON COLUMN fee_records.academic_year IS 'Academic year for this fee record';

-- =====================================================
-- Step 2: Add Monthly Fee Tracking Table (New)
-- =====================================================

-- This is a NEW table that works alongside existing fee_records
CREATE TABLE IF NOT EXISTS monthly_fee_tracking (
    id SERIAL PRIMARY KEY,
    fee_record_id INTEGER NOT NULL REFERENCES fee_records(id) ON DELETE CASCADE,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    session_year_id INTEGER NOT NULL REFERENCES session_years(id),
    
    -- Month Details
    academic_month INTEGER NOT NULL CHECK (academic_month BETWEEN 1 AND 12),
    academic_year INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL, -- 'April', 'May', etc.
    
    -- Amount Details
    monthly_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    paid_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    balance_amount DECIMAL(10,2) GENERATED ALWAYS AS (monthly_amount - paid_amount) STORED,
    
    -- Status and Dates
    due_date DATE NOT NULL,
    payment_status_id INTEGER REFERENCES payment_statuses(id) DEFAULT 1,
    
    -- Additional Charges
    late_fee DECIMAL(10,2) DEFAULT 0.00,
    discount_amount DECIMAL(10,2) DEFAULT 0.00,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    
    -- Constraints
    UNIQUE(fee_record_id, academic_month, academic_year)
);

COMMENT ON TABLE monthly_fee_tracking IS 'Month-wise fee tracking linked to existing fee_records';
COMMENT ON COLUMN monthly_fee_tracking.academic_month IS 'Academic month: 4=April, 5=May, ..., 3=March';

-- =====================================================
-- Step 3: Add Payment Allocation Table (New)
-- =====================================================

-- Links existing fee_payments to specific months
CREATE TABLE IF NOT EXISTS monthly_payment_allocations (
    id SERIAL PRIMARY KEY,
    fee_payment_id INTEGER NOT NULL REFERENCES fee_payments(id) ON DELETE CASCADE,
    monthly_tracking_id INTEGER NOT NULL REFERENCES monthly_fee_tracking(id) ON DELETE CASCADE,
    allocated_amount DECIMAL(10,2) NOT NULL CHECK (allocated_amount > 0),
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by INTEGER REFERENCES users(id),
    
    UNIQUE(fee_payment_id, monthly_tracking_id)
);

COMMENT ON TABLE monthly_payment_allocations IS 'Links existing payments to specific monthly tracking records';

-- =====================================================
-- Step 4: Add Indexes for Performance
-- =====================================================

-- Indexes for monthly_fee_tracking
CREATE INDEX IF NOT EXISTS idx_monthly_tracking_fee_record 
    ON monthly_fee_tracking(fee_record_id);

CREATE INDEX IF NOT EXISTS idx_monthly_tracking_student_session 
    ON monthly_fee_tracking(student_id, session_year_id);

CREATE INDEX IF NOT EXISTS idx_monthly_tracking_month_year 
    ON monthly_fee_tracking(academic_month, academic_year);

CREATE INDEX IF NOT EXISTS idx_monthly_tracking_due_date 
    ON monthly_fee_tracking(due_date);

CREATE INDEX IF NOT EXISTS idx_monthly_tracking_status 
    ON monthly_fee_tracking(payment_status_id);

-- Indexes for payment allocations
CREATE INDEX IF NOT EXISTS idx_payment_allocations_payment 
    ON monthly_payment_allocations(fee_payment_id);

CREATE INDEX IF NOT EXISTS idx_payment_allocations_monthly 
    ON monthly_payment_allocations(monthly_tracking_id);

-- =====================================================
-- Step 5: Create Helper Views
-- =====================================================

-- View combining existing and new data
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
    
    -- Monthly tracking summary
    COUNT(mft.id) as total_months_tracked,
    COUNT(CASE WHEN mft.payment_status_id = 3 THEN 1 END) as paid_months,
    COUNT(CASE WHEN mft.payment_status_id = 1 THEN 1 END) as pending_months,
    COUNT(CASE WHEN mft.payment_status_id = 4 THEN 1 END) as overdue_months,
    SUM(mft.monthly_amount) as monthly_total,
    SUM(mft.paid_amount) as monthly_paid,
    SUM(mft.balance_amount) as monthly_balance

FROM students s
JOIN classes c ON s.class_id = c.id
JOIN session_years sy ON s.session_year_id = sy.id
LEFT JOIN fee_records fr ON s.id = fr.student_id AND s.session_year_id = fr.session_year_id
LEFT JOIN monthly_fee_tracking mft ON fr.id = mft.fee_record_id
GROUP BY s.id, s.admission_number, s.first_name, s.last_name, c.display_name, sy.name, 
         fr.id, fr.total_amount, fr.paid_amount, fr.balance_amount;

COMMENT ON VIEW enhanced_student_fee_status IS 'Combined view of existing and enhanced fee tracking';

-- =====================================================
-- Step 6: Create Safe Migration Functions
-- =====================================================

-- Function to enable monthly tracking for existing fee records
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
    
    -- Calculate monthly amount
    monthly_amount := COALESCE(fee_record.total_annual_fee, fee_record.total_amount) / 12;
    
    -- Set starting year
    current_year := COALESCE(p_start_year, EXTRACT(YEAR FROM CURRENT_DATE));
    current_month := p_start_month;
    
    -- Create 12 monthly tracking records
    FOR month_counter IN 0..11 LOOP
        -- Calculate due date
        due_date := DATE(current_year || '-' || LPAD(current_month::TEXT, 2, '0') || '-10');
        
        -- Insert monthly tracking record
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
        ) ON CONFLICT (fee_record_id, academic_month, academic_year) DO NOTHING;
        
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
    
    -- Mark fee record as monthly tracked
    UPDATE fee_records 
    SET is_monthly_tracked = TRUE 
    WHERE id = p_fee_record_id;
    
    RETURN records_created;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION enable_monthly_tracking_for_record IS 'Safely enables monthly tracking for existing fee records';

-- =====================================================
-- Step 7: Create Trigger for Automatic Updates
-- =====================================================

-- Function to update monthly tracking when payments are made
CREATE OR REPLACE FUNCTION update_monthly_tracking_on_payment()
RETURNS TRIGGER AS $$
DECLARE
    tracking_record RECORD;
    remaining_amount DECIMAL(10,2);
BEGIN
    -- Only process if the fee record has monthly tracking enabled
    IF EXISTS (
        SELECT 1 FROM fee_records 
        WHERE id = NEW.fee_record_id AND is_monthly_tracked = TRUE
    ) THEN
        remaining_amount := NEW.amount;
        
        -- Allocate payment to monthly tracking records in chronological order
        FOR tracking_record IN 
            SELECT * FROM monthly_fee_tracking 
            WHERE fee_record_id = NEW.fee_record_id 
            AND balance_amount > 0
            ORDER BY academic_year, academic_month
        LOOP
            IF remaining_amount <= 0 THEN
                EXIT;
            END IF;
            
            DECLARE
                allocation_amount DECIMAL(10,2);
            BEGIN
                -- Calculate how much to allocate to this month
                allocation_amount := LEAST(remaining_amount, tracking_record.balance_amount);
                
                -- Create allocation record
                INSERT INTO monthly_payment_allocations (
                    fee_payment_id, monthly_tracking_id, allocated_amount
                ) VALUES (
                    NEW.id, tracking_record.id, allocation_amount
                );
                
                -- Update monthly tracking paid amount
                UPDATE monthly_fee_tracking 
                SET 
                    paid_amount = paid_amount + allocation_amount,
                    payment_status_id = CASE 
                        WHEN paid_amount + allocation_amount >= monthly_amount THEN 3 -- Paid
                        WHEN paid_amount + allocation_amount > 0 THEN 2 -- Partial
                        ELSE payment_status_id
                    END,
                    updated_at = NOW()
                WHERE id = tracking_record.id;
                
                remaining_amount := remaining_amount - allocation_amount;
            END;
        END LOOP;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger
CREATE TRIGGER trigger_update_monthly_tracking_on_payment
    AFTER INSERT ON fee_payments
    FOR EACH ROW
    EXECUTE FUNCTION update_monthly_tracking_on_payment();

COMMENT ON FUNCTION update_monthly_tracking_on_payment IS 'Automatically allocates payments to monthly tracking records';
