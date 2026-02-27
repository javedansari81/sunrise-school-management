-- Migration: Reduce attendance statuses from 7 to 3 (Present, Absent, Leave)
-- Date: 2026-02-27
-- Description: 
--   1. Update attendance records with statuses 3,4,5,6 to status 1 (PRESENT)
--   2. Delete statuses 3,4,5,6 from attendance_statuses table
--   3. Keep statuses: 1 (PRESENT), 2 (ABSENT), 7 (LEAVE)

-- Step 1: Update attendance records - change status 3,4,5,6 to 1 (PRESENT)
-- This treats LATE, HALF_DAY, EXCUSED, HOLIDAY as PRESENT
UPDATE sunrise.attendance_records 
SET attendance_status_id = 1, 
    updated_at = NOW()
WHERE attendance_status_id IN (3, 4, 5, 6);

-- Step 2: Delete the unused statuses from the attendance_statuses table
DELETE FROM sunrise.attendance_statuses 
WHERE id IN (3, 4, 5, 6);

-- Verify the changes
SELECT 'Remaining statuses:' as message;
SELECT id, name, description, color_code 
FROM sunrise.attendance_statuses 
ORDER BY id;

SELECT 'Attendance records count by status:' as message;
SELECT 
    s.id,
    s.name,
    s.description,
    COUNT(ar.id) as record_count
FROM sunrise.attendance_statuses s
LEFT JOIN sunrise.attendance_records ar ON ar.attendance_status_id = s.id
GROUP BY s.id, s.name, s.description
ORDER BY s.id;

