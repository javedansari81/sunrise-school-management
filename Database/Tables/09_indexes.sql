-- =====================================================
-- Database Indexes for Performance Optimization
-- =====================================================

-- Users table indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

-- Students table indexes
CREATE INDEX IF NOT EXISTS idx_students_admission_number ON students(admission_number);
CREATE INDEX IF NOT EXISTS idx_students_user_id ON students(user_id);
CREATE INDEX IF NOT EXISTS idx_students_class ON students(class);
CREATE INDEX IF NOT EXISTS idx_students_session_year ON students(session_year);
CREATE INDEX IF NOT EXISTS idx_students_is_active ON students(is_active);
CREATE INDEX IF NOT EXISTS idx_students_admission_date ON students(admission_date);
CREATE INDEX IF NOT EXISTS idx_students_class_section ON students(class, section);

-- Teachers table indexes
CREATE INDEX IF NOT EXISTS idx_teachers_employee_id ON teachers(employee_id);
CREATE INDEX IF NOT EXISTS idx_teachers_user_id ON teachers(user_id);
CREATE INDEX IF NOT EXISTS idx_teachers_email ON teachers(email);
CREATE INDEX IF NOT EXISTS idx_teachers_department ON teachers(department);
CREATE INDEX IF NOT EXISTS idx_teachers_position ON teachers(position);
CREATE INDEX IF NOT EXISTS idx_teachers_is_active ON teachers(is_active);
CREATE INDEX IF NOT EXISTS idx_teachers_joining_date ON teachers(joining_date);

-- Fee Structures table indexes (Updated for metadata-driven architecture)
CREATE INDEX IF NOT EXISTS idx_fee_structures_class_session ON fee_structures(class_id, session_year_id);
CREATE INDEX IF NOT EXISTS idx_fee_structures_session_year ON fee_structures(session_year_id);
CREATE INDEX IF NOT EXISTS idx_fee_structures_class_id ON fee_structures(class_id);

-- Fee Records table indexes (Updated for metadata-driven architecture)
CREATE INDEX IF NOT EXISTS idx_fee_records_student_id ON fee_records(student_id);
CREATE INDEX IF NOT EXISTS idx_fee_records_session_year_id ON fee_records(session_year_id);
CREATE INDEX IF NOT EXISTS idx_fee_records_payment_status_id ON fee_records(payment_status_id);
CREATE INDEX IF NOT EXISTS idx_fee_records_due_date ON fee_records(due_date);
CREATE INDEX IF NOT EXISTS idx_fee_records_payment_type_id ON fee_records(payment_type_id);
CREATE INDEX IF NOT EXISTS idx_fee_records_student_session ON fee_records(student_id, session_year_id);
CREATE INDEX IF NOT EXISTS idx_fee_records_student_payment_type ON fee_records(student_id, payment_type_id);
CREATE INDEX IF NOT EXISTS idx_fee_records_balance_amount ON fee_records(balance_amount);
CREATE INDEX IF NOT EXISTS idx_fee_records_created_at ON fee_records(created_at);
CREATE INDEX IF NOT EXISTS idx_fee_records_updated_at ON fee_records(updated_at);

-- Fee Payments table indexes (Updated for metadata-driven architecture)
CREATE INDEX IF NOT EXISTS idx_fee_payments_fee_record_id ON fee_payments(fee_record_id);
CREATE INDEX IF NOT EXISTS idx_fee_payments_payment_date ON fee_payments(payment_date);
CREATE INDEX IF NOT EXISTS idx_fee_payments_payment_method_id ON fee_payments(payment_method_id);
CREATE INDEX IF NOT EXISTS idx_fee_payments_collected_by ON fee_payments(collected_by);
CREATE INDEX IF NOT EXISTS idx_fee_payments_amount ON fee_payments(amount);
CREATE INDEX IF NOT EXISTS idx_fee_payments_transaction_id ON fee_payments(transaction_id);
CREATE INDEX IF NOT EXISTS idx_fee_payments_receipt_number ON fee_payments(receipt_number);

-- Student Attendance table indexes
CREATE INDEX IF NOT EXISTS idx_student_attendance_student_id ON student_attendance(student_id);
CREATE INDEX IF NOT EXISTS idx_student_attendance_date ON student_attendance(attendance_date);
CREATE INDEX IF NOT EXISTS idx_student_attendance_status ON student_attendance(status);
CREATE INDEX IF NOT EXISTS idx_student_attendance_student_date ON student_attendance(student_id, attendance_date);
CREATE INDEX IF NOT EXISTS idx_student_attendance_marked_by ON student_attendance(marked_by);

-- Teacher Attendance table indexes
CREATE INDEX IF NOT EXISTS idx_teacher_attendance_teacher_id ON teacher_attendance(teacher_id);
CREATE INDEX IF NOT EXISTS idx_teacher_attendance_date ON teacher_attendance(attendance_date);
CREATE INDEX IF NOT EXISTS idx_teacher_attendance_status ON teacher_attendance(status);
CREATE INDEX IF NOT EXISTS idx_teacher_attendance_teacher_date ON teacher_attendance(teacher_id, attendance_date);

-- Leave Requests table indexes
CREATE INDEX IF NOT EXISTS idx_leave_requests_applicant ON leave_requests(applicant_id, applicant_type);
CREATE INDEX IF NOT EXISTS idx_leave_requests_status ON leave_requests(status);
CREATE INDEX IF NOT EXISTS idx_leave_requests_leave_type ON leave_requests(leave_type);
CREATE INDEX IF NOT EXISTS idx_leave_requests_start_date ON leave_requests(start_date);
CREATE INDEX IF NOT EXISTS idx_leave_requests_end_date ON leave_requests(end_date);
CREATE INDEX IF NOT EXISTS idx_leave_requests_applied_to ON leave_requests(applied_to);
CREATE INDEX IF NOT EXISTS idx_leave_requests_reviewed_by ON leave_requests(reviewed_by);

-- Expenses table indexes
CREATE INDEX IF NOT EXISTS idx_expenses_expense_date ON expenses(expense_date);
CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses(category);
CREATE INDEX IF NOT EXISTS idx_expenses_status ON expenses(status);
CREATE INDEX IF NOT EXISTS idx_expenses_payment_status ON expenses(payment_status);
CREATE INDEX IF NOT EXISTS idx_expenses_requested_by ON expenses(requested_by);
CREATE INDEX IF NOT EXISTS idx_expenses_approved_by ON expenses(approved_by);
CREATE INDEX IF NOT EXISTS idx_expenses_vendor_name ON expenses(vendor_name);
CREATE INDEX IF NOT EXISTS idx_expenses_budget_year ON expenses(budget_year);

-- Vendors table indexes
CREATE INDEX IF NOT EXISTS idx_vendors_vendor_name ON vendors(vendor_name);
CREATE INDEX IF NOT EXISTS idx_vendors_vendor_code ON vendors(vendor_code);
CREATE INDEX IF NOT EXISTS idx_vendors_is_active ON vendors(is_active);
CREATE INDEX IF NOT EXISTS idx_vendors_gst_number ON vendors(gst_number);

-- Purchase Orders table indexes
CREATE INDEX IF NOT EXISTS idx_purchase_orders_po_number ON purchase_orders(po_number);
CREATE INDEX IF NOT EXISTS idx_purchase_orders_vendor_id ON purchase_orders(vendor_id);
CREATE INDEX IF NOT EXISTS idx_purchase_orders_order_date ON purchase_orders(order_date);
CREATE INDEX IF NOT EXISTS idx_purchase_orders_status ON purchase_orders(status);
CREATE INDEX IF NOT EXISTS idx_purchase_orders_created_by ON purchase_orders(created_by);

-- Composite indexes for common queries (Updated for metadata-driven architecture)
CREATE INDEX IF NOT EXISTS idx_students_class_active ON students(class_id, is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_teachers_dept_active ON teachers(department, is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_fee_records_pending ON fee_records(student_id, due_date, payment_status_id) WHERE payment_status_id IN (1, 4); -- Pending, Overdue
CREATE INDEX IF NOT EXISTS idx_fee_records_current_session ON fee_records(student_id, session_year_id, payment_type_id) WHERE session_year_id = 4; -- 2025-26
CREATE INDEX IF NOT EXISTS idx_attendance_monthly ON student_attendance(student_id, date_part('year', attendance_date), date_part('month', attendance_date));
CREATE INDEX IF NOT EXISTS idx_expenses_monthly ON expenses(category, date_part('year', expense_date), date_part('month', expense_date));

-- Partial indexes for better performance on filtered queries (Updated for metadata-driven architecture)
CREATE INDEX IF NOT EXISTS idx_users_active_email ON users(email) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_students_current_session ON students(class_id, section) WHERE session_year_id = 4 AND is_active = true; -- 2025-26
CREATE INDEX IF NOT EXISTS idx_fee_records_overdue ON fee_records(student_id, due_date, balance_amount) WHERE payment_status_id = 4; -- Overdue
CREATE INDEX IF NOT EXISTS idx_fee_records_unpaid ON fee_records(student_id, balance_amount, due_date) WHERE balance_amount > 0;
CREATE INDEX IF NOT EXISTS idx_fee_payments_recent ON fee_payments(payment_date, amount) WHERE payment_date >= CURRENT_DATE - INTERVAL '30 days';
CREATE INDEX IF NOT EXISTS idx_leave_requests_pending ON leave_requests(applied_to, start_date) WHERE status = 'Pending';

-- Additional fee management indexes for enhanced performance
CREATE INDEX IF NOT EXISTS idx_fee_records_search ON fee_records(student_id, session_year_id, payment_type_id, payment_status_id);
CREATE INDEX IF NOT EXISTS idx_fee_payments_search ON fee_payments(fee_record_id, payment_date, payment_method_id);
CREATE INDEX IF NOT EXISTS idx_fee_structures_lookup ON fee_structures(class_id, session_year_id, total_annual_fee);

-- Indexes for fee analytics and reporting
CREATE INDEX IF NOT EXISTS idx_fee_records_analytics ON fee_records(session_year_id, payment_type_id, total_amount, paid_amount);
CREATE INDEX IF NOT EXISTS idx_fee_payments_analytics ON fee_payments(payment_date, payment_method_id, amount);
CREATE INDEX IF NOT EXISTS idx_fee_records_collection_summary ON fee_records(session_year_id, payment_status_id, total_amount, paid_amount, balance_amount);

-- Text search indexes (for PostgreSQL full-text search)
CREATE INDEX IF NOT EXISTS idx_students_name_search ON students USING gin(to_tsvector('english', first_name || ' ' || last_name));
CREATE INDEX IF NOT EXISTS idx_teachers_name_search ON teachers USING gin(to_tsvector('english', first_name || ' ' || last_name));
CREATE INDEX IF NOT EXISTS idx_expenses_description_search ON expenses USING gin(to_tsvector('english', description));

-- Comments (Updated for metadata-driven architecture)
COMMENT ON INDEX idx_users_email IS 'Index for user email lookups during authentication';
COMMENT ON INDEX idx_students_admission_number IS 'Index for student admission number searches';
COMMENT ON INDEX idx_fee_records_student_session IS 'Composite index for fee queries by student and session';
COMMENT ON INDEX idx_fee_records_search IS 'Composite index for comprehensive fee record searches';
COMMENT ON INDEX idx_fee_records_analytics IS 'Index optimized for fee analytics and reporting queries';
COMMENT ON INDEX idx_fee_records_collection_summary IS 'Index for fee collection summary calculations';
COMMENT ON INDEX idx_fee_payments_analytics IS 'Index for payment analytics and trend analysis';
COMMENT ON INDEX idx_student_attendance_student_date IS 'Composite index for attendance queries';
COMMENT ON INDEX idx_expenses_monthly IS 'Composite index for monthly expense reports';
COMMENT ON INDEX idx_students_name_search IS 'Full-text search index for student names';
COMMENT ON INDEX idx_teachers_name_search IS 'Full-text search index for teacher names';
