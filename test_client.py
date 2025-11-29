"""
Test client for the authentication API
Run this after starting the server with: uvicorn main:app --reload
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def print_response(response, title=""):
    """Helper function to print formatted response"""
    print(f"\n{'='*60}")
    if title:
        print(f"{title}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response:")
        print(json.dumps(response.json(), indent=2))
    except:
        print(f"Response: {response.text}")
    print(f"{'='*60}\n")

# Test Registration
print("🔐 Testing User Authentication API\n")

# 1. Register a new user
print("1️⃣  POST /register - Register a new user")
register_data = {
    "username": "testuser",
    "password": "testpassword123"
}
response = requests.post(f"{BASE_URL}/register", json=register_data)
print_response(response, "Registration")

# Try to register the same user again (should fail)
print("2️⃣  POST /register - Try to register same user (should fail)")
response = requests.post(f"{BASE_URL}/register", json=register_data)
print_response(response, "Duplicate Registration")

# 3. Login with correct credentials
print("3️⃣  POST /login - Login with correct credentials")
login_data = {
    "username": "testuser",
    "password": "testpassword123"
}
response = requests.post(f"{BASE_URL}/login", data=login_data)
print_response(response, "Login Success")

# Extract tokens for authenticated requests
token = response.json()["access_token"]
refresh_token = response.json()["refresh_token"]
print(f"✅ Access Token: {token[:50]}...")
print(f"✅ Refresh Token: {refresh_token[:50]}...")

# 4. Login with wrong password (should fail)
print("4️⃣  POST /login - Login with wrong password (should fail)")
wrong_login = {
    "username": "testuser",
    "password": "wrongpassword"
}
response = requests.post(f"{BASE_URL}/login", data=wrong_login)
print_response(response, "Login Failure")

# 5. Get current user info (authenticated)
print("5️⃣  GET /me - Get current user info (requires authentication)")
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{BASE_URL}/me", headers=headers)
print_response(response, "Get Current User")

# 6. Try to access /me without token (should fail)
print("6️⃣  GET /me - Try without token (should fail)")
response = requests.get(f"{BASE_URL}/me")
print_response(response, "Unauthorized Access")

# 7. Refresh access token using refresh token
print("7️⃣  POST /refresh - Refresh access token using refresh token")
refresh_data = {"refresh_token": refresh_token}
response = requests.post(f"{BASE_URL}/refresh", json=refresh_data)
print_response(response, "Token Refresh")

# Extract new tokens
if response.status_code == 200:
    new_access_token = response.json()["access_token"]
    new_refresh_token = response.json()["refresh_token"]
    print(f"✅ New Access Token: {new_access_token[:50]}...")
    print(f"✅ New Refresh Token: {new_refresh_token[:50]}...")
    
    # 8. Use new access token
    print("\n8️⃣  GET /me - Use new access token")
    headers = {"Authorization": f"Bearer {new_access_token}"}
    response = requests.get(f"{BASE_URL}/me", headers=headers)
    print_response(response, "Get Current User with New Token")
    
    # 9. Logout (revoke refresh token)
    print("9️⃣  POST /logout - Logout and revoke refresh token")
    logout_data = {"refresh_token": new_refresh_token}
    response = requests.post(f"{BASE_URL}/logout", json=logout_data)
    print_response(response, "Logout")
    
    # 10. Try to refresh with revoked token (should fail)
    print("🔟 POST /refresh - Try to refresh with revoked token (should fail)")
    response = requests.post(f"{BASE_URL}/refresh", json=logout_data)
    print_response(response, "Refresh with Revoked Token")

print("\n✅ All tests completed!")
print("\n💡 How to use:")
print("   1. Register: POST /register with {username, password}")
print("   2. Login: POST /login with {username, password} - returns access_token and refresh_token")
print("   3. Use access_token: Add header 'Authorization: Bearer <access_token>' (expires in 30 min)")
print("   4. Refresh: POST /refresh with {refresh_token} - get new tokens (refresh_token lasts 7 days)")
print("   5. Logout: POST /logout with {refresh_token} - revoke refresh token")

