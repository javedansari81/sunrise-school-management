# Leave Approval Workflow Test Cases

## Test Case 4.1: Approve Leave Request
**Objective**: Verify admin can approve pending leave requests
**Preconditions**: Pending leave requests exist in database
**Steps**:
1. Navigate to "Pending Approval" tab
2. Click "Approve" button on a pending request
3. Add review comments (optional)
4. Confirm approval
5. Verify status changes to "Approved"

**Expected Results**:
- Approve button available for pending requests
- Approval dialog opens correctly
- Review comments field available
- Status updates to "Approved" immediately
- Success message displayed
- Request moves out of pending list

**Test Data**: Pending leave requests

---

## Test Case 4.2: Reject Leave Request
**Objective**: Verify admin can reject pending leave requests
**Preconditions**: Pending leave requests exist in database
**Steps**:
1. Navigate to "Pending Approval" tab
2. Click "Reject" button on a pending request
3. Add mandatory review comments explaining rejection
4. Confirm rejection
5. Verify status changes to "Rejected"

**Expected Results**:
- Reject button available for pending requests
- Rejection dialog opens correctly
- Review comments required for rejection
- Status updates to "Rejected" immediately
- Success message displayed
- Request moves out of pending list

---

## Test Case 4.3: Approval with Review Comments
**Objective**: Verify review comments functionality during approval
**Preconditions**: Pending leave request available
**Steps**:
1. Start approval process
2. Enter detailed review comments
3. Submit approval
4. View approved request details
5. Verify comments are saved and displayed

**Expected Results**:
- Review comments field accepts text input
- Comments saved with approval
- Comments visible in request details
- Reviewer name recorded correctly
- Approval timestamp recorded

---

## Test Case 4.4: Bulk Approval Operations
**Objective**: Verify bulk approval of multiple requests (if implemented)
**Preconditions**: Multiple pending leave requests
**Steps**:
1. Select multiple pending requests using checkboxes
2. Click "Bulk Approve" button
3. Add common review comments
4. Confirm bulk approval
5. Verify all selected requests are approved

**Expected Results**:
- Multiple selection works correctly
- Bulk approve option available
- All selected requests updated simultaneously
- Common comments applied to all
- Success message indicates number of approvals

---

## Test Case 4.5: Approval Restrictions - Already Processed
**Objective**: Verify cannot approve already processed requests
**Preconditions**: Approved and rejected leave requests exist
**Steps**:
1. View approved leave request
2. Verify no approve/reject buttons available
3. View rejected leave request
4. Verify no approve/reject buttons available

**Expected Results**:
- Approve/Reject buttons not visible for processed requests
- Clear indication of current status
- No ability to change final statuses
- Appropriate status colors displayed

---

## Test Case 4.6: Approval Workflow - Teacher Leave with Substitute
**Objective**: Verify approval workflow for teacher leaves requiring substitutes
**Preconditions**: Teacher leave request with substitute arrangement
**Steps**:
1. Review teacher leave request
2. Verify substitute teacher information displayed
3. Check substitute arrangement status
4. Approve request
5. Verify substitute information preserved

**Expected Results**:
- Substitute teacher details visible during review
- Substitute arrangement status clear
- Approval process considers substitute availability
- All substitute information maintained after approval

---

## Test Case 4.7: Approval Workflow - Medical Certificate Verification
**Objective**: Verify approval workflow for leaves requiring medical certificates
**Preconditions**: Sick leave request with medical certificate
**Steps**:
1. Review sick leave request
2. Verify medical certificate link/attachment visible
3. Check certificate details
4. Approve request based on certificate
5. Verify certificate information maintained

**Expected Results**:
- Medical certificate clearly visible during review
- Certificate link/file accessible
- Approval decision can consider certificate
- Certificate information preserved after approval

---

## Test Case 4.8: Approval Notifications
**Objective**: Verify notifications are sent after approval/rejection
**Preconditions**: Leave request with notification settings
**Steps**:
1. Approve a leave request
2. Check if notification is sent to applicant
3. Reject a leave request
4. Check if notification is sent to applicant
5. Verify notification content

**Expected Results**:
- Notifications sent automatically after approval/rejection
- Notification content includes relevant details
- Applicant receives timely notification
- Notification includes review comments if provided

---

## Test Case 4.9: Approval Authority Validation
**Objective**: Verify approval authority based on leave type and duration
**Preconditions**: Different leave types with varying approval requirements
**Steps**:
1. Review short-duration casual leave
2. Review long-duration medical leave
3. Verify appropriate approval authority indicated
4. Test approval by authorized user
5. Test approval restrictions for unauthorized users

**Expected Results**:
- Approval authority clearly indicated
- Different leave types show appropriate approvers
- Long-duration leaves may require higher authority
- Unauthorized users cannot approve certain requests

---

## Test Case 4.10: Approval Deadline Management
**Objective**: Verify handling of approval deadlines and urgent requests
**Preconditions**: Leave requests with different start dates
**Steps**:
1. Review leave request starting today
2. Verify urgent priority indication
3. Review leave request starting next week
4. Verify normal priority indication
5. Test priority-based sorting

**Expected Results**:
- Urgent requests clearly marked
- Priority indicators work correctly
- Sorting by urgency available
- Deadline information visible
- Overdue requests highlighted

---

## Test Case 4.11: Approval History Tracking
**Objective**: Verify approval history is properly tracked and displayed
**Preconditions**: Leave requests with approval history
**Steps**:
1. View approved leave request details
2. Check approval history section
3. Verify reviewer information displayed
4. Check approval timestamp
5. Verify review comments visible

**Expected Results**:
- Complete approval history visible
- Reviewer name and role displayed
- Accurate timestamps shown
- Review comments preserved
- Audit trail maintained

---

## Test Case 4.12: Conditional Approval
**Objective**: Verify conditional approval functionality (if implemented)
**Preconditions**: Leave request that may require conditions
**Steps**:
1. Start approval process
2. Add conditional approval comments
3. Set conditions for approval
4. Submit conditional approval
5. Verify conditional status

**Expected Results**:
- Conditional approval option available
- Conditions clearly specified
- Conditional status distinct from full approval
- Applicant notified of conditions
- Follow-up mechanism available

---

## Test Case 4.13: Approval Workflow - Emergency Leaves
**Objective**: Verify special handling for emergency leave approvals
**Preconditions**: Emergency leave requests in system
**Steps**:
1. Review emergency leave request
2. Verify expedited approval process
3. Check emergency indicators
4. Process emergency approval
5. Verify special handling

**Expected Results**:
- Emergency leaves clearly marked
- Expedited approval process available
- Special priority in approval queue
- Faster notification process
- Emergency contact information visible

---

## Test Case 4.14: Approval Workflow - Retroactive Requests
**Objective**: Verify handling of retroactive leave requests
**Preconditions**: Leave requests with past dates
**Steps**:
1. Review leave request with past start date
2. Verify retroactive indicators
3. Check special approval requirements
4. Process retroactive approval
5. Verify special handling

**Expected Results**:
- Retroactive requests clearly identified
- Special approval process for past dates
- Additional justification requirements
- Appropriate warnings displayed
- Audit trail for retroactive approvals

---

## Test Case 4.15: Approval Error Handling
**Objective**: Verify error handling during approval process
**Preconditions**: Ability to simulate approval errors
**Steps**:
1. Start approval process
2. Simulate server error during approval
3. Verify error handling
4. Retry approval process
5. Verify successful completion

**Expected Results**:
- Graceful error handling during approval
- Clear error messages displayed
- Retry mechanism available
- No partial approvals created
- Data consistency maintained
