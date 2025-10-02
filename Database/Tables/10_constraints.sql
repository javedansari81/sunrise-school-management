-- =====================================================
-- Complex Business Logic Constraints
-- =====================================================
--
-- This file contains ONLY complex business logic constraints that are better
-- maintained separately from table structure. Simple constraints (UNIQUE,
-- basic CHECK, simple FK) have been moved inline to table creation scripts.
--
-- MOVED TO TABLE CREATION SCRIPTS:
-- - Simple UNIQUE constraints (employee_id, po_number, etc.)
-- - Basic CHECK constraints (amount > 0, experience_years >= 0, etc.)
-- - Simple date validations (joining_date <= CURRENT_DATE, etc.)
--
-- KEPT HERE (Complex Business Logic):
-- - Complex regex validations (email format)
-- - Cross-column business rules (graduation_date > admission_date)
-- - Composite unique constraints with business logic
-- - Complex calculated field validations

-- =====================================================
-- Named Foreign Key Constraints (Complex Relationships)
-- =====================================================
-- Note: Basic foreign keys are now defined inline in table creation scripts.
-- These are for complex relationships that need explicit naming or special handling.

-- Fee Payments - Complex relationship with user tracking
ALTER TABLE fee_payments
ADD CONSTRAINT fk_fee_payments_collected_by
FOREIGN KEY (collected_by) REFERENCES users(id);

-- Note: Attendance tables were removed as they were orphaned (no models, no usage)

-- Leave Request - Complex workflow relationships
ALTER TABLE leave_requests
ADD CONSTRAINT fk_leave_requests_applied_to
FOREIGN KEY (applied_to) REFERENCES users(id),
ADD CONSTRAINT fk_leave_requests_reviewed_by
FOREIGN KEY (reviewed_by) REFERENCES users(id),
ADD CONSTRAINT fk_leave_requests_substitute
FOREIGN KEY (substitute_teacher_id) REFERENCES teachers(id);

-- Expense - Workflow and approval relationships
ALTER TABLE expenses
ADD CONSTRAINT fk_expenses_requested_by
FOREIGN KEY (requested_by) REFERENCES users(id),
ADD CONSTRAINT fk_expenses_approved_by
FOREIGN KEY (approved_by) REFERENCES users(id);

-- Purchase Order - Approval workflow relationships
ALTER TABLE purchase_orders
ADD CONSTRAINT fk_purchase_orders_created_by
FOREIGN KEY (created_by) REFERENCES users(id),
ADD CONSTRAINT fk_purchase_orders_approved_by
FOREIGN KEY (approved_by) REFERENCES users(id);

-- =====================================================
-- Complex Business Logic Check Constraints
-- =====================================================
-- Note: Simple CHECK constraints (amount > 0, date <= CURRENT_DATE, etc.)
-- have been moved inline to table creation scripts.

-- Complex regex validation for email format
ALTER TABLE users
ADD CONSTRAINT chk_users_email_format
CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

-- Complex calculated field validation for fee balance
ALTER TABLE fee_records
ADD CONSTRAINT chk_fee_records_balance
CHECK (balance_amount = total_amount - paid_amount);

-- Note: Attendance table constraints removed (tables were orphaned)

-- Complex business rule: Leave end date must be >= start date
ALTER TABLE leave_requests
ADD CONSTRAINT chk_leave_requests_dates
CHECK (end_date >= start_date),
ADD CONSTRAINT chk_leave_requests_total_days
CHECK (total_days > 0);

-- Complex business rule: Purchase order delivery date validations
ALTER TABLE purchase_orders
ADD CONSTRAINT chk_purchase_orders_dates
CHECK (expected_delivery_date IS NULL OR expected_delivery_date >= order_date),
ADD CONSTRAINT chk_purchase_orders_actual_delivery
CHECK (actual_delivery_date IS NULL OR actual_delivery_date >= order_date);

-- =====================================================
-- Complex Business Logic Unique Constraints
-- =====================================================
-- Note: Simple UNIQUE constraints have been moved inline to table creation scripts.

-- Complex business rule: Unique admission numbers per academic session
ALTER TABLE students
ADD CONSTRAINT uk_students_admission_session
UNIQUE (admission_number, session_year_id);

-- Complex business rule: Unique fee structure per class per session
ALTER TABLE fee_structures
ADD CONSTRAINT uk_fee_structures_class_session
UNIQUE (class_id, session_year_id);

-- =====================================================
-- Comments on Complex Constraints
-- =====================================================

COMMENT ON CONSTRAINT chk_users_email_format ON users IS 'Complex regex validation for email format';
COMMENT ON CONSTRAINT chk_fee_records_balance ON fee_records IS 'Business rule: balance must equal total minus paid amount';
COMMENT ON CONSTRAINT chk_leave_requests_dates ON leave_requests IS 'Business rule: end date cannot be before start date';
COMMENT ON CONSTRAINT uk_students_admission_session ON students IS 'Business rule: unique admission numbers per academic session';
COMMENT ON CONSTRAINT uk_fee_structures_class_session ON fee_structures IS 'Business rule: one fee structure per class per session';
