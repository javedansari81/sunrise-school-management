-- =====================================================
-- Foreign Key Constraints and Relationships
-- =====================================================

-- Note: Most foreign key constraints are already defined in the table creation scripts
-- This file contains additional constraints and relationship validations

-- Additional Foreign Key Constraints
-- (Most are already defined in table creation, these are supplementary)

-- User Profile constraints
ALTER TABLE user_profiles 
ADD CONSTRAINT fk_user_profiles_user_id 
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Student constraints
ALTER TABLE students 
ADD CONSTRAINT fk_students_user_id 
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Teacher constraints  
ALTER TABLE teachers 
ADD CONSTRAINT fk_teachers_user_id 
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Student Academic History constraints
ALTER TABLE student_academic_history 
ADD CONSTRAINT fk_student_academic_history_student_id 
FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE;

-- Teacher Subject Assignments constraints
ALTER TABLE teacher_subject_assignments 
ADD CONSTRAINT fk_teacher_subject_assignments_teacher_id 
FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE;

-- Fee Records constraints
ALTER TABLE fee_records 
ADD CONSTRAINT fk_fee_records_student_id 
FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE;

-- Fee Payments constraints
ALTER TABLE fee_payments 
ADD CONSTRAINT fk_fee_payments_fee_record_id 
FOREIGN KEY (fee_record_id) REFERENCES fee_records(id) ON DELETE CASCADE,
ADD CONSTRAINT fk_fee_payments_collected_by 
FOREIGN KEY (collected_by) REFERENCES users(id);

-- Attendance constraints
ALTER TABLE student_attendance 
ADD CONSTRAINT fk_student_attendance_student_id 
FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
ADD CONSTRAINT fk_student_attendance_marked_by 
FOREIGN KEY (marked_by) REFERENCES users(id);

ALTER TABLE teacher_attendance 
ADD CONSTRAINT fk_teacher_attendance_teacher_id 
FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
ADD CONSTRAINT fk_teacher_attendance_marked_by 
FOREIGN KEY (marked_by) REFERENCES users(id),
ADD CONSTRAINT fk_teacher_attendance_substitute 
FOREIGN KEY (substitute_teacher_id) REFERENCES teachers(id);

-- Leave Request constraints
ALTER TABLE leave_requests 
ADD CONSTRAINT fk_leave_requests_applied_to 
FOREIGN KEY (applied_to) REFERENCES users(id),
ADD CONSTRAINT fk_leave_requests_reviewed_by 
FOREIGN KEY (reviewed_by) REFERENCES users(id),
ADD CONSTRAINT fk_leave_requests_substitute 
FOREIGN KEY (substitute_teacher_id) REFERENCES teachers(id);

-- Leave Balance constraints
ALTER TABLE leave_balance 
ADD CONSTRAINT fk_leave_balance_teacher_id 
FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE;

-- Expense constraints
ALTER TABLE expenses 
ADD CONSTRAINT fk_expenses_requested_by 
FOREIGN KEY (requested_by) REFERENCES users(id),
ADD CONSTRAINT fk_expenses_approved_by 
FOREIGN KEY (approved_by) REFERENCES users(id);

-- Purchase Order constraints
ALTER TABLE purchase_orders 
ADD CONSTRAINT fk_purchase_orders_vendor_id 
FOREIGN KEY (vendor_id) REFERENCES vendors(id),
ADD CONSTRAINT fk_purchase_orders_created_by 
FOREIGN KEY (created_by) REFERENCES users(id),
ADD CONSTRAINT fk_purchase_orders_approved_by 
FOREIGN KEY (approved_by) REFERENCES users(id);

-- =====================================================
-- Check Constraints for Data Validation
-- =====================================================

-- User constraints
ALTER TABLE users 
ADD CONSTRAINT chk_users_email_format 
CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

-- Student constraints
ALTER TABLE students 
ADD CONSTRAINT chk_students_admission_date 
CHECK (admission_date <= CURRENT_DATE),
ADD CONSTRAINT chk_students_graduation_date 
CHECK (graduation_date IS NULL OR graduation_date > admission_date),
ADD CONSTRAINT chk_students_phone_format 
CHECK (phone IS NULL OR phone ~ '^[0-9+\-\s()]+$');

-- Teacher constraints
ALTER TABLE teachers 
ADD CONSTRAINT chk_teachers_joining_date 
CHECK (joining_date <= CURRENT_DATE),
ADD CONSTRAINT chk_teachers_resignation_date 
CHECK (resignation_date IS NULL OR resignation_date > joining_date),
ADD CONSTRAINT chk_teachers_experience_years 
CHECK (experience_years >= 0),
ADD CONSTRAINT chk_teachers_salary 
CHECK (salary IS NULL OR salary > 0);

-- Fee Records constraints
ALTER TABLE fee_records 
ADD CONSTRAINT chk_fee_records_amounts 
CHECK (total_amount > 0 AND paid_amount >= 0 AND balance_amount >= 0),
ADD CONSTRAINT chk_fee_records_balance 
CHECK (balance_amount = total_amount - paid_amount),
ADD CONSTRAINT chk_fee_records_due_date 
CHECK (due_date >= '2020-01-01');

-- Fee Payments constraints
ALTER TABLE fee_payments 
ADD CONSTRAINT chk_fee_payments_amount 
CHECK (amount > 0),
ADD CONSTRAINT chk_fee_payments_payment_date 
CHECK (payment_date <= CURRENT_DATE);

-- Attendance constraints
ALTER TABLE student_attendance 
ADD CONSTRAINT chk_student_attendance_date 
CHECK (attendance_date <= CURRENT_DATE),
ADD CONSTRAINT chk_student_attendance_late_minutes 
CHECK (late_minutes >= 0);

ALTER TABLE teacher_attendance 
ADD CONSTRAINT chk_teacher_attendance_date 
CHECK (attendance_date <= CURRENT_DATE),
ADD CONSTRAINT chk_teacher_attendance_hours 
CHECK (total_hours IS NULL OR total_hours >= 0),
ADD CONSTRAINT chk_teacher_attendance_late_minutes 
CHECK (late_minutes >= 0);

-- Leave Request constraints
ALTER TABLE leave_requests 
ADD CONSTRAINT chk_leave_requests_dates 
CHECK (end_date >= start_date),
ADD CONSTRAINT chk_leave_requests_total_days 
CHECK (total_days > 0);

-- Expense constraints
ALTER TABLE expenses 
ADD CONSTRAINT chk_expenses_amounts 
CHECK (amount > 0 AND tax_amount >= 0 AND total_amount > 0),
ADD CONSTRAINT chk_expenses_expense_date 
CHECK (expense_date >= '2020-01-01'),
ADD CONSTRAINT chk_expenses_payment_date 
CHECK (payment_date IS NULL OR payment_date >= expense_date);

-- Purchase Order constraints
ALTER TABLE purchase_orders 
ADD CONSTRAINT chk_purchase_orders_amounts 
CHECK (subtotal > 0 AND tax_amount >= 0 AND total_amount > 0),
ADD CONSTRAINT chk_purchase_orders_dates 
CHECK (expected_delivery_date IS NULL OR expected_delivery_date >= order_date),
ADD CONSTRAINT chk_purchase_orders_actual_delivery 
CHECK (actual_delivery_date IS NULL OR actual_delivery_date >= order_date);

-- =====================================================
-- Unique Constraints (Additional)
-- =====================================================

-- Ensure unique admission numbers per session
ALTER TABLE students 
ADD CONSTRAINT uk_students_admission_session 
UNIQUE (admission_number, session_year);

-- Ensure unique employee IDs
ALTER TABLE teachers 
ADD CONSTRAINT uk_teachers_employee_id 
UNIQUE (employee_id);

-- Ensure unique PO numbers
ALTER TABLE purchase_orders 
ADD CONSTRAINT uk_purchase_orders_po_number 
UNIQUE (po_number);

-- Ensure unique fee structure per class per session
ALTER TABLE fee_structures 
ADD CONSTRAINT uk_fee_structures_class_session 
UNIQUE (class_name, session_year);

-- =====================================================
-- Comments on Constraints
-- =====================================================

COMMENT ON CONSTRAINT chk_users_email_format ON users IS 'Validates email format using regex';
COMMENT ON CONSTRAINT chk_fee_records_balance ON fee_records IS 'Ensures balance equals total minus paid amount';
COMMENT ON CONSTRAINT chk_leave_requests_dates ON leave_requests IS 'Ensures end date is not before start date';
COMMENT ON CONSTRAINT uk_students_admission_session ON students IS 'Ensures unique admission numbers per academic session';
