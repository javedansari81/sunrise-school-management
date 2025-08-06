# Session Invalidation Testing Guide

This guide provides step-by-step instructions to test the session invalidation and authentication handling implementation.

## Prerequisites

1. Start the backend server: `cd sunrise-backend-fastapi && python main.py`
2. Start the frontend server: `cd sunrise-school-frontend && npm start`
3. Open browser developer console (F12)

## Test Scenarios

### 1. Test Session Expiration Detection

Open browser console and run:
```javascript
// Test session expiration detection
window.sessionTestUtils.testSessionExpiration();
```

Expected output:
- ✅ Expired token detected: true
- ✅ Valid token detected: true

### 2. Test Session Invalidation Flow

```javascript
// Test complete session invalidation flow
window.sessionTestUtils.testSessionInvalidationFlow();
```

Expected output:
- ✅ Session validation with expired token: PASS
- ✅ Session validation trigger: PASS

### 3. Simulate Session Expiration

```javascript
// Simulate session expiration (will trigger login popup)
window.sessionTestUtils.simulateSessionExpiration();
```

Expected behavior:
- Login popup should appear automatically
- Warning message should show: "Your session has expired. Please log in again to continue."

### 4. Test Token Expiration Time Calculation

```javascript
// Test token expiration time calculation
window.sessionTestUtils.testTokenExpirationTime();
```

Expected output:
- ✅ Token expiration time: [Date object]
- ✅ Time until expiration: [number] minutes

### 5. Run All Tests

```javascript
// Run all session tests
window.sessionTestUtils.runAllSessionTests();
```

## Manual Testing Scenarios

### Scenario 1: Expired Token on Protected Route Access

1. Log in to the application
2. Open browser console and run:
   ```javascript
   // Set an expired token
   localStorage.setItem('authToken', window.sessionTestUtils.createExpiredToken());
   ```
3. Try to access a protected route (e.g., `/admin/dashboard`)
4. **Expected**: Redirected to home page with login popup showing session expiration message

### Scenario 2: Missing Token on Protected Route Access

1. Clear localStorage:
   ```javascript
   localStorage.removeItem('authToken');
   localStorage.removeItem('userRole');
   ```
2. Try to access a protected route
3. **Expected**: Redirected to home page with login popup showing authentication required message

### Scenario 3: API Call with Expired Token

1. Log in to the application
2. Set an expired token:
   ```javascript
   localStorage.setItem('authToken', window.sessionTestUtils.createExpiredToken());
   ```
3. Make an API call (e.g., try to load admin dashboard data)
4. **Expected**: Session invalidation triggered, redirected to home with login popup

### Scenario 4: Session Monitoring

1. Log in to the application
2. Check session monitoring is active:
   ```javascript
   // Session service should be monitoring
   console.log('Session valid:', sessionService.isSessionValid());
   ```
3. Wait for session monitoring to detect expiration (or simulate it)
4. **Expected**: Automatic logout and login popup when session expires

## Verification Checklist

- [ ] Expired tokens are properly detected
- [ ] Session validation works correctly
- [ ] Protected routes redirect to home when session is invalid
- [ ] Login popup appears automatically on session expiration
- [ ] Appropriate warning messages are displayed
- [ ] Session monitoring starts after login
- [ ] Session monitoring stops after logout
- [ ] API calls handle 401 errors properly
- [ ] Session data is cleared on invalidation
- [ ] User experience is smooth during session transitions

## Expected User Experience

1. **Session Expiration**: User sees warning message explaining session expired
2. **Missing Authentication**: User sees message asking to log in
3. **Smooth Transition**: No jarring redirects or error pages
4. **Clear Feedback**: User understands why they need to log in again
5. **Easy Recovery**: Login popup is immediately available

## Troubleshooting

### Login Popup Not Appearing
- Check browser console for errors
- Verify AuthContext is properly integrated
- Check if showLoginPopup state is being set

### Session Not Being Detected as Expired
- Verify token format in localStorage
- Check sessionService.isTokenExpired() function
- Ensure JWT payload has correct exp field

### API Calls Not Triggering Session Invalidation
- Check axios response interceptor
- Verify 401 responses from backend
- Check sessionService callbacks are set

### Protected Routes Not Redirecting
- Verify ProtectedRoute component integration
- Check isAuthenticated logic
- Ensure session validation is called

## Notes

- Test utilities are only available in development mode
- Session monitoring runs every minute by default
- JWT tokens are validated client-side for expiration
- Backend still validates tokens for security
- Session data is cleared from localStorage on invalidation
