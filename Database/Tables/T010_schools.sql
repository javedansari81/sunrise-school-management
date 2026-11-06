-- =====================================================
-- Table: schools
-- Description: Tenants. One row per school served by the platform.
--              Every school-owned table carries school_id REFERENCES schools(id).
-- Dependencies: None
-- =====================================================

DROP TABLE IF EXISTS schools CASCADE;

CREATE TABLE schools (
    id SERIAL PRIMARY KEY,
    code VARCHAR(63) NOT NULL,
    name VARCHAR(255) NOT NULL,
    short_name VARCHAR(50),
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(255),
    website VARCHAR(255),
    logo_url TEXT,
    timezone VARCHAR(64) NOT NULL DEFAULT 'Asia/Kolkata',
    currency VARCHAR(3) NOT NULL DEFAULT 'INR',
    academic_year_start_month INTEGER NOT NULL DEFAULT 4,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT schools_code_unique UNIQUE (code),
    -- code is the subdomain label: lowercase letters, digits and hyphens
    CONSTRAINT schools_code_format CHECK (code ~ '^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$'),
    CONSTRAINT schools_status_valid CHECK (status IN ('ACTIVE', 'SUSPENDED')),
    CONSTRAINT schools_start_month_valid CHECK (academic_year_start_month BETWEEN 1 AND 12)
);

COMMENT ON TABLE schools IS 'Tenants. One row per school served by the platform';
COMMENT ON COLUMN schools.code IS 'Subdomain label, for example sunrise in sunrise.<base domain>';
COMMENT ON COLUMN schools.status IS 'ACTIVE or SUSPENDED. Suspended schools cannot log in';
