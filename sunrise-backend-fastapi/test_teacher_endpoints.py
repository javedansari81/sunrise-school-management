#!/usr/bin/env python3
"""
Test script for teacher management endpoints
"""
import requests
import json

def test_teacher_endpoints():
    base_url = 'http://localhost:8000/api/v1'
    
    print("🧪 Testing Teacher Management Endpoints")
    print("=" * 50)
    
    # Test 1: Configuration endpoint
    print("\n1. Testing teacher-management configuration...")
    try:
        response = requests.get(f'{base_url}/configuration/teacher-management/')
        print(f'   Status: {response.status_code}')
        if response.status_code == 200:
            config = response.json()
            print(f'   Available metadata: {list(config.keys())}')
            if 'genders' in config:
                print(f'   Genders: {len(config["genders"])} items')
            if 'qualifications' in config:
                print(f'   Qualifications: {len(config["qualifications"])} items')
            if 'employment_statuses' in config:
                print(f'   Employment Statuses: {len(config["employment_statuses"])} items')
        else:
            print(f'   Error: {response.text}')
    except Exception as e:
        print(f'   Configuration test failed: {e}')
    
    # Test 2: Teachers endpoint (without auth)
    print("\n2. Testing teachers endpoint (no auth)...")
    try:
        response = requests.get(f'{base_url}/teachers/')
        print(f'   Status: {response.status_code}')
        if response.status_code == 401:
            print('   ✅ Authentication required (expected)')
        elif response.status_code == 200:
            data = response.json()
            print(f'   Teachers found: {data.get("total", 0)}')
        else:
            print(f'   Error: {response.text}')
    except Exception as e:
        print(f'   Teachers test failed: {e}')
    
    # Test 3: Teacher options endpoints
    print("\n3. Testing teacher options endpoints...")
    options_endpoints = [
        '/teachers/options/departments',
        '/teachers/options/positions',
        '/teachers/options/qualifications',
        '/teachers/options/employment-status'
    ]
    
    for endpoint in options_endpoints:
        try:
            response = requests.get(f'{base_url}{endpoint}')
            print(f'   {endpoint}: Status {response.status_code}')
            if response.status_code == 401:
                print('     ✅ Authentication required (expected)')
        except Exception as e:
            print(f'     Error: {e}')
    
    print("\n" + "=" * 50)
    print("✅ Teacher endpoint tests completed!")

if __name__ == "__main__":
    test_teacher_endpoints()
