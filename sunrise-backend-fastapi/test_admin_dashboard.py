#!/usr/bin/env python3
"""
Test script to verify admin login and dashboard access
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_admin_login_and_dashboard():
    """Test admin login and verify dashboard access"""
    print("🧪 Testing Admin Login and Dashboard Access")
    print("=" * 50)
    
    # Test 1: Admin Login
    print("1️⃣ Testing Admin Login...")
    login_data = {
        "email": "admin@sunriseschool.edu",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login-json", json=login_data)
        response.raise_for_status()
        login_result = response.json()
        
        print(f"✅ Login successful!")
        print(f"   User: {login_result['user']['first_name']} {login_result['user']['last_name']}")
        print(f"   Email: {login_result['user']['email']}")
        print(f"   User Type: {login_result['user']['user_type']}")
        print(f"   Permissions: {len(login_result['permissions'])} permissions")
        
        # Extract token
        token = login_result['access_token']
        
        # Test 2: Verify Token with /auth/me
        print("\n2️⃣ Testing Token Verification...")
        headers = {"Authorization": f"Bearer {token}"}
        me_response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        me_response.raise_for_status()
        me_result = me_response.json()
        
        print(f"✅ Token verification successful!")
        print(f"   User ID: {me_result['id']}")
        print(f"   User Type: {me_result['user_type']}")
        print(f"   Is Active: {me_result['is_active']}")
        
        # Test 3: Check Dashboard Permission
        print("\n3️⃣ Testing Dashboard Permission...")
        has_dashboard_permission = "view_admin_dashboard" in login_result['permissions']
        user_type_is_admin = login_result['user']['user_type'].upper() == 'ADMIN'
        
        print(f"✅ Dashboard Permission Check:")
        print(f"   Has 'view_admin_dashboard' permission: {has_dashboard_permission}")
        print(f"   User type is ADMIN: {user_type_is_admin}")
        print(f"   Should show Dashboard menu: {has_dashboard_permission and user_type_is_admin}")
        
        # Test 4: Frontend Case Sensitivity
        print("\n4️⃣ Testing Frontend Case Sensitivity...")
        frontend_check = login_result['user']['user_type'].lower() == 'admin'
        print(f"✅ Frontend Compatibility:")
        print(f"   Database user_type: '{login_result['user']['user_type']}'")
        print(f"   Lowercase comparison: '{login_result['user']['user_type'].lower()}' == 'admin' → {frontend_check}")
        
        print("\n🎉 All tests passed! Admin dashboard should be visible.")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_admin_login_and_dashboard()
    exit(0 if success else 1)
