#!/usr/bin/env python3
"""
Test script for the Enable Monthly Tracking API endpoint.
This script tests the complete workflow after fixing the import issue.
"""

import requests
import json
import sys

def test_monthly_tracking_api():
    """Test the enable monthly tracking API endpoint"""
    
    # API endpoint
    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/api/v1/fees/enable-monthly-tracking"
    
    # Test data - replace with actual student ID from your database
    test_data = {
        "fee_record_ids": [35],  # This is actually student_id
        "start_month": 4,
        "start_year": 2025
    }
    
    print("🧪 Testing Enable Monthly Tracking API")
    print("=" * 50)
    print(f"Endpoint: {endpoint}")
    print(f"Payload: {json.dumps(test_data, indent=2)}")
    
    try:
        # Make the API request
        print("\n🚀 Making API request...")
        response = requests.post(
            endpoint,
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Success! API request completed successfully")
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            
            # Analyze the response
            if "results" in result:
                for student_result in result["results"]:
                    student_id = student_result.get("student_id")
                    student_name = student_result.get("student_name")
                    success = student_result.get("success")
                    fee_created = student_result.get("fee_record_created")
                    records_created = student_result.get("records_created")
                    message = student_result.get("message")
                    
                    print(f"\n📊 Student {student_id} ({student_name}):")
                    print(f"   Success: {success}")
                    print(f"   Fee Record Created: {fee_created}")
                    print(f"   Monthly Records Created: {records_created}")
                    print(f"   Message: {message}")
            
            return True
            
        elif response.status_code == 401:
            print("❌ Authentication Error: Please ensure you're logged in")
            print("This test requires authentication. Try testing through the UI instead.")
            return False
            
        elif response.status_code == 500:
            print("❌ Internal Server Error")
            try:
                error_detail = response.json()
                print(f"Error Details: {json.dumps(error_detail, indent=2)}")
                
                if "text" in str(error_detail):
                    print("\n🔧 Likely Issue: Missing 'text' import in fees.py")
                    print("Solution: Add 'text' to the SQLAlchemy imports")
                elif "enable_monthly_tracking_complete" in str(error_detail):
                    print("\n🔧 Likely Issue: Database function not created")
                    print("Solution: Run the enable_monthly_tracking_complete_function.sql script")
                    
            except:
                print(f"Raw Error Response: {response.text}")
            return False
            
        else:
            print(f"❌ Unexpected Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Is the FastAPI server running on localhost:8000?")
        return False
    except requests.exceptions.Timeout:
        print("❌ Timeout Error: Request took too long")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")
        return False

def main():
    """Main function"""
    print("🔍 Enable Monthly Tracking API Test")
    print("This script tests the API endpoint after fixing the import issue")
    print()
    
    success = test_monthly_tracking_api()
    
    if success:
        print("\n✅ Test completed successfully!")
        print("\n📋 Next Steps:")
        print("1. The API endpoint is working correctly")
        print("2. Test the complete workflow through the UI")
        print("3. Verify fee records and monthly tracking records are created")
    else:
        print("\n❌ Test failed!")
        print("\n🔧 Troubleshooting Steps:")
        print("1. Ensure FastAPI server is running (python main.py)")
        print("2. Run the database function SQL script")
        print("3. Check that 'text' is imported in fees.py")
        print("4. Verify student ID exists in database")
        sys.exit(1)

if __name__ == "__main__":
    main()
