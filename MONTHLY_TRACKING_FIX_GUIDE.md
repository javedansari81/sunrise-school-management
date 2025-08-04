# Monthly Tracking Fix Guide

## 🔍 Problem Description

The Fee Management System's monthly tracking functionality is broken with the error:
> "Monthly fee history not found for this student. Please enable monthly tracking first."

**Root Cause**: After adding soft delete columns (`is_deleted`, `deleted_date`) to the students table in V004 migration, the `enhanced_student_fee_status` database view was not updated to properly exclude soft-deleted students.

## 🛠️ Solution Options

### Option 1: Automated Fix (Recommended)

1. **Set up your environment variables** (if not already done):
   ```bash
   # In your .env file or environment
   DATABASE_URL=postgresql://username:password@localhost:5432/sunrise_school
   ```

2. **Run the automated fix script**:
   ```bash
   python apply_monthly_tracking_fix.py
   ```

3. **Restart your FastAPI server**:
   ```bash
   cd sunrise-backend-fastapi
   uvicorn main:app --reload
   ```

### Option 2: Manual Database Fix

1. **Connect to your PostgreSQL database** using your preferred client (pgAdmin, psql, etc.)

2. **Run the SQL fix script**:
   - Open `fix_monthly_tracking.sql` in your database client
   - Execute the entire script
   - Check for any error messages

3. **Verify the fix worked**:
   ```sql
   SELECT 
       COUNT(*) as total_students,
       COUNT(CASE WHEN has_monthly_tracking THEN 1 END) as with_tracking
   FROM enhanced_student_fee_status 
   WHERE session_year = '2025-26';
   ```

### Option 3: Direct SQL Commands

If you prefer to run individual commands:

```sql
-- 1. Ensure soft delete columns exist and are properly set
UPDATE students 
SET is_deleted = FALSE 
WHERE is_deleted IS NULL;

-- 2. Drop and recreate the problematic view
DROP VIEW IF EXISTS enhanced_student_fee_status CASCADE;

-- 3. Create the fixed view (copy from fix_monthly_tracking.sql)
CREATE OR REPLACE VIEW enhanced_student_fee_status AS
SELECT 
    s.id as student_id,
    s.admission_number,
    s.first_name || ' ' || s.last_name as student_name,
    c.display_name as class_name,
    sy.name as session_year,
    -- ... (rest of the view definition from the SQL file)
WHERE s.is_active = true 
  AND (s.is_deleted = false OR s.is_deleted IS NULL);
```

## 🧪 Testing the Fix

After applying the fix:

1. **Access the Fee Management System**:
   - Navigate to Admin Dashboard → Fee Management
   - Click on "Enhanced Monthly Tracking" tab

2. **Test viewing student monthly history**:
   - Select a session year and class
   - Click the "view" icon for any student
   - The error should no longer appear

3. **Test enabling monthly tracking**:
   - Select students and click "Enable Monthly Tracking"
   - This should work without errors

4. **Verify data integrity**:
   - Check that only active, non-deleted students appear in the list
   - Verify monthly tracking status shows correctly

## 🔧 What the Fix Does

The fix updates the `enhanced_student_fee_status` view to:

1. **Properly filter students**: Excludes soft-deleted students using:
   ```sql
   WHERE s.is_active = true 
     AND (s.is_deleted = false OR s.is_deleted IS NULL)
   ```

2. **Maintain data integrity**: Ensures only active students are included in fee management operations

3. **Preserve existing functionality**: All other features continue to work as before

## 🚨 Troubleshooting

### If you get connection errors:
- Verify your `DATABASE_URL` is correct
- Ensure PostgreSQL is running
- Check your database credentials

### If the view creation fails:
- Check if you have sufficient database permissions
- Ensure all referenced tables exist
- Look for any missing columns or dependencies

### If monthly tracking still doesn't work:
1. Restart your FastAPI backend server
2. Clear your browser cache
3. Check the backend logs for any remaining errors
4. Verify the `enable_monthly_tracking_for_record` function exists in your database

## 📋 Files Involved

- `fix_monthly_tracking.sql` - Main SQL fix script
- `apply_monthly_tracking_fix.py` - Automated Python application script
- `Database/Versioning/V007_fix_enhanced_student_fee_status_view.sql` - Complete migration script

## ✅ Success Indicators

You'll know the fix worked when:
- ✅ No more "Monthly fee history not found" errors
- ✅ Students with monthly tracking show "Enabled" status
- ✅ View dialogs open without errors
- ✅ Monthly tracking can be enabled for new students
- ✅ Payment history displays correctly

## 🎯 Next Steps

After the fix is applied:
1. Test all fee management functionality thoroughly
2. Enable monthly tracking for students who need it
3. Process some test payments to verify the system works end-to-end
4. Consider running the complete database migration scripts if you haven't already
