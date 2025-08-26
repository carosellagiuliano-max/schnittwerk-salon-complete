import requests
import json

def test_stylist_creation():
    """Test stylist creation with proper error handling"""
    
    print("Testing admin login...")
    login_response = requests.post(
        "http://localhost:8000/api/auth/login",
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
    
    print("\nTesting stylist creation with unique email...")
    stylist_data = {
        "name": "Test Stylist Unique",
        "email": "unique-test@example.com",
        "phone": "123456789",
        "specialties": "Damenschnitt"
    }
    
    response = requests.post(
        "http://localhost:8000/api/admin/stylists",
        json=stylist_data,
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("✅ Stylist creation with unique email successful")
        print(f"Created stylist: {response.json()}")
    else:
        print(f"❌ Stylist creation failed: {response.text}")
    
    print("\nTesting stylist creation with duplicate email...")
    duplicate_response = requests.post(
        "http://localhost:8000/api/admin/stylists",
        json=stylist_data,  # Same email as above
        headers=headers
    )
    
    print(f"Duplicate Status Code: {duplicate_response.status_code}")
    if duplicate_response.status_code == 400:
        error_detail = duplicate_response.json().get("detail", "")
        print(f"✅ Duplicate email properly rejected: {error_detail}")
    else:
        print(f"❌ Duplicate email handling failed: {duplicate_response.text}")

if __name__ == "__main__":
    test_stylist_creation()
