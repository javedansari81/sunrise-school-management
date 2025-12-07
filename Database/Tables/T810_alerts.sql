-- =====================================================
-- Table: alerts
-- Description: Stores all system alerts/notifications
-- Dependencies: alert_types, alert_statuses, users
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS alerts CASCADE;

-- Create table
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,

    -- Alert Classification (FK to metadata)
    alert_type_id INTEGER NOT NULL REFERENCES alert_types(id),
    alert_status_id INTEGER NOT NULL DEFAULT 1 REFERENCES alert_statuses(id),

    -- Alert Content
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,

    -- Actor Information (who triggered the alert)
    actor_user_id INTEGER REFERENCES users(id),
    actor_type VARCHAR(20),
    actor_name VARCHAR(200),

    -- Entity Information (what entity was affected)
    entity_type VARCHAR(50) NOT NULL,
    entity_id INTEGER NOT NULL,
    entity_display_name VARCHAR(255),

    -- Target Audience
    target_role VARCHAR(20),
    target_user_id INTEGER REFERENCES users(id),

    -- Additional Context (JSON for extensibility)
    alert_metadata JSONB DEFAULT '{}',

    -- Priority & Timing
    priority_level INTEGER DEFAULT 2,
    expires_at TIMESTAMP WITH TIME ZONE,

    -- Read/Acknowledgment Tracking
    read_at TIMESTAMP WITH TIME ZONE,
    read_by INTEGER REFERENCES users(id),
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    acknowledged_by INTEGER REFERENCES users(id),

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    -- Soft Delete
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_date TIMESTAMP WITH TIME ZONE
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_alerts_type ON alerts(alert_type_id);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(alert_status_id);
CREATE INDEX IF NOT EXISTS idx_alerts_actor ON alerts(actor_user_id);
CREATE INDEX IF NOT EXISTS idx_alerts_entity ON alerts(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_alerts_target_role ON alerts(target_role);
CREATE INDEX IF NOT EXISTS idx_alerts_target_user ON alerts(target_user_id);
CREATE INDEX IF NOT EXISTS idx_alerts_created ON alerts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_priority ON alerts(priority_level DESC, created_at DESC);

-- Composite index for common query patterns
CREATE INDEX IF NOT EXISTS idx_alerts_unread ON alerts(alert_status_id, target_role, created_at DESC)
    WHERE is_deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_alerts_role_unread ON alerts(target_role, alert_status_id, created_at DESC)
    WHERE is_deleted = FALSE;

-- Add comments
COMMENT ON TABLE alerts IS 'Central notification/alert storage for all system activities';
COMMENT ON COLUMN alerts.alert_type_id IS 'FK to alert_types - defines the type of alert';
COMMENT ON COLUMN alerts.alert_status_id IS 'FK to alert_statuses - current status of the alert';
COMMENT ON COLUMN alerts.actor_user_id IS 'User ID who triggered the action (can be NULL for system alerts)';
COMMENT ON COLUMN alerts.actor_type IS 'Type of actor: STUDENT, TEACHER, ADMIN, SYSTEM';
COMMENT ON COLUMN alerts.actor_name IS 'Denormalized actor name for display efficiency';
COMMENT ON COLUMN alerts.entity_type IS 'Type of entity affected: LEAVE_REQUEST, FEE_PAYMENT, TRANSPORT_PAYMENT, etc.';
COMMENT ON COLUMN alerts.entity_id IS 'ID of the affected entity';
COMMENT ON COLUMN alerts.entity_display_name IS 'Denormalized entity name for display efficiency';
COMMENT ON COLUMN alerts.target_role IS 'Target role: ADMIN, TEACHER, STUDENT (NULL = all roles)';
COMMENT ON COLUMN alerts.target_user_id IS 'Specific target user (NULL = broadcast to role)';
COMMENT ON COLUMN alerts.alert_metadata IS 'JSON field for storing additional context (amounts, dates, etc.)';
COMMENT ON COLUMN alerts.priority_level IS 'Priority: 1=Low, 2=Normal, 3=High, 4=Critical';

