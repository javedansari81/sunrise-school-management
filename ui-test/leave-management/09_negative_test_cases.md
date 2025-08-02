# Negative Test Cases

## Test Case 9.1: Invalid Form Submissions
**Objective**: Verify system handles invalid form submissions gracefully
**Preconditions**: Leave request form open
**Steps**:
1. Submit form with all fields empty
2. Submit form with invalid date ranges (end before start)
3. Submit form with negative total days
4. Submit form with extremely long text in reason field
5. Submit form with special characters in inappropriate fields
6. Submit form with SQL injection attempts

**Expected Results**:
- Form validation prevents submission of invalid data
- Clear error messages displayed for each validation failure
- No system crashes or unexpected behavior
- SQL injection attempts are blocked
- Form state preserved during validation errors
- User guided to correct invalid inputs

---

## Test Case 9.2: API Error Handling
**Objective**: Verify graceful handling of API errors and failures
**Preconditions**: Ability to simulate API errors
**Steps**:
1. Simulate 500 Internal Server Error during data loading
2. Simulate 404 Not Found for specific leave request
3. Simulate 401 Unauthorized during operation
4. Simulate network timeout during form submission
5. Simulate malformed JSON response
6. Simulate rate limiting (429 Too Many Requests)

**Expected Results**:
- Appropriate error messages displayed for each error type
- No application crashes or white screens
- User can retry operations after errors
- Loading states handled correctly during errors
- Error messages are user-friendly, not technical
- Application state remains consistent after errors

---

## Test Case 9.3: Authentication and Authorization Failures
**Objective**: Verify proper handling of authentication and authorization failures
**Preconditions**: Authentication system configured
**Steps**:
1. Access leave management with expired token
2. Attempt operations with insufficient permissions
3. Try to access admin features as non-admin user
4. Simulate session hijacking attempts
5. Test with malformed authentication tokens
6. Attempt CSRF attacks

**Expected Results**:
- Expired tokens trigger re-authentication
- Insufficient permissions show appropriate error messages
- Non-admin users cannot access admin features
- Security attacks are blocked
- User redirected to login when necessary
- No sensitive data exposed during auth failures

---

## Test Case 9.4: Database Connection Failures
**Objective**: Verify handling of database connectivity issues
**Preconditions**: Ability to simulate database issues
**Steps**:
1. Simulate database connection timeout
2. Simulate database server unavailable
3. Simulate database query failures
4. Simulate transaction rollback scenarios
5. Test during database maintenance windows

**Expected Results**:
- Database errors handled gracefully
- User informed of temporary unavailability
- No data corruption during failures
- Automatic retry mechanisms work (if implemented)
- Graceful degradation when possible
- System recovers when database is restored

---

## Test Case 9.5: File Upload Failures
**Objective**: Verify proper handling of file upload failures
**Preconditions**: File upload functionality available
**Steps**:
1. Upload file exceeding size limit
2. Upload file with unsupported format
3. Upload corrupted file
4. Simulate storage space full error
5. Upload file with malicious content
6. Interrupt upload process

**Expected Results**:
- File size limits enforced with clear error messages
- Unsupported formats rejected appropriately
- Corrupted files detected and rejected
- Storage errors handled gracefully
- Malicious files blocked by security measures
- Interrupted uploads cleaned up properly

---

## Test Case 9.6: Concurrent User Conflicts
**Objective**: Verify handling of concurrent user operations
**Preconditions**: Multiple users accessing same data
**Steps**:
1. Two users edit same leave request simultaneously
2. One user deletes request while another views it
3. Multiple users approve same request simultaneously
4. Simulate race conditions in data updates
5. Test optimistic locking scenarios

**Expected Results**:
- Concurrent edits handled with appropriate conflict resolution
- Deleted items show appropriate error when accessed
- Duplicate approvals prevented
- Race conditions don't cause data corruption
- Users informed of conflicts with clear messages
- Data integrity maintained during concurrent operations

---

## Test Case 9.7: Invalid URL and Route Handling
**Objective**: Verify proper handling of invalid URLs and routes
**Preconditions**: Application with routing configured
**Steps**:
1. Access non-existent route (/admin/invalid-page)
2. Access leave request with invalid ID
3. Manually modify URL parameters
4. Access routes without proper authentication
5. Test malformed URL parameters

**Expected Results**:
- 404 errors handled with user-friendly pages
- Invalid IDs show appropriate error messages
- URL manipulation doesn't break application
- Protected routes redirect to authentication
- Malformed parameters handled gracefully
- User can navigate back to valid pages

---

## Test Case 9.8: Browser Compatibility Issues
**Objective**: Verify handling of browser-specific issues
**Preconditions**: Different browsers and versions
**Steps**:
1. Test on unsupported browser versions
2. Test with JavaScript disabled
3. Test with cookies disabled
4. Test with local storage unavailable
5. Test with browser extensions that modify DOM

**Expected Results**:
- Graceful degradation on unsupported browsers
- Appropriate messaging when JavaScript required
- Cookie requirements clearly communicated
- Local storage failures handled gracefully
- Browser extensions don't break functionality
- Core functionality available across browsers

---

## Test Case 9.9: Performance Under Load
**Objective**: Verify system behavior under high load conditions
**Preconditions**: Ability to simulate high load
**Steps**:
1. Load page with thousands of leave requests
2. Perform rapid successive operations
3. Open multiple tabs with leave management
4. Simulate slow network conditions
5. Test with limited device memory

**Expected Results**:
- Large datasets handled with pagination/virtualization
- Rapid operations don't cause system instability
- Multiple tabs don't conflict or degrade performance
- Slow networks handled with appropriate timeouts
- Memory usage remains reasonable under load
- User experience degrades gracefully under stress

---

## Test Case 9.10: Data Validation Edge Cases
**Objective**: Verify handling of edge cases in data validation
**Preconditions**: Leave request form available
**Steps**:
1. Enter dates far in the future (year 2099)
2. Enter dates far in the past (year 1900)
3. Enter extremely long text strings
4. Enter Unicode characters and emojis
5. Enter HTML/script tags in text fields
6. Test with different locale date formats

**Expected Results**:
- Future dates handled according to business rules
- Past dates validated appropriately
- Long text strings truncated or rejected gracefully
- Unicode characters handled correctly
- HTML/script injection prevented
- Date formats parsed correctly regardless of locale

---

## Test Case 9.11: Session Management Failures
**Objective**: Verify proper handling of session management issues
**Preconditions**: Session management configured
**Steps**:
1. Simulate session timeout during form submission
2. Test with corrupted session data
3. Simulate session storage full
4. Test concurrent sessions from same user
5. Test session fixation attacks

**Expected Results**:
- Session timeouts handled gracefully with re-authentication
- Corrupted sessions cleared and new ones created
- Session storage issues handled appropriately
- Concurrent sessions managed correctly
- Session security attacks prevented
- User data protected during session issues

---

## Test Case 9.12: Configuration Data Failures
**Objective**: Verify handling of configuration data issues
**Preconditions**: Configuration system in place
**Steps**:
1. Simulate configuration endpoint unavailable
2. Test with malformed configuration data
3. Test with missing required configuration
4. Simulate configuration data corruption
5. Test with conflicting configuration values

**Expected Results**:
- Configuration failures don't prevent basic functionality
- Malformed data handled with fallback values
- Missing configuration detected and reported
- Data corruption handled gracefully
- Configuration conflicts resolved appropriately
- System remains functional with default configurations

---

## Test Case 9.13: Memory and Resource Leaks
**Objective**: Verify no memory leaks or resource issues
**Preconditions**: Browser developer tools available
**Steps**:
1. Monitor memory usage during extended use
2. Test rapid navigation between pages
3. Open and close dialogs repeatedly
4. Test with large datasets
5. Monitor for event listener leaks

**Expected Results**:
- Memory usage remains stable over time
- No memory leaks during navigation
- Dialog operations don't accumulate memory
- Large datasets don't cause memory issues
- Event listeners properly cleaned up
- Browser performance remains good

---

## Test Case 9.14: Cross-Site Scripting (XSS) Prevention
**Objective**: Verify protection against XSS attacks
**Preconditions**: Security testing tools available
**Steps**:
1. Attempt to inject script tags in form fields
2. Test with malicious URLs
3. Try to inject JavaScript in text areas
4. Test with encoded malicious scripts
5. Attempt DOM manipulation attacks

**Expected Results**:
- Script injection attempts blocked
- Malicious URLs sanitized or blocked
- Text areas properly escape user input
- Encoded scripts detected and prevented
- DOM manipulation attacks fail
- No script execution from user input

---

## Test Case 9.15: Data Integrity Failures
**Objective**: Verify handling of data integrity issues
**Preconditions**: Database with referential integrity
**Steps**:
1. Attempt to create leave request with non-existent user
2. Try to reference deleted leave types
3. Simulate foreign key constraint violations
4. Test with orphaned data records
5. Attempt to create circular references

**Expected Results**:
- Foreign key violations prevented with clear errors
- Deleted references handled gracefully
- Constraint violations don't crash system
- Orphaned data detected and handled
- Circular references prevented
- Data consistency maintained at all times
