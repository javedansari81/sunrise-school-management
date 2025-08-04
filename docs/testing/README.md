# Testing Documentation

This directory contains comprehensive testing guides, procedures, and troubleshooting documentation for the Sunrise School Management System.

## 📋 Available Guides

### 🧪 [EXPENSE_SOFT_DELETE_TESTING_GUIDE.md](./EXPENSE_SOFT_DELETE_TESTING_GUIDE.md)
**Comprehensive Soft Delete Testing**
- Pre-testing setup and database migration
- Step-by-step testing scenarios
- Authorization and permission testing
- Performance and edge case validation
- Success criteria checklist

### ✅ [VERIFICATION_STEPS.md](./VERIFICATION_STEPS.md)
**System Verification Procedures**
- Post-deployment verification steps
- Feature functionality checks
- Integration testing procedures
- User acceptance testing guidelines

### 🔧 [SOFT_DELETE_TROUBLESHOOTING_SUMMARY.md](./SOFT_DELETE_TROUBLESHOOTING_SUMMARY.md)
**Troubleshooting Guide**
- Common soft delete issues and solutions
- Database migration problems
- UI/UX troubleshooting
- Performance optimization tips

## 🎯 Testing Categories

### Unit Testing
- Backend API endpoint testing
- Frontend component testing
- Database model validation
- Business logic verification

### Integration Testing
- Frontend-backend communication
- Database integration
- Authentication flow testing
- Cross-service functionality

### Feature Testing
- Soft delete functionality
- User permission systems
- Data integrity validation
- UI/UX behavior verification

### Performance Testing
- Database query optimization
- API response times
- Frontend load performance
- Memory usage validation

## 🚀 Quick Testing Workflow

### 1. Pre-Testing Setup
```bash
# Ensure test environment is ready
cd sunrise-backend-fastapi
python scripts/run_tests.py

cd ../sunrise-school-frontend
npm test
```

### 2. Feature-Specific Testing
- Follow the relevant testing guide
- Execute all test scenarios
- Document any issues found
- Verify fixes before deployment

### 3. Integration Verification
- Test complete user workflows
- Verify cross-component functionality
- Check data consistency
- Validate security measures

### 4. Performance Validation
- Monitor response times
- Check database performance
- Validate memory usage
- Test under load conditions

## 🧪 Testing Tools and Frameworks

### Backend Testing
- **pytest** - Python testing framework
- **httpx** - Async HTTP client for API testing
- **SQLAlchemy** - Database testing utilities
- **Factory Boy** - Test data generation

### Frontend Testing
- **Jest** - JavaScript testing framework
- **React Testing Library** - Component testing
- **MSW** - API mocking for tests
- **Cypress** - End-to-end testing (optional)

### Database Testing
- **PostgreSQL Test Database** - Isolated test environment
- **Alembic** - Migration testing
- **SQL Scripts** - Data validation queries

## 📊 Testing Checklist

### Before Testing
- [ ] Test environment is set up
- [ ] Database migrations are applied
- [ ] All dependencies are installed
- [ ] Test data is prepared

### During Testing
- [ ] Follow test procedures step-by-step
- [ ] Document all findings
- [ ] Test both positive and negative scenarios
- [ ] Verify error handling

### After Testing
- [ ] All tests pass successfully
- [ ] Performance meets requirements
- [ ] Security measures are validated
- [ ] Documentation is updated

## 🚨 Common Testing Issues

### Database Issues
- Migration failures
- Test data conflicts
- Connection problems
- Performance degradation

### API Testing Issues
- Authentication failures
- CORS configuration problems
- Response format issues
- Timeout problems

### Frontend Testing Issues
- Component rendering problems
- State management issues
- API integration failures
- Browser compatibility

### Integration Issues
- Service communication failures
- Data synchronization problems
- Authentication flow issues
- Cross-browser compatibility

## 🔍 Debugging and Troubleshooting

### Backend Debugging
```bash
# Enable debug logging
export DEBUG=true
python main.py

# Run specific test categories
python scripts/run_tests.py auth
python scripts/run_tests.py database
```

### Frontend Debugging
```bash
# Run tests in watch mode
npm test -- --watch

# Run specific test files
npm test -- --testPathPattern=ExpenseManagement
```

### Database Debugging
```sql
-- Check test data integrity
SELECT COUNT(*) FROM expenses WHERE is_deleted = false;

-- Verify migration status
SELECT version_num FROM alembic_version;
```

## 📈 Test Coverage Goals

### Backend Coverage
- **API Endpoints**: 95%+ coverage
- **Business Logic**: 90%+ coverage
- **Database Models**: 85%+ coverage
- **Utility Functions**: 80%+ coverage

### Frontend Coverage
- **Components**: 80%+ coverage
- **Services**: 90%+ coverage
- **Utilities**: 85%+ coverage
- **Integration**: 70%+ coverage

## 🔗 Related Documentation

- **Setup Guides**: [../setup/](../setup/)
- **Database Documentation**: [../database/](../database/)
- **Feature Documentation**: [../features/](../features/)
- **Deployment Guides**: [../deployment/](../deployment/)

## 📞 Testing Support

### Getting Help
1. Check the specific testing guide for your feature
2. Review troubleshooting documentation
3. Consult setup guides for environment issues
4. Check feature documentation for expected behavior

### Reporting Issues
- Document the exact steps to reproduce
- Include error messages and logs
- Specify the testing environment
- Provide expected vs actual behavior
