-- =====================================================
-- Data Load: Alert Types and Alert Statuses
-- Description: Initial data for alert notification system
-- Dependencies: T800_alert_types, T805_alert_statuses
-- =====================================================

-- ===========================================
-- Alert Statuses Data
-- ===========================================
INSERT INTO alert_statuses (id, name, description, color_code, is_final) VALUES
(1, 'UNREAD', 'Alert not yet read', '#2196F3', FALSE),
(2, 'READ', 'Alert has been viewed', '#9E9E9E', FALSE),
(3, 'ACKNOWLEDGED', 'Alert acknowledged by user', '#4CAF50', TRUE),
(4, 'DISMISSED', 'Alert dismissed by user', '#757575', TRUE),
(5, 'EXPIRED', 'Alert has expired', '#BDBDBD', TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    color_code = EXCLUDED.color_code,
    is_final = EXCLUDED.is_final,
    updated_at = NOW();

-- ===========================================
-- Alert Types Data
-- ===========================================

-- Leave Management Alerts (1-9)
INSERT INTO alert_types (id, name, description, category, icon, color_code, priority_level, default_expiry_days, requires_acknowledgment) VALUES
(1, 'LEAVE_REQUEST_CREATED', 'Leave request submitted', 'LEAVE_MANAGEMENT', 'EventNote', '#2196F3', 2, 7, FALSE),
(2, 'LEAVE_REQUEST_APPROVED', 'Leave request approved', 'LEAVE_MANAGEMENT', 'CheckCircle', '#4CAF50', 1, 7, FALSE),
(3, 'LEAVE_REQUEST_REJECTED', 'Leave request rejected', 'LEAVE_MANAGEMENT', 'Cancel', '#F44336', 2, 7, FALSE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    category = EXCLUDED.category,
    icon = EXCLUDED.icon,
    color_code = EXCLUDED.color_code,
    priority_level = EXCLUDED.priority_level,
    default_expiry_days = EXCLUDED.default_expiry_days,
    requires_acknowledgment = EXCLUDED.requires_acknowledgment,
    updated_at = NOW();

-- Fee Management Alerts (10-19)
INSERT INTO alert_types (id, name, description, category, icon, color_code, priority_level, default_expiry_days, requires_acknowledgment) VALUES
(10, 'FEE_PAYMENT_RECEIVED', 'Fee payment processed', 'FINANCIAL', 'Payment', '#4CAF50', 2, 30, FALSE),
(11, 'FEE_PAYMENT_REVERSED', 'Fee payment reversed', 'FINANCIAL', 'Undo', '#FF9800', 3, 30, TRUE),
(12, 'FEE_OVERDUE', 'Fee payment overdue', 'FINANCIAL', 'Warning', '#F44336', 3, 30, FALSE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    category = EXCLUDED.category,
    icon = EXCLUDED.icon,
    color_code = EXCLUDED.color_code,
    priority_level = EXCLUDED.priority_level,
    default_expiry_days = EXCLUDED.default_expiry_days,
    requires_acknowledgment = EXCLUDED.requires_acknowledgment,
    updated_at = NOW();

-- Transport Fee Management Alerts (20-29)
INSERT INTO alert_types (id, name, description, category, icon, color_code, priority_level, default_expiry_days, requires_acknowledgment) VALUES
(20, 'TRANSPORT_PAYMENT_RECEIVED', 'Transport fee paid', 'FINANCIAL', 'DirectionsBus', '#4CAF50', 2, 30, FALSE),
(21, 'TRANSPORT_PAYMENT_REVERSED', 'Transport fee reversed', 'FINANCIAL', 'Undo', '#FF9800', 3, 30, TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    category = EXCLUDED.category,
    icon = EXCLUDED.icon,
    color_code = EXCLUDED.color_code,
    priority_level = EXCLUDED.priority_level,
    default_expiry_days = EXCLUDED.default_expiry_days,
    requires_acknowledgment = EXCLUDED.requires_acknowledgment,
    updated_at = NOW();

-- Student Management Alerts (30-39) - Future
INSERT INTO alert_types (id, name, description, category, icon, color_code, priority_level, default_expiry_days, requires_acknowledgment) VALUES
(30, 'STUDENT_ENROLLED', 'New student enrolled', 'ACADEMIC', 'PersonAdd', '#2196F3', 1, 30, FALSE),
(31, 'STUDENT_PROMOTED', 'Student promoted to next class', 'ACADEMIC', 'School', '#4CAF50', 1, 30, FALSE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    category = EXCLUDED.category,
    icon = EXCLUDED.icon,
    color_code = EXCLUDED.color_code,
    priority_level = EXCLUDED.priority_level,
    default_expiry_days = EXCLUDED.default_expiry_days,
    requires_acknowledgment = EXCLUDED.requires_acknowledgment,
    updated_at = NOW();

-- Attendance Alerts (40-49) - Future
INSERT INTO alert_types (id, name, description, category, icon, color_code, priority_level, default_expiry_days, requires_acknowledgment) VALUES
(40, 'ATTENDANCE_MARKED', 'Daily attendance marked', 'ACADEMIC', 'HowToReg', '#2196F3', 1, 1, FALSE),
(41, 'ATTENDANCE_LOW', 'Student attendance below threshold', 'ACADEMIC', 'Warning', '#FF9800', 3, 7, TRUE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    category = EXCLUDED.category,
    icon = EXCLUDED.icon,
    color_code = EXCLUDED.color_code,
    priority_level = EXCLUDED.priority_level,
    default_expiry_days = EXCLUDED.default_expiry_days,
    requires_acknowledgment = EXCLUDED.requires_acknowledgment,
    updated_at = NOW();

-- Inventory Alerts (50-59)
INSERT INTO alert_types (id, name, description, category, icon, color_code, priority_level, default_expiry_days, requires_acknowledgment) VALUES
(50, 'INVENTORY_LOW_STOCK', 'Inventory item low stock', 'ADMINISTRATIVE', 'Inventory', '#FF9800', 3, 7, TRUE),
(51, 'INVENTORY_PURCHASE_CREATED', 'Inventory purchase recorded', 'ADMINISTRATIVE', 'ShoppingCart', '#4CAF50', 2, 30, FALSE),
(52, 'INVENTORY_STOCK_PROCURED', 'Inventory stock procured', 'ADMINISTRATIVE', 'LocalShipping', '#2196F3', 2, 30, FALSE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    category = EXCLUDED.category,
    icon = EXCLUDED.icon,
    color_code = EXCLUDED.color_code,
    priority_level = EXCLUDED.priority_level,
    default_expiry_days = EXCLUDED.default_expiry_days,
    requires_acknowledgment = EXCLUDED.requires_acknowledgment,
    updated_at = NOW();

-- Expense Management Alerts (60-69)
INSERT INTO alert_types (id, name, description, category, icon, color_code, priority_level, default_expiry_days, requires_acknowledgment) VALUES
(60, 'EXPENSE_CREATED', 'New expense created', 'FINANCIAL', 'Receipt', '#2196F3', 2, 30, FALSE),
(61, 'EXPENSE_APPROVED', 'Expense approved', 'FINANCIAL', 'CheckCircle', '#4CAF50', 2, 30, FALSE),
(62, 'EXPENSE_REJECTED', 'Expense rejected', 'FINANCIAL', 'Cancel', '#F44336', 3, 30, FALSE),
(63, 'EXPENSE_PAID', 'Expense marked as paid', 'FINANCIAL', 'AccountBalanceWallet', '#4CAF50', 2, 30, FALSE),
(64, 'EXPENSE_UPDATED', 'Expense has been updated', 'FINANCIAL', 'Edit', '#FF9800', 2, 30, FALSE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    category = EXCLUDED.category,
    icon = EXCLUDED.icon,
    color_code = EXCLUDED.color_code,
    priority_level = EXCLUDED.priority_level,
    default_expiry_days = EXCLUDED.default_expiry_days,
    requires_acknowledgment = EXCLUDED.requires_acknowledgment,
    updated_at = NOW();

-- System Alerts (100+)
INSERT INTO alert_types (id, name, description, category, icon, color_code, priority_level, default_expiry_days, requires_acknowledgment) VALUES
(100, 'SYSTEM_ANNOUNCEMENT', 'System announcement', 'SYSTEM', 'Campaign', '#9C27B0', 3, 30, FALSE)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    category = EXCLUDED.category,
    icon = EXCLUDED.icon,
    color_code = EXCLUDED.color_code,
    priority_level = EXCLUDED.priority_level,
    default_expiry_days = EXCLUDED.default_expiry_days,
    requires_acknowledgment = EXCLUDED.requires_acknowledgment,
    updated_at = NOW();

