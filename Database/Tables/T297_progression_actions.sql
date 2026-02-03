-- =====================================================
-- Table: progression_actions
-- Description: Stores progression action types for session progression (metadata table)
-- Dependencies: None (metadata table)
-- Similar to: alert_types (T800)
-- =====================================================

-- Drop existing table
DROP TABLE IF EXISTS progression_actions CASCADE;

-- Create table
CREATE TABLE progression_actions (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    display_order INTEGER DEFAULT 0,
    icon VARCHAR(50),                    -- Material UI icon name for UI display
    color_code VARCHAR(10),              -- Hex color code for UI display
    is_positive BOOLEAN DEFAULT TRUE,    -- TRUE for positive actions (PROMOTED), FALSE for negative (DEMOTED)
    creates_new_session BOOLEAN DEFAULT TRUE,  -- TRUE if action creates entry in new session
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_progression_actions_active ON progression_actions(is_active);
CREATE INDEX IF NOT EXISTS idx_progression_actions_order ON progression_actions(display_order);

-- Add comments
COMMENT ON TABLE progression_actions IS 'Progression action types for session progression (metadata table)';
COMMENT ON COLUMN progression_actions.id IS 'Primary key - manually assigned ID';
COMMENT ON COLUMN progression_actions.name IS 'Action identifier (NEW_ADMISSION, PROMOTED, RETAINED, etc.)';
COMMENT ON COLUMN progression_actions.description IS 'Human-readable description of the action';
COMMENT ON COLUMN progression_actions.display_order IS 'Order for display in UI dropdowns';
COMMENT ON COLUMN progression_actions.icon IS 'Material UI icon name for UI display';
COMMENT ON COLUMN progression_actions.color_code IS 'Hex color code for UI display';
COMMENT ON COLUMN progression_actions.is_positive IS 'Flag for positive/negative action for UI styling';
COMMENT ON COLUMN progression_actions.creates_new_session IS 'Flag indicating if action creates entry in new session';

