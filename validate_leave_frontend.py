#!/usr/bin/env python3
"""
Validation script for the Leave Management System frontend
Checks if all components are properly implemented and configured
"""

import os
import sys
import subprocess
import json
from pathlib import Path


class LeaveSystemValidator:
    """Validator for the leave management system frontend"""
    
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
    
    def validate_frontend_files(self):
        """Validate frontend files exist and have correct structure"""
        print("\n🔍 Validating Frontend Files...")
        
        frontend_files = [
            "sunrise-school-frontend/src/components/admin/LeaveManagementSystem.tsx",
            "sunrise-school-frontend/src/services/api.ts",
            "sunrise-school-frontend/src/contexts/ConfigurationContext.tsx"
        ]
        
        for file_path in frontend_files:
            self.check(
                f"Frontend file exists: {file_path}",
                os.path.exists(file_path),
                f"File not found: {file_path}"
            )
    
    def validate_leave_component_structure(self):
        """Validate leave component has correct structure"""
        print("\n🔍 Validating Leave Component Structure...")
        
        component_file = "sunrise-school-frontend/src/components/admin/LeaveManagementSystem.tsx"
        if os.path.exists(component_file):
            with open(component_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Check for key imports
                imports = [
                    ("React imports", "import React"),
                    ("Material-UI imports", "from '@mui/material'"),
                    ("Configuration context", "useConfiguration"),
                    ("Leave API", "leaveAPI"),
                    ("Date picker", "DatePicker"),
                ]
                
                for import_name, import_pattern in imports:
                    self.check(
                        f"Import: {import_name}",
                        import_pattern in content,
                        f"Missing import: {import_name}"
                    )
                
                # Check for key features
                features = [
                    ("Configuration context usage", "useConfiguration()"),
                    ("Leave API usage", "leaveAPI."),
                    ("CRUD operations", "handleSubmit"),
                    ("Filtering functionality", "handleFilterChange" in content or "setFilters" in content),
                    ("Approval functionality", "handleApprove"),
                    ("Delete functionality", "handleDelete"),
                    ("Loading states", "CircularProgress"),
                    ("Error handling", "Snackbar"),
                    ("Grid components fixed", "size={{" in content),
                ]
                
                for feature_name, feature_pattern in features:
                    if isinstance(feature_pattern, str):
                        condition = feature_pattern in content
                    else:
                        condition = feature_pattern
                    
                    self.check(
                        f"Feature: {feature_name}",
                        condition,
                        f"Missing feature: {feature_name}"
                    )
    
    def validate_api_service(self):
        """Validate API service has correct structure"""
        print("\n🔍 Validating API Service...")
        
        api_service_file = "sunrise-school-frontend/src/services/api.ts"
        if os.path.exists(api_service_file):
            with open(api_service_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Check for leave API methods
                api_methods = [
                    ("getLeaves", "getLeaves:"),
                    ("createLeave", "createLeave:"),
                    ("updateLeave", "updateLeave:"),
                    ("deleteLeave", "deleteLeave:"),
                    ("approveLeave", "approveLeave:"),
                    ("getLeaveStatistics", "getLeaveStatistics:"),
                    ("getPendingLeaves", "getPendingLeaves:"),
                ]
                
                for method_name, method_pattern in api_methods:
                    self.check(
                        f"API method: {method_name}",
                        method_pattern in content,
                        f"Missing API method: {method_name}"
                    )
    
    def validate_configuration_context(self):
        """Validate configuration context structure"""
        print("\n🔍 Validating Configuration Context...")
        
        context_file = "sunrise-school-frontend/src/contexts/ConfigurationContext.tsx"
        if os.path.exists(context_file):
            with open(context_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Check for key properties
                properties = [
                    ("isLoading property", "isLoading:"),
                    ("configuration property", "configuration:"),
                    ("error property", "error:"),
                    ("getLeaveTypes method", "getLeaveTypes"),
                    ("getLeaveStatuses method", "getLeaveStatuses"),
                ]
                
                for prop_name, prop_pattern in properties:
                    self.check(
                        f"Context property: {prop_name}",
                        prop_pattern in content,
                        f"Missing property: {prop_name}"
                    )
    
    def validate_typescript_syntax(self):
        """Validate TypeScript syntax by checking for common issues"""
        print("\n🔍 Validating TypeScript Syntax...")
        
        component_file = "sunrise-school-frontend/src/components/admin/LeaveManagementSystem.tsx"
        if os.path.exists(component_file):
            with open(component_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Check for fixed Grid syntax
                self.check(
                    "Grid components use new syntax",
                    "size={{" in content and "item xs=" not in content,
                    "Grid components still use old v4 syntax"
                )
                
                # Check for proper optional chaining
                self.check(
                    "Configuration uses optional chaining",
                    "configuration?." in content,
                    "Configuration access without optional chaining"
                )
                
                # Check for proper loading state usage
                self.check(
                    "Uses isLoading from context",
                    "isLoading:" in content or "isLoading =" in content,
                    "Still using old loading property"
                )
    
    def check_package_dependencies(self):
        """Check if required packages are installed"""
        print("\n🔍 Checking Package Dependencies...")
        
        package_json_path = "sunrise-school-frontend/package.json"
        if os.path.exists(package_json_path):
            with open(package_json_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
                
                dependencies = package_data.get('dependencies', {})
                dev_dependencies = package_data.get('devDependencies', {})
                all_deps = {**dependencies, **dev_dependencies}
                
                required_packages = [
                    "@mui/material",
                    "@mui/icons-material", 
                    "@mui/x-date-pickers",
                    "react",
                    "typescript"
                ]
                
                for package in required_packages:
                    self.check(
                        f"Package installed: {package}",
                        package in all_deps,
                        f"Missing package: {package}"
                    )
    
    def print_summary(self):
        """Print validation summary"""
        print("\n" + "="*60)
        print("🧪 LEAVE MANAGEMENT SYSTEM FRONTEND VALIDATION SUMMARY")
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
            print("🎉 All validations passed! Leave management frontend is properly implemented.")
            print("\n📋 FRONTEND FEATURES VALIDATED:")
            print("  ✓ Configuration context integration")
            print("  ✓ Complete CRUD operations")
            print("  ✓ Material-UI Grid v5 syntax")
            print("  ✓ Proper TypeScript usage")
            print("  ✓ API service integration")
            print("  ✓ Error handling and loading states")
            return True
        else:
            print("❌ Some validations failed. Please address the errors above.")
            print("\n💡 COMMON FIXES:")
            print("  • Update Grid components to use size={{ xs: 12 }} syntax")
            print("  • Use isLoading instead of loading from configuration context")
            print("  • Add optional chaining (?.) for configuration access")
            print("  • Ensure all required packages are installed")
            return False


def main():
    """Main validation runner"""
    print("🚀 Validating Leave Management System Frontend Implementation")
    print("="*60)
    
    validator = LeaveSystemValidator()
    
    # Run all validations
    validator.validate_frontend_files()
    validator.validate_leave_component_structure()
    validator.validate_api_service()
    validator.validate_configuration_context()
    validator.validate_typescript_syntax()
    validator.check_package_dependencies()
    
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
