/**
 * Test utilities for session invalidation functionality
 * These functions help test the session expiration and authentication handling
 */

import { sessionService } from '../services/sessionService';

/**
 * Create an expired JWT token for testing
 * This creates a token that expired 1 hour ago
 */
export const createExpiredToken = (): string => {
  const header = {
    alg: 'HS256',
    typ: 'JWT'
  };

  const payload = {
    sub: '123',
    exp: Math.floor(Date.now() / 1000) - 3600, // Expired 1 hour ago
    iat: Math.floor(Date.now() / 1000) - 7200  // Issued 2 hours ago
  };

  // Create a fake JWT token (base64 encoded header and payload)
  const encodedHeader = btoa(JSON.stringify(header));
  const encodedPayload = btoa(JSON.stringify(payload));
  const fakeSignature = 'fake-signature-for-testing';

  return `${encodedHeader}.${encodedPayload}.${fakeSignature}`;
};

/**
 * Create a valid JWT token for testing
 * This creates a token that expires in 1 hour
 */
export const createValidToken = (): string => {
  const header = {
    alg: 'HS256',
    typ: 'JWT'
  };

  const payload = {
    sub: '123',
    exp: Math.floor(Date.now() / 1000) + 3600, // Expires in 1 hour
    iat: Math.floor(Date.now() / 1000)         // Issued now
  };

  // Create a fake JWT token (base64 encoded header and payload)
  const encodedHeader = btoa(JSON.stringify(header));
  const encodedPayload = btoa(JSON.stringify(payload));
  const fakeSignature = 'fake-signature-for-testing';

  return `${encodedHeader}.${encodedPayload}.${fakeSignature}`;
};

/**
 * Test session expiration detection
 */
export const testSessionExpiration = () => {
  console.log('🧪 Testing Session Expiration Detection');
  
  // Test with expired token
  const expiredToken = createExpiredToken();
  const isExpired = sessionService.isTokenExpired(expiredToken);
  console.log(`✅ Expired token detected: ${isExpired}`);
  
  // Test with valid token
  const validToken = createValidToken();
  const isValid = !sessionService.isTokenExpired(validToken);
  console.log(`✅ Valid token detected: ${isValid}`);
  
  return { expiredTokenTest: isExpired, validTokenTest: isValid };
};

/**
 * Test session invalidation flow
 */
export const testSessionInvalidationFlow = () => {
  console.log('🧪 Testing Session Invalidation Flow');
  
  // Store original token
  const originalToken = localStorage.getItem('authToken');
  
  try {
    // Set an expired token
    const expiredToken = createExpiredToken();
    localStorage.setItem('authToken', expiredToken);
    
    // Test session validation
    const isSessionValid = sessionService.isSessionValid();
    console.log(`✅ Session validation with expired token: ${!isSessionValid ? 'PASS' : 'FAIL'}`);
    
    // Test session validation trigger
    const validationResult = sessionService.validateCurrentSession();
    console.log(`✅ Session validation trigger: ${!validationResult ? 'PASS' : 'FAIL'}`);
    
    return {
      sessionValidation: !isSessionValid,
      validationTrigger: !validationResult
    };
  } finally {
    // Restore original token
    if (originalToken) {
      localStorage.setItem('authToken', originalToken);
    } else {
      localStorage.removeItem('authToken');
    }
  }
};

/**
 * Simulate session expiration for testing
 * This will set an expired token and trigger the session validation
 */
export const simulateSessionExpiration = () => {
  console.log('🧪 Simulating Session Expiration');
  
  // Set an expired token
  const expiredToken = createExpiredToken();
  localStorage.setItem('authToken', expiredToken);
  
  // Trigger session validation
  sessionService.validateCurrentSession();
  
  console.log('✅ Session expiration simulated - check for login popup');
};

/**
 * Test token expiration time calculation
 */
export const testTokenExpirationTime = () => {
  console.log('🧪 Testing Token Expiration Time Calculation');
  
  const validToken = createValidToken();
  const expiration = sessionService.getTokenExpiration(validToken);
  const timeUntilExpiration = sessionService.getTimeUntilExpiration();
  
  console.log(`✅ Token expiration time: ${expiration}`);
  console.log(`✅ Time until expiration: ${timeUntilExpiration} minutes`);
  
  return { expiration, timeUntilExpiration };
};

/**
 * Run all session invalidation tests
 */
export const runAllSessionTests = () => {
  console.log('🧪 Running All Session Invalidation Tests');
  console.log('==========================================');
  
  const results = {
    expirationDetection: testSessionExpiration(),
    invalidationFlow: testSessionInvalidationFlow(),
    expirationTime: testTokenExpirationTime()
  };
  
  console.log('==========================================');
  console.log('🧪 All Tests Completed');
  console.log('Results:', results);
  
  return results;
};

// Make functions available globally for browser console testing
if (typeof window !== 'undefined') {
  (window as any).sessionTestUtils = {
    createExpiredToken,
    createValidToken,
    testSessionExpiration,
    testSessionInvalidationFlow,
    simulateSessionExpiration,
    testTokenExpirationTime,
    runAllSessionTests
  };
  
  console.log('🧪 Session test utilities loaded. Use window.sessionTestUtils to access test functions.');
}
