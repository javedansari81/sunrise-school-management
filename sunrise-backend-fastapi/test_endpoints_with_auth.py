#!/usr/bin/env python3
"""
Test the leaves endpoints with proper authentication
"""
import asyncio
import sys
import os
import httpx
import json

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

async def test_endpoints_with_auth():
    """Test the endpoints that were failing with 422 errors"""
    print("🔍 Testing Leaves Endpoints with Authentication...")
    
    base_url = "http://localhost:8000"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # First, try to login to get a token
            print("1. Attempting to login...")
            login_response = await client.post(
                f"{base_url}/api/v1/auth/login-json",
                json={"email": "admin@sunriseschool.edu", "password": "admin123"}
            )
            
            if login_response.status_code != 200:
                print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
                return False
            
            login_data = login_response.json()
            token = login_data.get("access_token")
            
            if not token:
                print(f"❌ No token received: {login_data}")
                return False
            
            print(f"✅ Login successful, got token: {token[:20]}...")
            
            # Set up headers with authentication
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test the pending leaves endpoint
            print("2. Testing /api/v1/leaves/pending endpoint...")
            pending_response = await client.get(
                f"{base_url}/api/v1/leaves/pending",
                headers=headers
            )
            
            print(f"   Status: {pending_response.status_code}")
            if pending_response.status_code == 200:
                pending_data = pending_response.json()
                print(f"   ✅ Success: Found {len(pending_data)} pending requests")
            else:
                print(f"   ❌ Failed: {pending_response.text}")
            
            # Test the statistics endpoint
            print("3. Testing /api/v1/leaves/statistics endpoint...")
            stats_response = await client.get(
                f"{base_url}/api/v1/leaves/statistics",
                headers=headers
            )
            
            print(f"   Status: {stats_response.status_code}")
            if stats_response.status_code == 200:
                stats_data = stats_response.json()
                print(f"   ✅ Success: {json.dumps(stats_data, indent=2)}")
            else:
                print(f"   ❌ Failed: {stats_response.text}")
            
            # Test without authentication to confirm it fails properly
            print("4. Testing without authentication (should fail with 401)...")
            no_auth_response = await client.get(f"{base_url}/api/v1/leaves/pending")
            print(f"   Status without auth: {no_auth_response.status_code}")
            if no_auth_response.status_code == 401:
                print("   ✅ Correctly rejected unauthenticated request")
            else:
                print(f"   ⚠️ Unexpected status: {no_auth_response.status_code}")
            
            return True
        
    except httpx.ConnectError:
        print("❌ Could not connect to server. Make sure the server is running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_endpoints_with_auth())
