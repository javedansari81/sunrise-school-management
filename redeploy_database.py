"""
Script to drop sunrise schema and redeploy the entire database
"""
import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"
DEPLOY_ENDPOINT = f"{BASE_URL}/api/v1/database/deploy"
STATUS_ENDPOINT = f"{BASE_URL}/api/v1/database/status"

def check_server():
    """Check if the backend server is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def deploy_database():
    """Deploy the database by calling the API endpoint"""
    print("=" * 60)
    print("SUNRISE SCHOOL DATABASE REDEPLOYMENT")
    print("=" * 60)
    print()
    
    # Check if server is running
    print("Checking if backend server is running...")
    if not check_server():
        print("❌ Backend server is not running!")
        print()
        print("Please start the backend server first:")
        print("  cd sunrise-backend-fastapi")
        print("  python -m uvicorn app.main:app --reload")
        print()
        return False
    
    print("✓ Backend server is running")
    print()
    
    # Confirm action
    print("⚠️  WARNING: This will DROP the entire sunrise schema and ALL data!")
    print("⚠️  This action cannot be undone!")
    print()
    response = input("Are you sure you want to continue? (yes/no): ")
    
    if response.lower() != 'yes':
        print("Deployment cancelled.")
        return False
    
    print()
    print("Starting database redeployment...")
    print("-" * 60)
    
    try:
        # Call the deployment endpoint
        response = requests.post(DEPLOY_ENDPOINT, timeout=300)
        
        if response.status_code == 200:
            result = response.json()
            
            print()
            print("=" * 60)
            print("DEPLOYMENT RESULT")
            print("=" * 60)
            print()
            
            if result.get('success'):
                print("✓ Database deployment SUCCESSFUL!")
                print()
                print(f"Total Steps: {result.get('total_steps', 0)}")
                print(f"Completed: {result.get('completed_steps', 0)}")
                print(f"Failed: {result.get('failed_steps', 0)}")
                print()
                
                # Show step details
                print("Deployment Steps:")
                print("-" * 60)
                for step in result.get('steps', []):
                    status_icon = "✓" if step['status'] == 'success' else "✗"
                    print(f"{status_icon} {step['step']}: {step['message']}")
                    if step.get('error'):
                        print(f"  Error: {step['error']}")
                
                print()
                print("=" * 60)
                print("DATABASE READY!")
                print("=" * 60)
                print()
                print("Default Admin Credentials:")
                print("  Email: admin@sunriseschool.edu")
                print("  Password: admin123")
                print()
                print("You can now access the application at:")
                print(f"  {BASE_URL}")
                print()
                
                return True
            else:
                print("✗ Database deployment FAILED!")
                print()
                print(f"Error: {result.get('message', 'Unknown error')}")
                print()
                print("Failed Steps:")
                print("-" * 60)
                for step in result.get('steps', []):
                    if step['status'] == 'failed':
                        print(f"✗ {step['step']}: {step['message']}")
                        if step.get('error'):
                            print(f"  Error: {step['error']}")
                print()
                return False
        else:
            print(f"✗ HTTP Error {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("✗ Request timed out. The deployment might still be running.")
        print("Check the backend logs for details.")
        return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def get_database_status():
    """Get current database status"""
    try:
        response = requests.get(STATUS_ENDPOINT, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print()
            print("=" * 60)
            print("CURRENT DATABASE STATUS")
            print("=" * 60)
            print()
            print(json.dumps(result, indent=2))
            print()
    except Exception as e:
        print(f"Could not get database status: {str(e)}")

if __name__ == "__main__":
    success = deploy_database()
    
    if success:
        # Wait a moment and then show database status
        time.sleep(1)
        get_database_status()

