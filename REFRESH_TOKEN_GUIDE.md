# Refresh Token Implementation Guide

## Overview

The authentication system now uses **both access tokens and refresh tokens** for better security and user experience.

## How It Works

### Token Types

1. **Access Token** (Short-lived)
   - Expires in: **30 minutes**
   - Used for: API requests
   - Sent in: `Authorization: Bearer <token>` header
   - Purpose: Authenticate API calls

2. **Refresh Token** (Long-lived)
   - Expires in: **7 days**
   - Used for: Getting new access tokens
   - Stored in: Database (can be revoked)
   - Purpose: Get new access tokens without re-login

### Flow

```
1. User logs in → Gets both access_token + refresh_token
2. Use access_token for API calls (expires in 30 min)
3. When access_token expires → Use refresh_token to get new tokens
4. Refresh token rotates (old one deleted, new one created)
5. User can logout → Refresh token is revoked
```

## API Endpoints

### 1. Login - Get Tokens
**POST** `/login`

Request:
```
username: testuser
password: testpassword123
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "random-secure-token-string...",
  "token_type": "bearer"
}
```

### 2. Refresh - Get New Tokens
**POST** `/refresh`

Request:
```json
{
  "refresh_token": "your-refresh-token-here"
}
```

Response:
```json
{
  "access_token": "new-access-token...",
  "refresh_token": "new-refresh-token...",
  "token_type": "bearer"
}
```

**Note:** The old refresh token is automatically deleted (token rotation for security).

### 3. Logout - Revoke Token
**POST** `/logout`

Request:
```json
{
  "refresh_token": "your-refresh-token-here"
}
```

Response:
```json
{
  "message": "Successfully logged out"
}
```

## Database Schema

A new table `refresh_tokens` is automatically created:

```sql
CREATE TABLE refresh_tokens (
    id SERIAL PRIMARY KEY,
    token VARCHAR UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id),
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Security Features

✅ **Token Rotation**: Each refresh creates a new refresh token, old one is deleted  
✅ **Token Revocation**: Logout deletes refresh token from database  
✅ **Expiration**: Both tokens expire automatically  
✅ **Database Storage**: Refresh tokens stored in DB (can be revoked/managed)  
✅ **User Validation**: Refresh checks if user is still active  

## Benefits

1. **Better Security**: Short-lived access tokens limit exposure if stolen
2. **Better UX**: Users don't need to re-login every 30 minutes
3. **Revocable**: Can logout/revoke refresh tokens
4. **Rotation**: Refresh tokens rotate on each use (prevents reuse if stolen)

## Example Usage

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Login
response = requests.post(f"{BASE_URL}/login", data={
    "username": "testuser",
    "password": "testpassword123"
})
tokens = response.json()
access_token = tokens["access_token"]
refresh_token = tokens["refresh_token"]

# 2. Use access token
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get(f"{BASE_URL}/me", headers=headers)

# 3. When access token expires, refresh it
response = requests.post(f"{BASE_URL}/refresh", json={
    "refresh_token": refresh_token
})
new_tokens = response.json()
access_token = new_tokens["access_token"]  # Use new token
refresh_token = new_tokens["refresh_token"]  # Save new refresh token

# 4. Logout when done
requests.post(f"{BASE_URL}/logout", json={
    "refresh_token": refresh_token
})
```

## Testing

Run the test client to see all functionality:
```bash
python test_client.py
```

This will test:
- Registration
- Login (gets both tokens)
- Using access token
- Refreshing tokens
- Logout
- Trying to use revoked token


