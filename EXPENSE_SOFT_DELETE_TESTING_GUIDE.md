# Expense Soft Delete Testing Guide

## Overview
This guide provides comprehensive testing procedures for the newly implemented soft delete functionality in the expense management system.

## Pre-Testing Setup

### 1. Database Migration
**IMPORTANT**: Run the SQL migration script before testing:

```bash
# Connect to your PostgreSQL database and run:
psql -h localhost -U postgres -d sunrise_school_db -f V006_expenses_soft_delete_migration.sql
```

**Expected Output:**
- ✅ Migration completed successfully!
- All existing expenses marked as active (is_deleted = FALSE)
- New indexes created for performance

### 2. Application Restart
Restart the FastAPI backend to load the updated models:
```bash
# Stop and restart your FastAPI server
```

### 3. Verify Database Schema
Check that the new columns exist:
```sql
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'expenses' 
  AND column_name IN ('is_deleted', 'deleted_date')
ORDER BY column_name;
```

**Expected Results:**
- `is_deleted`: boolean, NOT NULL, default FALSE
- `deleted_date`: timestamp with time zone, nullable

## Testing Scenarios

### Test 1: Basic Soft Delete Functionality

#### Steps:
1. Navigate to `/admin/expenses`
2. Note the current total expense count in summary cards
3. Select any expense record and click the delete button
4. Confirm deletion in the popup dialog

#### Expected Results:
- ✅ Success message: "Expense deleted successfully"
- ✅ Expense disappears from the list immediately
- ✅ Summary statistics update to reflect the deletion
- ✅ Total expense count decreases by 1
- ✅ Appropriate status card (Pending/Approved/Rejected) count decreases

#### Database Verification:
```sql
-- Check that record still exists but is marked as deleted
SELECT id, description, total_amount, is_deleted, deleted_date 
FROM expenses 
WHERE id = [DELETED_EXPENSE_ID];
```

**Expected**: `is_deleted = TRUE`, `deleted_date` has timestamp

### Test 2: UI Data Consistency

#### Steps:
1. Before deletion: Note expense list count and summary totals
2. Delete an expense
3. Refresh the page manually
4. Check expense list and summary cards

#### Expected Results:
- ✅ Deleted expense does not reappear after page refresh
- ✅ Summary statistics remain consistent
- ✅ No duplicate entries or missing data
- ✅ Pagination works correctly with reduced record count

### Test 3: Authorization Testing

#### Test 3a: Delete Own Expense (Non-Admin User)
1. Login as a non-admin user (teacher/staff)
2. Create an expense or find an expense created by this user
3. Attempt to delete the expense

**Expected**: ✅ Deletion succeeds

#### Test 3b: Delete Other's Expense (Non-Admin User)
1. Login as a non-admin user
2. Attempt to delete an expense created by another user

**Expected**: ❌ Error message: "You can only delete your own expenses unless you are an admin"

#### Test 3c: Admin Delete Any Expense
1. Login as an admin user
2. Attempt to delete any expense (regardless of creator)

**Expected**: ✅ Deletion succeeds

### Test 4: Error Handling

#### Test 4a: Delete Non-Existent Expense
```bash
# Test API directly
curl -X DELETE "http://localhost:8000/api/v1/expenses/99999" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected**: ❌ 404 Error: "Expense not found"

#### Test 4b: Delete Already Deleted Expense
1. Delete an expense successfully
2. Attempt to delete the same expense again (using direct API call)

**Expected**: ❌ 400 Error: "Expense is already deleted"

### Test 5: Statistics Accuracy

#### Steps:
1. Record initial statistics (total, pending, approved, rejected amounts)
2. Delete expenses of different statuses (1 pending, 1 approved, 1 rejected)
3. Verify statistics update correctly

#### Expected Results:
- ✅ Total amount decreases by sum of deleted expenses
- ✅ Pending amount decreases by amount of deleted pending expense
- ✅ Approved amount decreases by amount of deleted approved expense
- ✅ Rejected count decreases by 1
- ✅ Category breakdown excludes deleted expenses
- ✅ Payment method breakdown excludes deleted expenses

### Test 6: Performance Testing

#### Steps:
1. Create multiple expenses (10-20 records)
2. Delete several expenses
3. Test page load times and query performance

#### Expected Results:
- ✅ Page loads quickly (< 2 seconds)
- ✅ No noticeable performance degradation
- ✅ Database queries use indexes efficiently

## Database Verification Queries

### Check Soft Delete Status
```sql
-- View all expenses with their delete status
SELECT 
    id, 
    description, 
    total_amount, 
    expense_status_id,
    is_deleted, 
    deleted_date,
    created_at
FROM expenses 
ORDER BY created_at DESC;
```

### Verify Active Records Only
```sql
-- This should match what the UI shows
SELECT COUNT(*) as active_expenses 
FROM expenses 
WHERE is_deleted = FALSE;
```

### Check Deleted Records
```sql
-- View soft-deleted records
SELECT 
    id, 
    description, 
    total_amount, 
    deleted_date,
    EXTRACT(EPOCH FROM (NOW() - deleted_date))/60 as minutes_since_deletion
FROM expenses 
WHERE is_deleted = TRUE 
ORDER BY deleted_date DESC;
```

### Statistics Verification
```sql
-- Manual statistics calculation (should match API response)
SELECT 
    COUNT(*) as total_expenses,
    COUNT(CASE WHEN expense_status_id = 1 THEN 1 END) as pending_expenses,
    COUNT(CASE WHEN expense_status_id = 2 THEN 1 END) as approved_expenses,
    COUNT(CASE WHEN expense_status_id = 3 THEN 1 END) as rejected_expenses,
    SUM(total_amount) as total_amount,
    SUM(CASE WHEN expense_status_id = 1 THEN total_amount ELSE 0 END) as pending_amount,
    SUM(CASE WHEN expense_status_id = 2 THEN total_amount ELSE 0 END) as approved_amount,
    SUM(CASE WHEN expense_status_id = 3 THEN total_amount ELSE 0 END) as rejected_amount
FROM expenses 
WHERE is_deleted = FALSE;
```

## Troubleshooting

### Issue: Migration Fails
**Solution**: Check PostgreSQL connection and permissions. Ensure database exists.

### Issue: Columns Not Found Error
**Solution**: Restart FastAPI application after running migration.

### Issue: Statistics Not Updating
**Solution**: Check browser console for API errors. Verify backend logs.

### Issue: Deleted Records Still Visible
**Solution**: 
1. Check if migration ran successfully
2. Verify CRUD methods are filtering `is_deleted = FALSE`
3. Clear browser cache and refresh

## Success Criteria Checklist

- [ ] ✅ SQL migration runs without errors
- [ ] ✅ Deleted expenses disappear from UI immediately
- [ ] ✅ Summary statistics update correctly after deletion
- [ ] ✅ Deleted records remain in database with `is_deleted = TRUE`
- [ ] ✅ Authorization rules work correctly (own expenses vs admin)
- [ ] ✅ Error handling works for edge cases
- [ ] ✅ Page refresh doesn't show deleted records
- [ ] ✅ No performance degradation
- [ ] ✅ Database queries use proper indexes
- [ ] ✅ All expense list filters exclude deleted records

## Post-Testing Cleanup

### Optional: View Deleted Records (Admin Only)
If you need to see deleted records for audit purposes:
```sql
-- Admin query to see all records including deleted
SELECT 
    id, 
    description, 
    total_amount, 
    is_deleted, 
    deleted_date,
    CASE WHEN is_deleted THEN 'DELETED' ELSE 'ACTIVE' END as status
FROM expenses 
ORDER BY created_at DESC;
```

### Restore Deleted Record (Emergency)
If you need to restore a soft-deleted record:
```sql
-- CAUTION: Only use in emergencies
UPDATE expenses 
SET is_deleted = FALSE, deleted_date = NULL 
WHERE id = [EXPENSE_ID] AND is_deleted = TRUE;
```

## Contact
If you encounter any issues during testing, check the backend logs for detailed error messages and stack traces.
