-- =====================================================
-- Schema Initialization for Sunrise School Management System
-- =====================================================
-- This script creates the database schema and initial setup
-- Run this script FIRST before creating any database objects
--
-- PREREQUISITES:
-- 1. PostgreSQL database 'sunrise_school_db' must exist
-- 2. User 'sunrise_user' must exist with proper permissions
--
-- USAGE:
-- psql -U sunrise_user -d sunrise_school_db -f Database/Schema/00_create_schema.sql
--
-- =====================================================

-- Start transaction
BEGIN;

\echo '=========================================='
\echo 'Initializing Database Schema...'
\echo '=========================================='

-- =====================================================
-- 1. Create Schema
-- =====================================================

\echo ''
\echo 'Step 1: Creating sunrise schema...'

-- Create the sunrise schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS sunrise;

\echo '✓ Schema created'

-- =====================================================
-- 2. Set Search Path
-- =====================================================

\echo ''
\echo 'Step 2: Setting search path...'

-- Set search path to use sunrise schema by default
SET search_path TO sunrise, public;

-- Make it permanent for the current database
ALTER DATABASE sunrise_school_db SET search_path TO sunrise, public;

\echo '✓ Search path configured'

-- =====================================================
-- 3. Install Required Extensions
-- =====================================================

\echo ''
\echo 'Step 3: Installing extensions...'

-- Install pgcrypto for password hashing (if needed)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

\echo '✓ Extensions installed'

-- =====================================================
-- 4. Create Version Tracking Table
-- =====================================================

\echo ''
\echo 'Step 4: Creating version tracking table...'

CREATE TABLE IF NOT EXISTS schema_versions (
    id SERIAL PRIMARY KEY,
    version VARCHAR(10) NOT NULL,
    description TEXT,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    applied_by VARCHAR(100) DEFAULT current_user
);

-- Insert initial version
INSERT INTO schema_versions (version, description)
VALUES ('2.1', 'Initial schema setup with refactored structure')
ON CONFLICT DO NOTHING;

\echo '✓ Version tracking table created'

-- =====================================================
-- 5. Grant Permissions
-- =====================================================

\echo ''
\echo 'Step 5: Granting permissions...'

-- Grant usage on schema to sunrise_user
GRANT USAGE ON SCHEMA sunrise TO sunrise_user;
GRANT CREATE ON SCHEMA sunrise TO sunrise_user;

-- Grant permissions on all tables in schema (for future tables)
ALTER DEFAULT PRIVILEGES IN SCHEMA sunrise 
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO sunrise_user;

-- Grant permissions on all sequences in schema (for future sequences)
ALTER DEFAULT PRIVILEGES IN SCHEMA sunrise 
GRANT USAGE, SELECT ON SEQUENCES TO sunrise_user;

\echo '✓ Permissions granted'

-- Commit transaction
COMMIT;

-- =====================================================
-- Success Message
-- =====================================================

\echo ''
\echo '=========================================='
\echo 'SCHEMA INITIALIZATION COMPLETED!'
\echo '=========================================='
\echo 'Schema: sunrise'
\echo 'Search Path: sunrise, public'
\echo 'Extensions: pgcrypto'
\echo 'Version Tracking: Enabled'
\echo ''
\echo 'Next steps:'
\echo '1. Run table creation scripts from Database/Tables/'
\echo '2. Run function creation scripts from Database/Functions/'
\echo '3. Run view creation scripts from Database/Views/'
\echo '4. Run data load scripts from Database/DataLoads/'
\echo '=========================================='

