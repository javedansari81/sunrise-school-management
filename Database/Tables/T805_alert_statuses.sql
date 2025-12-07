-- =====================================================
-- Table: alert_statuses
-- Description: Stores alert status options (UNREAD, READ, ACKNOWLEDGED, etc.)
-- Dependencies: None (metadata table)
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS alert_statuses CASCADE;

-- Create table
CREATE TABLE alert_statuses (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    color_code VARCHAR(10),
    is_final BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_alert_statuses_active ON alert_statuses(is_active);

-- Add comments
COMMENT ON TABLE alert_statuses IS 'Alert status options (UNREAD, READ, ACKNOWLEDGED, DISMISSED, EXPIRED)';
COMMENT ON COLUMN alert_statuses.id IS 'Primary key - manually assigned ID';
COMMENT ON COLUMN alert_statuses.name IS 'Status name';
COMMENT ON COLUMN alert_statuses.color_code IS 'Hex color code for UI display';
COMMENT ON COLUMN alert_statuses.is_final IS 'Flag indicating if this is a terminal status (no further changes allowed)';

