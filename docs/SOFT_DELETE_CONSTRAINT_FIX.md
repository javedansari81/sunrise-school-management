# Soft-Delete Constraint Fix Documentation

## Problem Description

When an admin attempts to create a new teacher record using an `employee_id` that belongs to a previously soft-deleted teacher, the system shows a database constraint error instead of a user-friendly message.

**Error Example:**
```
DETAIL: Key (employee_id)=(EMP001) already exists.
```

## Root Cause

The database had simple unique constraints on `employee_id` and `email` columns that didn't consider the `is_deleted` flag:

```sql
-- Problematic constraints
ALTER TABLE teachers ADD CONSTRAINT uk_teachers_employee_id UNIQUE (employee_id);
ALTER TABLE teachers ADD CONSTRAINT uk_teachers_email UNIQUE (email);
```

These constraints prevented inserting new records with the same identifiers, even when existing records were soft-deleted.

## Solution Overview

### 1. Database Migration (V1.5)

**File:** `Database/Versioning/V1.5__fix_soft_delete_unique_constraints.sql`

**Key Changes:**
- Replaced simple unique constraints with **partial unique constraints**
- Constraints only apply to non-deleted records (`WHERE is_deleted IS FALSE OR is_deleted IS NULL`)
- Applied to both teachers and students tables

**New Constraints:**
```sql
-- Teachers
CREATE UNIQUE INDEX uk_teachers_employee_id_active 
ON teachers (employee_id) 
WHERE (is_deleted IS FALSE OR is_deleted IS NULL);

CREATE UNIQUE INDEX uk_teachers_email_active 
ON teachers (email) 
WHERE (is_deleted IS FALSE OR is_deleted IS NULL) AND email IS NOT NULL;

-- Students  
CREATE UNIQUE INDEX uk_students_admission_number_active 
ON students (admission_number) 
WHERE (is_deleted IS FALSE OR is_deleted IS NULL);

CREATE UNIQUE INDEX uk_students_email_active 
ON students (email) 
WHERE (is_deleted IS FALSE OR is_deleted IS NULL) AND email IS NOT NULL;
```

### 2. Enhanced Error Handling

**Files Updated:**
- `app/api/v1/endpoints/teachers.py`
- `app/api/v1/endpoints/students.py`

**Features Added:**
- Try-catch blocks for `IntegrityError`
- User-friendly error messages
- Detection of soft-deleted records causing conflicts
- Proper database rollback on errors

### 3. Validation Logic

**File:** `app/utils/soft_delete_helpers.py`

**Functions:**
- `validate_teacher_creation_with_soft_delete_check()`
- `validate_student_creation_with_soft_delete_check()`
- `generate_replacement_success_message()`

## Implementation Details

### Expected Behavior After Fix

1. **Active Record Exists:**
   - Error: "Teacher with this employee ID already exists"

2. **Only Soft-Deleted Record Exists:**
   - Success: "Teacher Jane Smith created successfully (previous record with employee ID EMP001 was archived)"

3. **No Existing Records:**
   - Normal creation with standard success message

### User Messages

**Success Messages:**
```
Teacher John Doe created successfully (previous record with employee ID EMP001 was archived)
Student Alice Johnson created successfully (previous record with admission number ADM001 was archived)
```

**Error Messages:**
```
Teacher with this employee ID already exists
Student with this admission number already exists
Teacher with email john@example.com exists in archived records. Please contact system administrator to resolve this conflict.
```

## Installation Steps

### 1. Apply Database Migration

**Option A: Using the migration script**
```bash
cd sunrise-backend-fastapi
python scripts/apply_soft_delete_migration.py
```

**Option B: Manual SQL execution**
```bash
psql -d your_database -f Database/Versioning/V1.5__fix_soft_delete_unique_constraints.sql
```

### 2. Verify Installation

**Run the test script:**
```bash
python tests/test_database_constraint_fix.py
```

**Expected Output:**
```
✅ Database migration test PASSED - partial unique constraints working correctly
✅ Email constraint test PASSED - can reuse emails from soft-deleted records
```

### 3. Test in UI

1. Create a teacher with employee ID "TEST001"
2. Soft delete the teacher (set `is_deleted = TRUE`)
3. Try to create a new teacher with employee ID "TEST001"
4. Should succeed with success message about archived record

## Technical Details

### Database Schema Changes

**Before (Problematic):**
```sql
employee_id VARCHAR(50) UNIQUE NOT NULL
email VARCHAR(255) UNIQUE NOT NULL
```

**After (Fixed):**
```sql
employee_id VARCHAR(50) NOT NULL  -- No simple unique constraint
email VARCHAR(255) NOT NULL       -- No simple unique constraint

-- Partial unique indexes instead
CREATE UNIQUE INDEX uk_teachers_employee_id_active 
ON teachers (employee_id) 
WHERE (is_deleted IS FALSE OR is_deleted IS NULL);
```

### Code Changes Summary

1. **Enhanced API Endpoints:**
   - Added `IntegrityError` handling
   - Improved error messages
   - Database rollback on errors

2. **Validation Helpers:**
   - Soft-delete detection functions
   - Success message generation
   - Comprehensive validation logic

3. **Test Coverage:**
   - Database constraint tests
   - API error handling tests
   - Integration workflow tests

## Troubleshooting

### Common Issues

1. **Migration Not Applied:**
   ```
   ❌ Database constraint error (migration may not be applied)
   ```
   **Solution:** Run the migration script or apply SQL manually

2. **Permission Errors:**
   ```
   ERROR: permission denied to create index
   ```
   **Solution:** Ensure database user has CREATE privileges

3. **Existing Data Conflicts:**
   ```
   ERROR: could not create unique index
   ```
   **Solution:** Clean up duplicate active records before migration

### Verification Queries

**Check if migration was applied:**
```sql
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'teachers' 
  AND indexname LIKE '%_active';
```

**Test soft-delete functionality:**
```sql
-- This should work after migration
INSERT INTO teachers (employee_id, first_name, last_name, email, phone, position, joining_date, is_deleted) 
VALUES ('TEST001', 'Old', 'Teacher', 'old@test.com', '1111111111', 'Teacher', CURRENT_DATE, TRUE);

INSERT INTO teachers (employee_id, first_name, last_name, email, phone, position, joining_date) 
VALUES ('TEST001', 'New', 'Teacher', 'new@test.com', '2222222222', 'Teacher', CURRENT_DATE);
```

## Files Modified

### Database Files
- `Database/Versioning/V1.5__fix_soft_delete_unique_constraints.sql` (NEW)

### Backend Files
- `app/api/v1/endpoints/teachers.py` (MODIFIED)
- `app/api/v1/endpoints/students.py` (MODIFIED)
- `app/utils/soft_delete_helpers.py` (EXISTING)

### Test Files
- `tests/test_database_constraint_fix.py` (NEW)
- `tests/test_soft_delete_validation.py` (EXISTING)

### Scripts
- `scripts/apply_soft_delete_migration.py` (NEW)

## Success Criteria

✅ **Database Migration Applied:** Partial unique constraints created  
✅ **No Constraint Errors:** Can create records with same identifiers as soft-deleted ones  
✅ **User-Friendly Messages:** Clear success/error messages shown  
✅ **Proper Validation:** Active records still prevent duplicates  
✅ **Email Support:** Email validation also works with soft-deleted records  
✅ **Test Coverage:** Comprehensive tests verify functionality
