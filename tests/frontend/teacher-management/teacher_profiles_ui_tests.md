# Teacher Profiles UI Test Cases

## Test Case 1: Teacher Profiles Page Loading
**Objective**: Verify the Teacher Profiles page loads correctly with all components
**Preconditions**: User is logged in as admin
**Steps**:
1. Navigate to `/admin/teachers`
2. Verify page title displays "Teacher Profiles"
3. Verify "New Teacher" button is visible and positioned correctly
4. Verify filters section is displayed with search and dropdown filters
5. Verify tabs are displayed (All Teachers, Active Teachers, Inactive Teachers)
6. Verify table structure is correct with appropriate columns

**Expected Results**:
- Page loads without errors
- All UI components are properly positioned and styled
- Configuration is loaded successfully
- Table shows appropriate headers: Teacher, Employee ID, Department, Position, Contact, Status, Actions

---

## Test Case 2: Teacher Search Functionality
**Objective**: Verify teacher search works correctly
**Preconditions**: Teacher Profiles page is loaded with existing teachers
**Steps**:
1. Enter teacher name in search field
2. Verify results are filtered in real-time
3. Clear search and verify all teachers are shown again
4. Search by employee ID
5. Search by email address
6. Test partial matches

**Expected Results**:
- Search filters results immediately without requiring submit button
- Results match search criteria (name, employee ID, email)
- Partial matches work correctly
- Clear search restores full list
- Search is case-insensitive

---

## Test Case 3: Teacher Filters Functionality
**Objective**: Verify filter dropdowns work correctly
**Preconditions**: Teacher Profiles page is loaded
**Steps**:
1. Select department filter
2. Verify teachers are filtered by selected department
3. Select position filter
4. Verify combined filters work correctly
5. Select qualification filter
6. Select employment status filter
7. Reset filters to "All"

**Expected Results**:
- Each filter works independently
- Multiple filters can be combined
- Filter options are populated from configuration
- "All" option shows all teachers
- Filters update results in real-time

---

## Test Case 4: Teacher Tabs Functionality
**Objective**: Verify tab switching works correctly
**Preconditions**: Teacher Profiles page is loaded with active and inactive teachers
**Steps**:
1. Click "All Teachers" tab
2. Verify all teachers are displayed
3. Click "Active Teachers" tab
4. Verify only active teachers are shown
5. Click "Inactive Teachers" tab
6. Verify only inactive teachers are shown
7. Verify teacher counts in tab labels are correct

**Expected Results**:
- Tab switching works smoothly
- Correct teachers are displayed for each tab
- Teacher counts are accurate
- Active tab is visually highlighted
- Table content updates correctly

---

## Test Case 5: New Teacher Dialog
**Objective**: Verify the New Teacher dialog functions correctly
**Preconditions**: Teacher Profiles page is loaded
**Steps**:
1. Click "New Teacher" button
2. Verify dialog opens with correct title
3. Verify all form fields are present and properly labeled
4. Test form validation (required fields)
5. Fill in valid teacher data
6. Submit form
7. Verify teacher is created and appears in list
8. Test dialog cancel functionality

**Expected Results**:
- Dialog opens with "New Teacher Profile" title
- All required fields are marked appropriately
- Form validation prevents submission with missing required data
- Valid data creates teacher successfully
- New teacher appears in the table
- Cancel button closes dialog without saving

---

## Test Case 6: Edit Teacher Dialog
**Objective**: Verify teacher editing functionality
**Preconditions**: Teacher Profiles page is loaded with existing teachers
**Steps**:
1. Click edit icon for a teacher
2. Verify dialog opens with "Edit Teacher Profile" title
3. Verify form is pre-populated with teacher data
4. Modify some fields
5. Save changes
6. Verify changes are reflected in the table
7. Test validation on edit form

**Expected Results**:
- Edit dialog opens with correct title
- Form fields are pre-populated with existing data
- Changes can be saved successfully
- Updated data appears in the table
- Validation works on edit form
- Cancel preserves original data

---

## Test Case 7: View Teacher Dialog
**Objective**: Verify view-only teacher dialog
**Preconditions**: Teacher Profiles page is loaded with existing teachers
**Steps**:
1. Click view icon for a teacher
2. Verify dialog opens with "View Teacher Profile" title
3. Verify all fields are displayed but disabled
4. Verify only "Close" button is available
5. Verify all teacher information is displayed correctly
6. Close dialog

**Expected Results**:
- View dialog opens with correct title
- All form fields are disabled/read-only
- Only "Close" button is present (no Save/Update)
- All teacher data is displayed correctly
- Dialog can be closed properly

---

## Test Case 8: Teacher Actions (Delete)
**Objective**: Verify teacher deletion functionality
**Preconditions**: Teacher Profiles page is loaded with existing teachers
**Steps**:
1. Click delete icon for a teacher
2. Verify confirmation dialog appears
3. Confirm deletion
4. Verify teacher is soft deleted (moved to inactive)
5. Verify teacher no longer appears in active list
6. Check inactive teachers tab to confirm soft delete

**Expected Results**:
- Delete confirmation dialog appears
- Confirmation is required before deletion
- Teacher is soft deleted (not permanently removed)
- Teacher moves from active to inactive status
- Soft delete preserves teacher data
- UI updates correctly after deletion

---

## Test Case 9: Teacher Contact Information Display
**Objective**: Verify teacher contact information is displayed correctly
**Preconditions**: Teacher Profiles page is loaded with teachers having contact info
**Steps**:
1. Verify phone numbers are displayed with phone icon
2. Verify email addresses are displayed with email icon
3. Verify contact information formatting
4. Test contact information in different screen sizes
5. Verify emergency contact information in view dialog

**Expected Results**:
- Phone numbers display with appropriate icon
- Email addresses display with appropriate icon
- Contact information is properly formatted
- Information is readable on mobile devices
- Emergency contact shows in detailed view

---

## Test Case 10: Teacher Profile Avatar and Display
**Objective**: Verify teacher profile display elements
**Preconditions**: Teacher Profiles page is loaded
**Steps**:
1. Verify teacher avatars show initials correctly
2. Verify teacher names are displayed prominently
3. Verify qualification information is shown
4. Verify status chips display correctly
5. Verify composite identifier format in dropdowns

**Expected Results**:
- Avatars show first and last name initials
- Teacher names are clearly visible
- Qualification appears as secondary text
- Status chips use appropriate colors (green for active, gray for inactive)
- Composite format shows "John Smith (EMP001)" in references

---

## Test Case 11: Responsive Design
**Objective**: Verify teacher management works on different screen sizes
**Preconditions**: Teacher Profiles page is loaded
**Steps**:
1. Test on desktop (1920x1080)
2. Test on tablet (768x1024)
3. Test on mobile (375x667)
4. Verify table scrolling on small screens
5. Verify dialog responsiveness
6. Test filter layout on mobile

**Expected Results**:
- Layout adapts to different screen sizes
- Table is scrollable horizontally on small screens
- Dialogs are properly sized for mobile
- Filters stack appropriately on mobile
- All functionality remains accessible
- Text remains readable at all sizes

---

## Test Case 12: Performance and Loading
**Objective**: Verify performance with large datasets
**Preconditions**: Database contains 100+ teachers
**Steps**:
1. Load Teacher Profiles page
2. Measure initial load time
3. Test search performance with large dataset
4. Test filter performance
5. Test pagination if implemented
6. Verify loading indicators

**Expected Results**:
- Page loads within acceptable time (< 3 seconds)
- Search results appear quickly (< 1 second)
- Filters respond immediately
- Loading indicators show during data fetching
- No performance degradation with large datasets
- Smooth scrolling and interactions

---

## Test Case 13: Error Handling
**Objective**: Verify proper error handling in teacher management
**Preconditions**: Teacher Profiles page is loaded
**Steps**:
1. Test with network disconnection
2. Test with invalid server responses
3. Test form submission with server errors
4. Test configuration loading failures
5. Verify error messages are user-friendly
6. Test error recovery

**Expected Results**:
- Network errors show appropriate messages
- Server errors are handled gracefully
- Form errors are displayed clearly
- Configuration errors don't break the page
- Error messages are helpful and actionable
- Users can recover from errors

---

## Test Case 14: Integration with Authentication
**Objective**: Verify teacher management respects authentication and permissions
**Preconditions**: Various user roles available
**Steps**:
1. Test as admin user (full access)
2. Test as teacher user (limited access)
3. Test as student user (no access)
4. Verify teacher profile access for own profile
5. Test logout and re-login functionality

**Expected Results**:
- Admin has full access to teacher management
- Teachers can view/edit their own profiles only
- Students cannot access teacher management
- Authentication is enforced on all endpoints
- Proper redirects occur for unauthorized access
- Session management works correctly
