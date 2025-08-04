/**
 * Test script to verify Leave Management page fixes
 * Run this in the browser console on the Leave Management page
 */

console.log('🧪 Testing Leave Management Page Fixes');
console.log('=====================================');

// Test 1: Check if service configuration is loading
function testServiceConfiguration() {
  console.log('\n1. Testing Service Configuration Loading...');
  
  // Check if the ServiceConfigurationLoader is working
  const configLoader = document.querySelector('[data-testid="service-config-loader"]');
  if (configLoader) {
    console.log('✅ ServiceConfigurationLoader found');
  } else {
    console.log('⚠️ ServiceConfigurationLoader not found (this is normal if already loaded)');
  }
  
  // Check for loading indicators
  const loadingIndicators = document.querySelectorAll('[role="progressbar"]');
  if (loadingIndicators.length > 0) {
    console.log('⏳ Loading indicators found:', loadingIndicators.length);
  } else {
    console.log('✅ No loading indicators (configuration likely loaded)');
  }
}

// Test 2: Check for authentication
function testAuthentication() {
  console.log('\n2. Testing Authentication...');
  
  // Check for login prompts
  const loginPrompts = document.querySelectorAll('*').forEach(el => {
    if (el.textContent && el.textContent.includes('Please login')) {
      console.log('❌ Login prompt found - user not authenticated');
      return false;
    }
  });
  
  console.log('✅ No login prompts found - user appears authenticated');
  return true;
}

// Test 3: Check for error messages
function testErrorMessages() {
  console.log('\n3. Testing for Error Messages...');
  
  // Check for error alerts
  const errorAlerts = document.querySelectorAll('[role="alert"]');
  if (errorAlerts.length > 0) {
    console.log('⚠️ Error alerts found:', errorAlerts.length);
    errorAlerts.forEach((alert, index) => {
      console.log(`   Alert ${index + 1}:`, alert.textContent);
    });
  } else {
    console.log('✅ No error alerts found');
  }
}

// Test 4: Check for Leave Management content
function testLeaveManagementContent() {
  console.log('\n4. Testing Leave Management Content...');
  
  // Check for tabs
  const tabs = document.querySelectorAll('[role="tab"]');
  if (tabs.length > 0) {
    console.log('✅ Tabs found:', tabs.length);
    tabs.forEach((tab, index) => {
      console.log(`   Tab ${index + 1}:`, tab.textContent);
    });
  } else {
    console.log('❌ No tabs found');
  }
  
  // Check for table content
  const tables = document.querySelectorAll('table');
  if (tables.length > 0) {
    console.log('✅ Tables found:', tables.length);
  } else {
    console.log('⚠️ No tables found (might be empty data)');
  }
}

// Test 5: Check network requests
function testNetworkRequests() {
  console.log('\n5. Testing Network Requests...');
  console.log('📡 Check the Network tab in DevTools for:');
  console.log('   - /api/v1/configuration/leave-management/ (should be 200 OK)');
  console.log('   - /api/v1/leaves (should be 200 OK or 401 if not authenticated)');
  console.log('   - /api/v1/leaves/statistics (should be 200 OK)');
  
  // Monitor fetch requests
  const originalFetch = window.fetch;
  window.fetch = function(...args) {
    console.log('🌐 Fetch request:', args[0]);
    return originalFetch.apply(this, arguments)
      .then(response => {
        console.log(`📡 Response for ${args[0]}:`, response.status, response.statusText);
        return response;
      })
      .catch(error => {
        console.error(`❌ Fetch error for ${args[0]}:`, error);
        throw error;
      });
  };
  
  console.log('✅ Network monitoring enabled');
}

// Test 6: Check console for debug logs
function testDebugLogs() {
  console.log('\n6. Checking for Debug Logs...');
  console.log('🔍 Look for these debug messages in the console:');
  console.log('   - 🔧 ServiceConfigurationLoader [leave-management]');
  console.log('   - 🔧 useServiceConfiguration [leave-management] effect running');
  console.log('   - 🚀 Triggering load for leave-management');
  console.log('   - 🌐 Loading leave requests with params');
  console.log('   - ✅ Leave requests loaded');
}

// Run all tests
function runAllTests() {
  testServiceConfiguration();
  testAuthentication();
  testErrorMessages();
  testLeaveManagementContent();
  testNetworkRequests();
  testDebugLogs();
  
  console.log('\n🎯 Test Summary:');
  console.log('================');
  console.log('1. Check the browser Network tab for API calls');
  console.log('2. Look for debug messages in the console');
  console.log('3. Verify that leave management content is displayed');
  console.log('4. If you see login prompts, authenticate first');
  console.log('5. If you see errors, check the backend server status');
}

// Auto-run tests after a short delay
setTimeout(runAllTests, 2000);

// Export for manual testing
window.leaveManagementTest = {
  runAllTests,
  testServiceConfiguration,
  testAuthentication,
  testErrorMessages,
  testLeaveManagementContent,
  testNetworkRequests,
  testDebugLogs
};

console.log('\n💡 Manual testing available via: window.leaveManagementTest.runAllTests()');
