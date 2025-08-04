# Frontend Tests

This directory contains all frontend tests for the Sunrise School Management System React application, including component tests, context tests, and feature-specific testing documentation.

## 📁 Directory Structure

```
tests/frontend/
├── contexts-tests/        # React context testing
│   └── AuthContext.test.tsx      # Authentication context tests
├── tests/                 # Component and integration tests
│   └── ExpenseManagement.test.tsx # Expense management component tests
├── leave-management/      # Leave management feature test documentation
│   ├── 01_navigation_and_access.md
│   ├── 02_data_loading_tests.md
│   ├── 03_leave_request_management.md
│   ├── 04_approval_workflow_tests.md
│   ├── 05_filtering_and_search_tests.md
│   ├── 06_ui_component_tests.md
│   ├── 07_responsive_design_tests.md
│   ├── 08_integration_tests.md
│   ├── 09_negative_test_cases.md
│   ├── 10_test_execution_checklist.md
│   └── README.md
├── App.test.tsx           # Main application tests
├── test-config-loading.js # Configuration loading tests
└── README.md              # This file
```

## 🚀 Running Frontend Tests

### Run All Tests
```bash
cd sunrise-school-frontend
npm test
```

### Run Tests in Watch Mode
```bash
npm test -- --watch
```

### Run Tests with Coverage
```bash
npm test -- --coverage --watchAll=false
```

### Run Specific Test Files
```bash
# Authentication context tests
npm test -- --testPathPattern=AuthContext

# Expense management tests
npm test -- --testPathPattern=ExpenseManagement

# Main app tests
npm test -- --testPathPattern=App.test
```

## 🧪 Test Categories

### Component Tests (`tests/`)
**Individual React component testing:**

- **ExpenseManagement.test.tsx** - Expense management component testing
  - Component rendering and props
  - User interaction handling
  - State management validation
  - API integration testing
  - Error handling and edge cases

### Context Tests (`contexts-tests/`)
**React context and state management testing:**

- **AuthContext.test.tsx** - Authentication context testing
  - Login/logout functionality
  - Token management
  - User state persistence
  - Authentication flow validation
  - Error handling for auth failures

### Feature Documentation (`leave-management/`)
**Comprehensive feature testing documentation:**

- **Navigation and Access** - Page routing and access control
- **Data Loading** - API data fetching and loading states
- **Request Management** - Leave request CRUD operations
- **Approval Workflow** - Leave approval and rejection processes
- **Filtering and Search** - Data filtering and search functionality
- **UI Components** - Component behavior and interaction
- **Responsive Design** - Mobile and desktop compatibility
- **Integration Tests** - End-to-end workflow testing
- **Negative Test Cases** - Error scenarios and edge cases
- **Execution Checklist** - Complete testing checklist

## 🔧 Test Configuration

### Jest Configuration
Tests use Jest with React Testing Library:
```javascript
// setupTests.ts
import '@testing-library/jest-dom';
import { configure } from '@testing-library/react';

configure({ testIdAttribute: 'data-testid' });
```

### Mock Service Worker (MSW)
API mocking for isolated component testing:
```javascript
// Mock API responses for testing
const handlers = [
  rest.get('/api/v1/expenses', (req, res, ctx) => {
    return res(ctx.json(mockExpenses));
  }),
];
```

### Test Utilities
Common testing utilities and helpers:
```javascript
// Custom render function with providers
const renderWithProviders = (ui, options = {}) => {
  const AllTheProviders = ({ children }) => (
    <AuthProvider>
      <ConfigurationProvider>
        {children}
      </ConfigurationProvider>
    </AuthProvider>
  );
  
  return render(ui, { wrapper: AllTheProviders, ...options });
};
```

## 📊 Test Patterns

### Component Rendering Test
```javascript
test('renders expense management component', () => {
  renderWithProviders(<ExpenseManagement />);
  expect(screen.getByText('Expense Management')).toBeInTheDocument();
});
```

### User Interaction Test
```javascript
test('handles expense creation', async () => {
  renderWithProviders(<ExpenseManagement />);
  
  const addButton = screen.getByText('Add Expense');
  fireEvent.click(addButton);
  
  await waitFor(() => {
    expect(screen.getByText('New Expense Form')).toBeInTheDocument();
  });
});
```

### API Integration Test
```javascript
test('loads expenses from API', async () => {
  renderWithProviders(<ExpenseManagement />);
  
  await waitFor(() => {
    expect(screen.getByText('Office Supplies')).toBeInTheDocument();
  });
});
```

### Error Handling Test
```javascript
test('displays error message on API failure', async () => {
  // Mock API failure
  server.use(
    rest.get('/api/v1/expenses', (req, res, ctx) => {
      return res(ctx.status(500));
    })
  );
  
  renderWithProviders(<ExpenseManagement />);
  
  await waitFor(() => {
    expect(screen.getByText('Failed to load expenses')).toBeInTheDocument();
  });
});
```

## 🎯 Testing Best Practices

### Component Testing
- **Test user interactions** rather than implementation details
- **Use semantic queries** (getByRole, getByLabelText) over getByTestId
- **Test accessibility** with screen reader compatible queries
- **Mock external dependencies** (APIs, third-party libraries)
- **Test error states** and loading states

### Context Testing
- **Test state changes** through user actions
- **Verify context value updates** propagate to consumers
- **Test context provider** initialization and cleanup
- **Mock localStorage/sessionStorage** for persistence testing

### Integration Testing
- **Test complete user workflows** from start to finish
- **Verify component communication** and data flow
- **Test routing** and navigation between pages
- **Validate form submissions** and data persistence

## 🚨 Common Issues

### Test Environment Issues
```bash
# Clear Jest cache if tests behave unexpectedly
npm test -- --clearCache

# Update snapshots if component output changes
npm test -- --updateSnapshot
```

### Mock Issues
```bash
# Verify MSW handlers are properly configured
# Check mock data matches expected API responses
# Ensure mocks are reset between tests
```

### Async Testing Issues
```bash
# Use waitFor for async operations
# Avoid act() warnings with proper async handling
# Mock timers for time-dependent tests
```

## 📈 Coverage Goals

### Target Coverage
- **Components**: 80%+ coverage
- **Contexts**: 90%+ coverage
- **Utilities**: 85%+ coverage
- **Integration**: All critical paths covered

### Coverage Reports
```bash
# Generate coverage report
npm test -- --coverage --watchAll=false

# View detailed coverage
open coverage/lcov-report/index.html
```

## 🔗 Related Testing

- **Backend Tests**: [../backend/](../backend/)
- **Script Tests**: [../scripts/](../scripts/)
- **Testing Documentation**: [../../docs/testing/](../../docs/testing/)

## 📞 Support

### Debugging Tests
1. **Use screen.debug()** to see rendered output
2. **Check console logs** for React warnings
3. **Verify mock setup** for API calls
4. **Use React DevTools** for component inspection

### Writing New Tests
1. **Follow existing patterns** in test files
2. **Use descriptive test names** that explain user scenarios
3. **Test from user perspective** rather than implementation
4. **Include accessibility testing** where appropriate
5. **Mock external dependencies** for isolated testing

### Performance Testing
- **Use React Profiler** for performance analysis
- **Test component re-rendering** with React.memo
- **Validate lazy loading** and code splitting
- **Monitor bundle size** impact of new components
