import requests
import json

def test_service_creation():
    """Test service creation with proper error handling"""
    
    print("Testing admin login...")
    login_response = requests.post(
        "https://app-fpsvflzd.fly.dev/api/auth/login",
        json={"email": "admin@schnittwerk.com", "password": "admin123"}
    )
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.text}")
        return
    
    token = login_response.json()["access_token"]
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    print("✅ Admin login successful")
    
    print("\nTesting service creation...")
    service_data = {
        "name": "Test Service",
        "category": "haircut",
        "service_type": "women",
        "duration": 60,
        "price": 50.0,
        "description": "Test description"
    }
    
    response = requests.post(
        "https://app-fpsvflzd.fly.dev/api/admin/services",
        json=service_data,
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ Service creation successful")
    else:
        print(f"❌ Service creation failed")

if __name__ == "__main__":
    test_service_creation()
