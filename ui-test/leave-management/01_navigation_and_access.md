# Navigation and Access Test Cases

## Test Case 1.1: Admin Route Access
**Objective**: Verify admin users can access the Leave Management system
**Preconditions**: User logged in with ADMIN role
**Steps**:
1. Navigate to `/admin/leaves`
2. Verify page loads successfully
3. Check page title displays "Leave Management System"
4. Verify admin layout is rendered correctly

**Expected Results**:
- Page loads without errors
- Leave Management System component is displayed
- Admin navigation tabs are visible
- User has access to all leave management features

**Test Data**: Admin user credentials

---

## Test Case 1.2: Non-Admin Route Access
**Objective**: Verify non-admin users cannot access admin leave management
**Preconditions**: User logged in with TEACHER or STUDENT role
**Steps**:
1. Attempt to navigate to `/admin/leaves`
2. Verify access is denied or redirected

**Expected Results**:
- User is redirected to appropriate page
- Error message displayed if applicable
- No access to admin leave management features

**Test Data**: Teacher/Student user credentials

---

## Test Case 1.3: Unauthenticated Access
**Objective**: Verify unauthenticated users cannot access leave management
**Preconditions**: No user logged in
**Steps**:
1. Attempt to navigate to `/admin/leaves`
2. Verify redirect to login page

**Expected Results**:
- User redirected to login page
- No access to leave management system
- Appropriate authentication prompt displayed

---

## Test Case 1.4: Admin Navigation Tabs
**Objective**: Verify admin navigation tabs work correctly
**Preconditions**: Admin user logged in and on leave management page
**Steps**:
1. Click on "Dashboard" tab
2. Verify navigation to `/admin/dashboard`
3. Click on "Fees Management" tab
4. Verify navigation to `/admin/fees`
5. Click on "Leave Management" tab
6. Verify navigation to `/admin/leaves`
7. Click on "Expense Management" tab
8. Verify navigation to `/admin/expenses`
9. Click on "Student Profiles" tab
10. Verify navigation to `/admin/students`

**Expected Results**:
- All navigation tabs work correctly
- Active tab is highlighted appropriately
- Page content changes correctly for each tab
- URL updates correctly

---

## Test Case 1.5: Leave Management Tab Navigation
**Objective**: Verify internal tab navigation within leave management
**Preconditions**: Admin user on leave management page
**Steps**:
1. Verify "All Requests" tab is active by default
2. Click on "Pending Approval" tab
3. Verify tab content changes
4. Click on "My Requests" tab
5. Verify tab content changes
6. Click on "Statistics" tab
7. Verify tab content changes
8. Return to "All Requests" tab

**Expected Results**:
- Tab switching works smoothly
- Content updates correctly for each tab
- Active tab is visually highlighted
- No JavaScript errors in console

---

## Test Case 1.6: Browser Back/Forward Navigation
**Objective**: Verify browser navigation works correctly
**Preconditions**: Admin user on leave management page
**Steps**:
1. Navigate to different admin tabs
2. Use browser back button
3. Verify correct page is displayed
4. Use browser forward button
5. Verify correct page is displayed

**Expected Results**:
- Browser back/forward buttons work correctly
- Page state is maintained appropriately
- No broken navigation states

---

## Test Case 1.7: Direct URL Access
**Objective**: Verify direct URL access to leave management works
**Preconditions**: Admin user logged in
**Steps**:
1. Enter `/admin/leaves` directly in browser address bar
2. Press Enter
3. Verify page loads correctly

**Expected Results**:
- Page loads successfully
- All components render correctly
- No authentication issues

---

## Test Case 1.8: Page Refresh Behavior
**Objective**: Verify page refresh maintains functionality
**Preconditions**: Admin user on leave management page with data loaded
**Steps**:
1. Load leave management page
2. Wait for data to load
3. Refresh the page (F5 or Ctrl+R)
4. Verify page reloads correctly

**Expected Results**:
- Page refreshes successfully
- Data reloads from API
- User remains authenticated
- All functionality works after refresh

---

## Test Case 1.9: Session Timeout Handling
**Objective**: Verify behavior when user session expires
**Preconditions**: Admin user on leave management page
**Steps**:
1. Simulate session timeout (if possible)
2. Attempt to perform any action
3. Verify appropriate handling

**Expected Results**:
- User is redirected to login page
- Appropriate session timeout message displayed
- No data corruption or errors

---

## Test Case 1.10: Multiple Tab Behavior
**Objective**: Verify application works correctly with multiple browser tabs
**Preconditions**: Admin user logged in
**Steps**:
1. Open leave management in first tab
2. Open leave management in second tab
3. Perform actions in both tabs
4. Verify data consistency

**Expected Results**:
- Both tabs work independently
- Data updates are reflected appropriately
- No conflicts between tabs
- Session management works correctly
