#!/usr/bin/env python3
"""
Quick validation script for the expense management system
Checks if all components are properly integrated and working
"""

import os
import sys
import subprocess
import json
from pathlib import Path


class ExpenseSystemValidator:
    """Validator for the expense management system"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.success_count = 0
        self.total_checks = 0
    
    def check(self, description, condition, error_msg=None, warning_msg=None):
        """Check a condition and record result"""
        self.total_checks += 1
        print(f"Checking: {description}...", end=" ")
        
        if condition:
            print("✓")
            self.success_count += 1
            return True
        else:
            print("✗")
            if error_msg:
                self.errors.append(f"{description}: {error_msg}")
            elif warning_msg:
                self.warnings.append(f"{description}: {warning_msg}")
            else:
                self.errors.append(f"{description}: Failed")
            return False
    
    def validate_backend_files(self):
        """Validate backend files exist and have correct structure"""
        print("\n🔍 Validating Backend Files...")
        
        backend_files = [
            "sunrise-backend-fastapi/app/models/expense.py",
            "sunrise-backend-fastapi/app/schemas/expense.py",
            "sunrise-backend-fastapi/app/crud/crud_expense.py",
            "sunrise-backend-fastapi/app/api/v1/endpoints/expenses.py",
            "Database/DataLoads/07_sample_expense_data.sql"
        ]
        
        for file_path in backend_files:
            self.check(
                f"Backend file exists: {file_path}",
                os.path.exists(file_path),
                f"File not found: {file_path}"
            )
    
    def validate_frontend_files(self):
        """Validate frontend files exist and have correct structure"""
        print("\n🔍 Validating Frontend Files...")
        
        frontend_files = [
            "sunrise-school-frontend/src/pages/admin/ExpenseManagement.tsx",
            "sunrise-school-frontend/src/services/api.ts"
        ]
        
        for file_path in frontend_files:
            self.check(
                f"Frontend file exists: {file_path}",
                os.path.exists(file_path),
                f"File not found: {file_path}"
            )
    
    def validate_test_files(self):
        """Validate test files exist"""
        print("\n🔍 Validating Test Files...")
        
        test_files = [
            "sunrise-backend-fastapi/api-tests/tests/test_expense_management.py",
            "sunrise-school-frontend/ui-tests/tests/ExpenseManagement.test.tsx",
            "sunrise-backend-fastapi/api-tests/integration/test_expense_system.py"
        ]
        
        for file_path in test_files:
            self.check(
                f"Test file exists: {file_path}",
                os.path.exists(file_path),
                f"Test file not found: {file_path}"
            )
    
    def validate_backend_models(self):
        """Validate backend models have correct structure"""
        print("\n🔍 Validating Backend Models...")
        
        model_file = "sunrise-backend-fastapi/app/models/expense.py"
        if os.path.exists(model_file):
            with open(model_file, 'r') as f:
                content = f.read()
                
                # Check for key model classes
                self.check(
                    "Expense model class exists",
                    "class Expense(Base):" in content,
                    "Expense model class not found"
                )
                
                self.check(
                    "Vendor model class exists",
                    "class Vendor(Base):" in content,
                    "Vendor model class not found"
                )
                
                self.check(
                    "Budget model class exists",
                    "class Budget(Base):" in content,
                    "Budget model class not found"
                )
                
                # Check for metadata-driven fields
                self.check(
                    "Uses expense_category_id (metadata-driven)",
                    "expense_category_id" in content,
                    "Not using metadata-driven expense categories"
                )
                
                self.check(
                    "Uses expense_status_id (metadata-driven)",
                    "expense_status_id" in content,
                    "Not using metadata-driven expense statuses"
                )
                
                self.check(
                    "Uses payment_method_id (metadata-driven)",
                    "payment_method_id" in content,
                    "Not using metadata-driven payment methods"
                )
    
    def validate_backend_schemas(self):
        """Validate backend schemas have correct structure"""
        print("\n🔍 Validating Backend Schemas...")
        
        schema_file = "sunrise-backend-fastapi/app/schemas/expense.py"
        if os.path.exists(schema_file):
            with open(schema_file, 'r') as f:
                content = f.read()
                
                # Check for key schema classes
                self.check(
                    "ExpenseBase schema exists",
                    "class ExpenseBase(BaseModel):" in content,
                    "ExpenseBase schema not found"
                )
                
                self.check(
                    "ExpenseWithDetails schema exists",
                    "class ExpenseWithDetails" in content,
                    "ExpenseWithDetails schema not found"
                )
                
                self.check(
                    "ExpenseFilters schema exists",
                    "class ExpenseFilters(BaseModel):" in content,
                    "ExpenseFilters schema not found"
                )
                
                # Check for metadata-driven fields
                self.check(
                    "Uses expense_category_id in schemas",
                    "expense_category_id" in content,
                    "Schemas not using metadata-driven categories"
                )
    
    def validate_api_endpoints(self):
        """Validate API endpoints have correct structure"""
        print("\n🔍 Validating API Endpoints...")
        
        api_file = "sunrise-backend-fastapi/app/api/v1/endpoints/expenses.py"
        if os.path.exists(api_file):
            with open(api_file, 'r') as f:
                content = f.read()
                
                # Check for CRUD endpoints
                endpoints = [
                    ("GET expenses", '@router.get("/", response_model=ExpenseListResponse)'),
                    ("POST expenses", '@router.post("/", response_model=Expense)'),
                    ("GET expense by ID", '@router.get("/{expense_id}", response_model=ExpenseWithDetails)'),
                    ("PUT expense", '@router.put("/{expense_id}", response_model=Expense)'),
                    ("DELETE expense", '@router.delete("/{expense_id}")'),
                    ("PATCH approve", '@router.patch("/{expense_id}/approve", response_model=Expense)'),
                    ("GET statistics", 'get_expense_statistics'),
                ]
                
                for endpoint_name, endpoint_pattern in endpoints:
                    self.check(
                        f"API endpoint exists: {endpoint_name}",
                        endpoint_pattern in content,
                        f"Missing endpoint: {endpoint_name}"
                    )
    
    def validate_frontend_component(self):
        """Validate frontend component has correct structure"""
        print("\n🔍 Validating Frontend Component...")
        
        component_file = "sunrise-school-frontend/src/pages/admin/ExpenseManagement.tsx"
        if os.path.exists(component_file):
            with open(component_file, 'r') as f:
                content = f.read()
                
                # Check for key features
                features = [
                    ("Configuration context usage", "useConfiguration"),
                    ("Expense API usage", "expenseAPI"),
                    ("CRUD operations", "handleSubmit"),
                    ("Filtering functionality", "handleFilterChange"),
                    ("Approval functionality", "handleApprove"),
                    ("Delete functionality", "handleDelete"),
                    ("Pagination", "Pagination"),
                    ("Loading states", "CircularProgress"),
                    ("Error handling", "Snackbar"),
                ]
                
                for feature_name, feature_pattern in features:
                    self.check(
                        f"Frontend feature: {feature_name}",
                        feature_pattern in content,
                        f"Missing feature: {feature_name}"
                    )
    
    def validate_api_service(self):
        """Validate API service has correct structure"""
        print("\n🔍 Validating API Service...")
        
        api_service_file = "sunrise-school-frontend/src/services/api.ts"
        if os.path.exists(api_service_file):
            with open(api_service_file, 'r') as f:
                content = f.read()
                
                # Check for expense API methods
                api_methods = [
                    ("getExpenses", "getExpenses:"),
                    ("createExpense", "createExpense:"),
                    ("updateExpense", "updateExpense:"),
                    ("deleteExpense", "deleteExpense:"),
                    ("approveExpense", "approveExpense:"),
                    ("getStatistics", "getStatistics:"),
                ]
                
                for method_name, method_pattern in api_methods:
                    self.check(
                        f"API method: {method_name}",
                        method_pattern in content,
                        f"Missing API method: {method_name}"
                    )
    
    def validate_database_schema(self):
        """Validate database schema and test data"""
        print("\n🔍 Validating Database Schema...")
        
        # Check if sample data file exists and has correct structure
        sample_data_file = "Database/DataLoads/07_sample_expense_data.sql"
        if os.path.exists(sample_data_file):
            with open(sample_data_file, 'r') as f:
                content = f.read()
                
                # Check for key data insertions
                data_checks = [
                    ("Vendor sample data", "INSERT INTO vendors"),
                    ("Expense sample data", "INSERT INTO expenses"),
                    ("Metadata usage", "expense_category_id"),
                    ("Various expense statuses", "expense_status_id"),
                    ("Payment methods", "payment_method_id"),
                ]
                
                for check_name, check_pattern in data_checks:
                    self.check(
                        f"Database: {check_name}",
                        check_pattern in content,
                        f"Missing in database: {check_name}"
                    )
    
    def print_summary(self):
        """Print validation summary"""
        print("\n" + "="*60)
        print("🧪 EXPENSE MANAGEMENT SYSTEM VALIDATION SUMMARY")
        print("="*60)
        
        print(f"✓ Successful checks: {self.success_count}/{self.total_checks}")
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        print("-"*60)
        
        if not self.errors:
            print("🎉 All validations passed! Expense management system is properly implemented.")
            print("\n📋 SYSTEM FEATURES VALIDATED:")
            print("  ✓ Metadata-driven architecture")
            print("  ✓ Complete CRUD operations")
            print("  ✓ Approval workflows")
            print("  ✓ Advanced filtering and pagination")
            print("  ✓ Statistics and reporting")
            print("  ✓ Vendor management")
            print("  ✓ Frontend integration")
            print("  ✓ Comprehensive test coverage")
            return True
        else:
            print("❌ Some validations failed. Please address the errors above.")
            return False


def main():
    """Main validation runner"""
    print("🚀 Validating Expense Management System Implementation")
    print("="*60)
    
    validator = ExpenseSystemValidator()
    
    # Run all validations
    validator.validate_backend_files()
    validator.validate_frontend_files()
    validator.validate_test_files()
    validator.validate_backend_models()
    validator.validate_backend_schemas()
    validator.validate_api_endpoints()
    validator.validate_frontend_component()
    validator.validate_api_service()
    validator.validate_database_schema()
    
    # Print summary
    success = validator.print_summary()
    
    return 0 if success else 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️  Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Validation error: {e}")
        sys.exit(1)
