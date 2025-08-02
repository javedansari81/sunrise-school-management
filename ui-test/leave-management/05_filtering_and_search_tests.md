# Filtering and Search Test Cases

## Test Case 5.1: Applicant Type Filter
**Objective**: Verify filtering by applicant type works correctly
**Preconditions**: Leave requests from both students and teachers exist
**Steps**:
1. Navigate to "All Requests" tab
2. Select "Students" from applicant type filter
3. Verify only student leave requests are displayed
4. Select "Teachers" from applicant type filter
5. Verify only teacher leave requests are displayed
6. Select "All" to clear filter

**Expected Results**:
- Filter dropdown populated with options (All, Students, Teachers)
- Student filter shows only student requests
- Teacher filter shows only teacher requests
- "All" option shows all requests
- Request count updates correctly with filter

**Test Data**: Leave requests from both students and teachers

---

## Test Case 5.2: Leave Status Filter
**Objective**: Verify filtering by leave status works correctly
**Preconditions**: Leave requests with different statuses exist
**Steps**:
1. Select "Pending" from leave status filter
2. Verify only pending requests are displayed
3. Select "Approved" from leave status filter
4. Verify only approved requests are displayed
5. Select "Rejected" from leave status filter
6. Verify only rejected requests are displayed
7. Select "All" to clear filter

**Expected Results**:
- Status filter populated from configuration data
- Each status filter shows correct requests
- Status colors match filter selection
- Request count updates with each filter
- Filter state maintained during page navigation

**Test Data**: Leave requests with various statuses

---

## Test Case 5.3: Leave Type Filter
**Objective**: Verify filtering by leave type works correctly
**Preconditions**: Leave requests of different types exist
**Steps**:
1. Select "Sick Leave" from leave type filter
2. Verify only sick leave requests are displayed
3. Select "Casual Leave" from leave type filter
4. Verify only casual leave requests are displayed
5. Test other leave types
6. Select "All" to clear filter

**Expected Results**:
- Leave type filter populated from configuration
- Each type filter shows correct requests
- Leave type names display correctly
- Filter works for all available leave types
- Clear filter functionality works

**Test Data**: Leave requests of various types (sick, casual, emergency, etc.)

---

## Test Case 5.4: Date Range Filter
**Objective**: Verify filtering by date range works correctly
**Preconditions**: Leave requests with different date ranges exist
**Steps**:
1. Set "From Date" to a specific date
2. Verify requests starting from that date are shown
3. Set "To Date" to limit the range
4. Verify requests within date range are shown
5. Clear date filters
6. Verify all requests are shown again

**Expected Results**:
- Date picker components work correctly
- From date filter works independently
- To date filter works independently
- Combined date range filter works correctly
- Clear date filter functionality works
- Invalid date ranges handled gracefully

**Test Data**: Leave requests spanning different date ranges

---

## Test Case 5.5: Class Name Filter (for Students)
**Objective**: Verify filtering by class name works correctly
**Preconditions**: Student leave requests from different classes exist
**Steps**:
1. Select specific class from class filter
2. Verify only requests from that class are shown
3. Test multiple class selections
4. Clear class filter
5. Verify all student requests are shown

**Expected Results**:
- Class filter populated with available classes
- Class filter shows correct student requests
- Multiple class selection works (if implemented)
- Class names display correctly
- Filter integrates with other filters

**Test Data**: Student leave requests from various classes

---

## Test Case 5.6: Department Filter (for Teachers)
**Objective**: Verify filtering by department works correctly
**Preconditions**: Teacher leave requests from different departments exist
**Steps**:
1. Select specific department from department filter
2. Verify only requests from that department are shown
3. Test multiple department selections
4. Clear department filter
5. Verify all teacher requests are shown

**Expected Results**:
- Department filter populated with available departments
- Department filter shows correct teacher requests
- Department names display correctly
- Filter works with teacher applicant type
- Clear functionality works correctly

**Test Data**: Teacher leave requests from various departments

---

## Test Case 5.7: Combined Filters
**Objective**: Verify multiple filters work together correctly
**Preconditions**: Diverse leave request data available
**Steps**:
1. Apply applicant type filter (Students)
2. Apply leave status filter (Pending)
3. Apply leave type filter (Sick Leave)
4. Verify results match all filter criteria
5. Add date range filter
6. Verify combined results are correct

**Expected Results**:
- Multiple filters work simultaneously
- Results match all applied filter criteria
- Filter combinations reduce result set appropriately
- No conflicts between different filters
- Performance remains good with multiple filters

**Test Data**: Comprehensive leave request dataset

---

## Test Case 5.8: Filter State Persistence
**Objective**: Verify filter state is maintained during navigation
**Preconditions**: Filters applied to leave request list
**Steps**:
1. Apply multiple filters
2. Navigate to different tab
3. Return to filtered tab
4. Verify filters are still applied
5. Refresh page
6. Verify filter state handling

**Expected Results**:
- Filter state maintained during tab navigation
- Applied filters persist appropriately
- Page refresh behavior is consistent
- URL parameters reflect filter state (if implemented)
- Filter state cleared when appropriate

---

## Test Case 5.9: Filter Performance with Large Dataset
**Objective**: Verify filter performance with large number of requests
**Preconditions**: Large dataset of leave requests (100+ records)
**Steps**:
1. Load page with large dataset
2. Apply various filters
3. Measure response time
4. Test filter combinations
5. Verify UI responsiveness

**Expected Results**:
- Filters respond quickly even with large dataset
- UI remains responsive during filtering
- No significant delays in filter application
- Pagination works correctly with filters
- Memory usage remains reasonable

**Test Data**: Large dataset of leave requests

---

## Test Case 5.10: Search Functionality
**Objective**: Verify search functionality works correctly (if implemented)
**Preconditions**: Leave requests with searchable content
**Steps**:
1. Enter applicant name in search box
2. Verify matching requests are displayed
3. Search by leave reason keywords
4. Verify relevant results shown
5. Test partial matches
6. Clear search and verify all results return

**Expected Results**:
- Search box accepts text input
- Search results match query criteria
- Partial matches work correctly
- Search is case-insensitive
- Clear search functionality works
- Search integrates with filters

**Test Data**: Leave requests with various applicant names and reasons

---

## Test Case 5.11: Filter Reset Functionality
**Objective**: Verify filter reset/clear functionality works correctly
**Preconditions**: Multiple filters applied
**Steps**:
1. Apply multiple different filters
2. Click "Clear Filters" or "Reset" button
3. Verify all filters are cleared
4. Verify all requests are displayed
5. Test individual filter clearing

**Expected Results**:
- Clear all filters button works correctly
- All filters reset to default state
- Full dataset displayed after reset
- Individual filter clearing works
- Reset button available when filters applied

---

## Test Case 5.12: Filter Validation
**Objective**: Verify filter input validation works correctly
**Preconditions**: Filter components available
**Steps**:
1. Enter invalid date range (end before start)
2. Verify validation error
3. Test invalid search characters
4. Verify input sanitization
5. Test filter with no matching results

**Expected Results**:
- Invalid date ranges prevented or warned
- Input validation works correctly
- No matching results handled gracefully
- Error messages are clear and helpful
- Invalid inputs don't break functionality

---

## Test Case 5.13: Mobile Filter Interface
**Objective**: Verify filter interface works on mobile devices
**Preconditions**: Mobile device or responsive design testing
**Steps**:
1. Access filters on mobile device
2. Test dropdown interactions
3. Test date picker on mobile
4. Verify filter application works
5. Test filter clearing on mobile

**Expected Results**:
- Filter interface adapts to mobile screen
- Touch interactions work correctly
- Dropdowns are accessible on mobile
- Date pickers work on mobile browsers
- All filter functionality available on mobile

---

## Test Case 5.14: Filter Accessibility
**Objective**: Verify filter components are accessible
**Preconditions**: Screen reader or accessibility testing tools
**Steps**:
1. Navigate filters using keyboard only
2. Test screen reader compatibility
3. Verify ARIA labels are present
4. Test focus management
5. Verify color contrast for filter states

**Expected Results**:
- All filters accessible via keyboard
- Screen readers can announce filter options
- Proper ARIA labels and roles present
- Focus management works correctly
- Sufficient color contrast for visibility

---

## Test Case 5.15: Filter Error Handling
**Objective**: Verify error handling in filter operations
**Preconditions**: Ability to simulate filter errors
**Steps**:
1. Simulate server error during filter operation
2. Verify error handling
3. Test network timeout during filtering
4. Verify recovery behavior
5. Test filter with corrupted data

**Expected Results**:
- Graceful error handling during filter operations
- Clear error messages displayed
- Filter state preserved during errors
- Recovery mechanism available
- No data corruption during filter errors
