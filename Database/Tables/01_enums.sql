-- =====================================================
-- PostgreSQL ENUM Types for Sunrise School Management
-- =====================================================
-- This file contains all ENUM type definitions used across the database
-- Note: These ENUMs are currently not used in favor of VARCHAR with CHECK constraints
-- for better compatibility with SQLAlchemy

-- Session Year ENUM (Academic Years)
-- Currently using VARCHAR(10) with CHECK constraints instead
-- CREATE TYPE session_year_enum AS ENUM ('2022-23', '2023-24', '2024-25', '2025-26', '2026-27');

-- Payment Type ENUM (Fee Payment Frequencies)
-- Currently using VARCHAR(20) with CHECK constraints instead
-- CREATE TYPE payment_type_enum AS ENUM ('Monthly', 'Quarterly', 'Half Yearly', 'Yearly');

-- Payment Status ENUM (Fee Payment Status)
-- Currently using VARCHAR(20) with CHECK constraints instead
-- CREATE TYPE payment_status_enum AS ENUM ('Pending', 'Partial', 'Paid', 'Overdue');

-- Payment Method ENUM (Payment Methods)
-- Currently using VARCHAR(20) with CHECK constraints instead
-- CREATE TYPE payment_method_enum AS ENUM ('Cash', 'Cheque', 'Online', 'UPI', 'Card');

-- User Role ENUM (System User Roles)
-- Currently using VARCHAR(20) with CHECK constraints instead
-- CREATE TYPE user_role_enum AS ENUM ('admin', 'teacher', 'student', 'parent');

-- Gender ENUM (Gender Options)
-- Currently using VARCHAR(10) with CHECK constraints instead
-- CREATE TYPE gender_enum AS ENUM ('Male', 'Female', 'Other');

-- Leave Status ENUM (Leave Application Status)
-- Currently using VARCHAR(20) with CHECK constraints instead
-- CREATE TYPE leave_status_enum AS ENUM ('Pending', 'Approved', 'Rejected');

-- Leave Type ENUM (Types of Leave)
-- Currently using VARCHAR(30) with CHECK constraints instead
-- CREATE TYPE leave_type_enum AS ENUM ('Sick Leave', 'Casual Leave', 'Emergency Leave', 'Medical Leave');

-- Attendance Status ENUM (Daily Attendance Status)
-- Currently using VARCHAR(10) with CHECK constraints instead
-- CREATE TYPE attendance_status_enum AS ENUM ('Present', 'Absent', 'Late', 'Half Day');

-- =====================================================
-- NOTES:
-- =====================================================
-- 1. All ENUM types are commented out because we're using VARCHAR with CHECK constraints
-- 2. This provides better compatibility with SQLAlchemy ORM
-- 3. CHECK constraints are defined in individual table files
-- 4. If you want to use native PostgreSQL ENUMs, uncomment the types above
--    and update the table definitions accordingly
-- =====================================================
