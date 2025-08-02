# Leave Request Management Test Cases

## Test Case 3.1: Create New Leave Request - Student
**Objective**: Verify admin can create a new leave request for a student
**Preconditions**: Admin user logged in, student data available
**Steps**:
1. Click "New Leave Request" button
2. Select "Student" as applicant type
3. Select a student from dropdown
4. Select leave type (e.g., "Sick Leave")
5. Set start date and end date
6. Enter reason for leave
7. Fill parent consent details
8. Enter emergency contact information
9. Click "Submit"

**Expected Results**:
- Dialog opens correctly
- All form fields are available and functional
- Student dropdown populated from database
- Leave type dropdown populated from configuration
- Date pickers work correctly
- Form validation works (required fields)
- Success message displayed after submission
- New request appears in the list

**Test Data**: Valid student records, leave types

---

## Test Case 3.2: Create New Leave Request - Teacher
**Objective**: Verify admin can create a new leave request for a teacher
**Preconditions**: Admin user logged in, teacher data available
**Steps**:
1. Click "New Leave Request" button
2. Select "Teacher" as applicant type
3. Select a teacher from dropdown
4. Select leave type (e.g., "Personal Leave")
5. Set start date and end date
6. Enter reason for leave
7. Select substitute teacher (if required)
8. Mark substitute arranged checkbox
9. Click "Submit"

**Expected Results**:
- Teacher-specific form fields displayed
- Teacher dropdown populated correctly
- Substitute teacher options available
- Form submission works correctly
- Request created successfully

**Test Data**: Valid teacher records, substitute teacher options

---

## Test Case 3.3: Form Validation - Required Fields
**Objective**: Verify form validation for required fields
**Preconditions**: Admin user on new leave request dialog
**Steps**:
1. Open new leave request dialog
2. Leave required fields empty
3. Attempt to submit form
4. Verify validation messages
5. Fill one field at a time and test validation

**Expected Results**:
- Form cannot be submitted with empty required fields
- Appropriate validation messages displayed
- Validation messages clear when fields are filled
- Submit button disabled until form is valid

---

## Test Case 3.4: Date Validation
**Objective**: Verify date field validation works correctly
**Preconditions**: Admin user on new leave request dialog
**Steps**:
1. Set end date before start date
2. Verify validation error
3. Set start date in the past
4. Verify validation (if applicable)
5. Set valid date range
6. Verify validation passes

**Expected Results**:
- End date cannot be before start date
- Appropriate date validation messages
- Total days calculated automatically
- Date picker restrictions work correctly

---

## Test Case 3.5: Half-Day Leave Request
**Objective**: Verify half-day leave request functionality
**Preconditions**: Admin user creating leave request
**Steps**:
1. Create new leave request
2. Check "Half Day" option
3. Select session (morning/afternoon)
4. Verify total days shows 0.5 or 1
5. Submit request

**Expected Results**:
- Half-day option works correctly
- Session selection available
- Total days calculated correctly
- Half-day requests saved properly

---

## Test Case 3.6: View Leave Request Details
**Objective**: Verify viewing leave request details works correctly
**Preconditions**: Leave requests exist in database
**Steps**:
1. Click "View" icon on a leave request
2. Verify dialog opens with request details
3. Check all information is displayed correctly
4. Verify read-only mode (no editing)
5. Close dialog

**Expected Results**:
- View dialog opens correctly
- All request details displayed
- Fields are read-only
- Close button works correctly
- No edit functionality in view mode

---

## Test Case 3.7: Edit Leave Request
**Objective**: Verify editing existing leave request works correctly
**Preconditions**: Pending leave requests exist
**Steps**:
1. Click "Edit" icon on a pending leave request
2. Modify some fields (reason, dates, etc.)
3. Save changes
4. Verify updates are reflected

**Expected Results**:
- Edit dialog opens with pre-filled data
- All fields are editable (for pending requests)
- Changes save successfully
- Updated data displayed in list
- Success message shown

---

## Test Case 3.8: Delete Leave Request
**Objective**: Verify deleting leave request works correctly
**Preconditions**: Pending leave requests exist
**Steps**:
1. Click "Delete" icon on a pending leave request
2. Confirm deletion in confirmation dialog
3. Verify request is removed from list

**Expected Results**:
- Confirmation dialog appears
- Request deleted successfully
- Request removed from UI
- Success message displayed
- Cannot delete approved/rejected requests

---

## Test Case 3.9: Bulk Operations
**Objective**: Verify bulk operations work correctly (if implemented)
**Preconditions**: Multiple leave requests exist
**Steps**:
1. Select multiple leave requests using checkboxes
2. Perform bulk action (approve/reject)
3. Verify all selected requests are updated

**Expected Results**:
- Multiple selection works correctly
- Bulk actions apply to all selected items
- Status updates correctly for all items
- Appropriate confirmation dialogs shown

---

## Test Case 3.10: Leave Request Status Workflow
**Objective**: Verify leave request status transitions work correctly
**Preconditions**: Leave requests in different statuses
**Steps**:
1. Create new request (should be "Pending")
2. Approve the request
3. Verify status changes to "Approved"
4. Try to edit approved request
5. Verify editing is restricted

**Expected Results**:
- New requests start as "Pending"
- Status transitions work correctly
- Approved/Rejected requests cannot be edited
- Status colors display correctly

---

## Test Case 3.11: Medical Certificate Upload
**Objective**: Verify medical certificate upload functionality
**Preconditions**: Leave type requiring medical certificate
**Steps**:
1. Create leave request for sick leave
2. Upload medical certificate file
3. Verify file upload works
4. Submit request
5. Verify certificate URL is saved

**Expected Results**:
- File upload component works
- Supported file types accepted
- File size validation works
- Certificate URL saved correctly
- File accessible after submission

---

## Test Case 3.12: Emergency Contact Validation
**Objective**: Verify emergency contact field validation
**Preconditions**: Creating student leave request
**Steps**:
1. Create student leave request
2. Enter invalid phone number format
3. Verify validation error
4. Enter valid phone number
5. Verify validation passes

**Expected Results**:
- Phone number format validation works
- Appropriate error messages displayed
- Valid formats accepted
- Required field validation works

---

## Test Case 3.13: Substitute Teacher Assignment
**Objective**: Verify substitute teacher assignment for teacher leaves
**Preconditions**: Teacher leave request, substitute teachers available
**Steps**:
1. Create teacher leave request
2. Select substitute teacher from dropdown
3. Mark "Substitute Arranged" checkbox
4. Submit request
5. Verify substitute assignment saved

**Expected Results**:
- Substitute teacher dropdown populated
- Selection saves correctly
- Substitute arranged flag works
- Information displayed in request details

---

## Test Case 3.14: Leave Request Search and Filter
**Objective**: Verify search and filter functionality works correctly
**Preconditions**: Multiple leave requests with different attributes
**Steps**:
1. Use applicant type filter
2. Use leave status filter
3. Use leave type filter
4. Use date range filter
5. Combine multiple filters
6. Clear filters

**Expected Results**:
- All filters work independently
- Combined filters work correctly
- Filter results update immediately
- Clear filters resets to all data
- Filter state maintained during navigation

---

## Test Case 3.15: Responsive Design - Mobile View
**Objective**: Verify leave request management works on mobile devices
**Preconditions**: Mobile device or browser developer tools
**Steps**:
1. Access leave management on mobile
2. Test creating new request
3. Test viewing request details
4. Test table scrolling and interaction

**Expected Results**:
- Mobile layout displays correctly
- All functionality accessible on mobile
- Touch interactions work properly
- Text and buttons appropriately sized
- Horizontal scrolling works for tables

---

## Test Case 3.16: Error Handling - API Failures
**Objective**: Verify graceful handling of API failures during CRUD operations
**Preconditions**: Ability to simulate API failures
**Steps**:
1. Simulate server error during create operation
2. Verify error message displayed
3. Simulate network timeout during update
4. Verify timeout handling
5. Test recovery after connection restored

**Expected Results**:
- Appropriate error messages displayed
- No data corruption occurs
- User can retry operations
- Application remains stable
- Clear guidance provided to user
