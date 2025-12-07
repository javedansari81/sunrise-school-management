-- =====================================================
-- Table: alert_types
-- Description: Stores alert type definitions (LEAVE_REQUEST, FEE_PAYMENT, etc.)
-- Dependencies: None (metadata table)
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS alert_types CASCADE;

-- Create table
CREATE TABLE alert_types (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    icon VARCHAR(50),
    color_code VARCHAR(10),
    priority_level INTEGER DEFAULT 1,
    default_expiry_days INTEGER DEFAULT 30,
    requires_acknowledgment BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_alert_types_category ON alert_types(category);
CREATE INDEX IF NOT EXISTS idx_alert_types_active ON alert_types(is_active);

-- Add comments
COMMENT ON TABLE alert_types IS 'Alert type definitions for the notification system';
COMMENT ON COLUMN alert_types.id IS 'Primary key - manually assigned ID';
COMMENT ON COLUMN alert_types.name IS 'Alert type identifier (LEAVE_REQUEST_CREATED, FEE_PAYMENT_RECEIVED, etc.)';
COMMENT ON COLUMN alert_types.category IS 'Alert category for grouping (LEAVE_MANAGEMENT, FINANCIAL, ACADEMIC, ADMINISTRATIVE, SYSTEM)';
COMMENT ON COLUMN alert_types.icon IS 'Material UI icon name for UI display';
COMMENT ON COLUMN alert_types.color_code IS 'Hex color code for UI display';
COMMENT ON COLUMN alert_types.priority_level IS 'Priority level: 1=Low, 2=Medium, 3=High, 4=Critical';
COMMENT ON COLUMN alert_types.default_expiry_days IS 'Number of days until alert auto-expires';
COMMENT ON COLUMN alert_types.requires_acknowledgment IS 'Flag indicating if user must acknowledge this alert type';

