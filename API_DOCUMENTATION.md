# Backend API Documentation

**Basee URL:** `http://localhost:8000`  
**API Version:** 1.0  
**Framework:** FastAPI

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Endpoints](#endpoints)
4. [Data Models](#data-models)
5. [Error Handling](#error-handling)
6. [Code Examples](#code-examples)
7. [Interactive Documentation](#interactive-documentation)

---

## Overview

This API provides:
- **User Authentication** (Registration, Login, Token Management)
- **PDF Text Extraction** (Upload PDF, Extract Text)

### Features

- ✅ JWT-based authentication with access & refresh tokens
- ✅ Password hashing (bcrypt)
- ✅ Token rotation on refresh
- ✅ CORS enabled for frontend integration
- ✅ PDF text extraction (no storage, process and return)

### Server Setup

The server runs on `http://localhost:8000` by default.  
**Interactive API Docs:** `http://localhost:8000/docs` (Swagger UI)

---

## Authentication

### Authentication Flow

1. **Register** → Create user account
2. **Login** → Get `access_token` and `refresh_token`
3. **Use Access Token** → Include in `Authorization` header for protected endpoints
4. **Refresh Token** → When access token expires, use refresh token to get new tokens
5. **Logout** → Revoke refresh token

### Token Types

| Token Type | Expiration | Usage | Storage |
|------------|-----------|-------|---------|
| **Access Token** | 30 minutes | API requests | Client-side only |
| **Refresh Token** | 7 days | Get new access tokens | Database (revocable) |

### Token Usage

**Access Token:**
```
Authorization: Bearer <access_token>
```

**Refresh Token:**
Send in request body when calling `/refresh` endpoint.

---

## Endpoints

### 1. Root Endpoint

**GET** `/`

Get API information and available endpoints.

**Request:**
```http
GET / HTTP/1.1
Host: localhost:8000
```

**Response:** `200 OK`
```json
{
  "message": "User Authentication API with PDF Text Extraction",
  "endpoints": {
    "register": "POST /register - Register a new user",
    "login": "POST /login - Login and get access/refresh tokens",
    "refresh": "POST /refresh - Get new access token using refresh token",
    "logout": "POST /logout - Revoke refresh token",
    "me": "GET /me - Get current user info (requires authentication)",
    "extract-text": "POST /extract-text - Extract text from PDF file"
  }
}
```

---

### 2. Register User

**POST** `/register`

Register a new user account.

**Request:**
```http
POST /register HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "username": "john_doe",
  "password": "securepassword123"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "username": "john_doe",
  "is_active": true
}
```

**Error Responses:**

`400 Bad Request` - Username already exists
```json
{
  "detail": "Username already registered"
}
```

**Notes:**
- Username must be unique
- Password is automatically hashed (bcrypt)
- User is created with `is_active: true`

---

### 3. Login

**POST** `/login`

Authenticate user and get access/refresh tokens.

**Request:**
```http
POST /login HTTP/1.1
Host: localhost:8000
Content-Type: application/x-www-form-urlencoded

username=john_doe&password=securepassword123
```

**Note:** This endpoint uses `application/x-www-form-urlencoded`, not JSON!

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huX2RvZSIsImV4cCI6MTc2NDQzODU1NSwidHlwZSI6ImFjY2VzcyJ9...",
  "refresh_token": "vPLpPXdOYR3gk3YT9xtF29IO9n-ZttndRCVur-X3jO8",
  "token_type": "bearer"
}
```

**Error Responses:**

`401 Unauthorized` - Invalid credentials
```json
{
  "detail": "Incorrect username or password"
}
```

**Important:**
- Store both tokens securely (localStorage, sessionStorage, or secure cookies)
- Access token expires in 30 minutes
- Refresh token expires in 7 days
- Use refresh token to get new access tokens when needed

---

### 4. Refresh Token

**POST** `/refresh`

Get new access and refresh tokens using a valid refresh token.

**Request:**
```http
POST /refresh HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "refresh_token": "vPLpPXdOYR3gk3YT9xtF29IO9n-ZttndRCVur-X3jO8"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "BFYIKNo5NTGkoHTvj9x0HUbrRz54ZAvylhWMnw3shck",
  "token_type": "bearer"
}
```

**Error Responses:**

`401 Unauthorized` - Invalid or expired refresh token
```json
{
  "detail": "Invalid refresh token"
}
```

or

```json
{
  "detail": "Refresh token has expired"
}
```

**Important:**
- **Token Rotation:** The old refresh token is automatically deleted
- **Always save the new refresh token** - the old one won't work anymore
- Use this endpoint when access token expires (401 response)

---

### 5. Logout

**POST** `/logout`

Revoke a refresh token (logout user).

**Request:**
```http
POST /logout HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "refresh_token": "vPLpPXdOYR3gk3YT9xtF29IO9n-ZttndRCVur-X3jO8"
}
```

**Response:** `200 OK`
```json
{
  "message": "Successfully logged out"
}
```

**Notes:**
- This revokes the refresh token (can't be used again)
- Access tokens remain valid until they expire
- Call this when user explicitly logs out

---

### 6. Get Current User

**GET** `/me`

Get information about the currently authenticated user.

**Request:**
```http
GET /me HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "username": "john_doe",
  "is_active": true
}
```

**Error Responses:**

`401 Unauthorized` - Invalid or missing token
```json
{
  "detail": "Could not validate credentials"
}
```

or

```json
{
  "detail": "Not authenticated"
}
```

**Notes:**
- Requires valid access token in `Authorization` header
- Use this to verify token validity and get user info

---

### 7. Extract PDF Text

**POST** `/extract-text`

Extract text content from a PDF file. No authentication required.

**Request:**
```http
POST /extract-text HTTP/1.1
Host: localhost:8000
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="document.pdf"
Content-Type: application/pdf

[PDF file binary data]
------WebKitFormBoundary--
```

**Response:** `200 OK`
```json
{
  "filename": "document.pdf",
  "text": "Extracted text content from the PDF...",
  "pages": 5,
  "characters": 1234
}
```

**Response (No text found):** `200 OK`
```json
{
  "filename": "document.pdf",
  "text": "",
  "message": "No text found in PDF (might be scanned/image-based)",
  "pages": 3
}
```

**Error Responses:**

`400 Bad Request` - Invalid file type
```json
{
  "detail": "File must be a PDF (application/pdf)"
}
```

`500 Internal Server Error` - Processing error
```json
{
  "detail": "Error extracting text from PDF: [error details]"
}
```

**Notes:**
- File is processed in memory (not stored)
- Maximum file size depends on server configuration
- Scanned PDFs (image-based) won't have extractable text
- Returns empty text if PDF contains only images

---

## Data Models

### UserCreate

Request model for user registration.

```typescript
interface UserCreate {
  username: string;  // Required, unique
  password: string;   // Required
}
```

### UserResponse

Response model for user information.

```typescript
interface UserResponse {
  id: number;
  username: string;
  is_active: boolean;
}
```

### Token

Response model for login/refresh endpoints.

```typescript
interface Token {
  access_token: string;
  refresh_token: string;
  token_type: "bearer";
}
```

### TokenRefresh

Request model for refresh/logout endpoints.

```typescript
interface TokenRefresh {
  refresh_token: string;
}
```

### PDFExtractResponse

Response model for PDF extraction.

```typescript
interface PDFExtractResponse {
  filename: string;
  text: string;
  pages: number;
  characters: number;
}
```

### ErrorResponse

Standard error response format.

```typescript
interface ErrorResponse {
  detail: string;
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | When It Occurs |
|------|---------|----------------|
| `200` | OK | Successful request |
| `201` | Created | User successfully registered |
| `400` | Bad Request | Invalid input, validation error |
| `401` | Unauthorized | Invalid/missing token, wrong credentials |
| `404` | Not Found | Resource not found |
| `500` | Internal Server Error | Server error |

### Error Response Format

All errors follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Error Scenarios

#### 1. Invalid Credentials
```json
{
  "detail": "Incorrect username or password"
}
```

#### 2. Token Expired
```json
{
  "detail": "Could not validate credentials"
}
```
**Solution:** Use `/refresh` endpoint to get new tokens.

#### 3. Missing Token
```json
{
  "detail": "Not authenticated"
}
```
**Solution:** Include `Authorization: Bearer <token>` header.

#### 4. Username Already Exists
```json
{
  "detail": "Username already registered"
}
```

#### 5. Invalid File Type
```json
{
  "detail": "File must be a PDF (application/pdf)"
}
```

---

## Code Examples

### JavaScript/TypeScript (Fetch API)

#### Register User
```javascript
async function register(username, password) {
  const response = await fetch('http://localhost:8000/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      username,
      password,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }

  return await response.json();
}
```

#### Login
```javascript
async function login(username, password) {
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);

  const response = await fetch('http://localhost:8000/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }

  const tokens = await response.json();
  
  // Store tokens securely
  localStorage.setItem('access_token', tokens.access_token);
  localStorage.setItem('refresh_token', tokens.refresh_token);
  
  return tokens;
}
```

#### Get Current User (Authenticated)
```javascript
async function getCurrentUser() {
  const accessToken = localStorage.getItem('access_token');
  
  const response = await fetch('http://localhost:8000/me', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
    },
  });

  if (response.status === 401) {
    // Token expired, try to refresh
    await refreshAccessToken();
    return getCurrentUser(); // Retry
  }

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }

  return await response.json();
}
```

#### Refresh Token
```javascript
async function refreshAccessToken() {
  const refreshToken = localStorage.getItem('refresh_token');
  
  const response = await fetch('http://localhost:8000/refresh', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      refresh_token: refreshToken,
    }),
  });

  if (!response.ok) {
    // Refresh token expired, user needs to login again
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    throw new Error('Session expired. Please login again.');
  }

  const tokens = await response.json();
  
  // Update stored tokens
  localStorage.setItem('access_token', tokens.access_token);
  localStorage.setItem('refresh_token', tokens.refresh_token);
  
  return tokens;
}
```

#### Logout
```javascript
async function logout() {
  const refreshToken = localStorage.getItem('refresh_token');
  
  await fetch('http://localhost:8000/logout', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      refresh_token: refreshToken,
    }),
  });

  // Clear tokens
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
}
```

#### Extract PDF Text
```javascript
async function extractPDFText(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch('http://localhost:8000/extract-text', {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }

  return await response.json();
}

// Usage
const fileInput = document.querySelector('input[type="file"]');
fileInput.addEventListener('change', async (e) => {
  const file = e.target.files[0];
  if (file) {
    try {
      const result = await extractPDFText(file);
      console.log('Extracted text:', result.text);
      console.log('Pages:', result.pages);
    } catch (error) {
      console.error('Error:', error.message);
    }
  }
});
```

### Axios Example

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token refresh on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      try {
        await refreshAccessToken();
        // Retry original request
        return api.request(error.config);
      } catch {
        // Redirect to login
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Register
await api.post('/register', { username, password });

// Login
const formData = new URLSearchParams();
formData.append('username', username);
formData.append('password', password);
const { data } = await api.post('/login', formData, {
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
});

// Get current user
const { data: user } = await api.get('/me');

// Extract PDF
const formData = new FormData();
formData.append('file', file);
const { data: pdfData } = await api.post('/extract-text', formData);
```

### React Hook Example

```typescript
import { useState, useEffect } from 'react';

function useAuth() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      setLoading(false);
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/me', {
        headers: { 'Authorization': `Bearer ${token}` },
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      } else {
        // Try refresh
        await refreshToken();
      }
    } catch (error) {
      console.error('Auth check failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const login = async (username: string, password: string) => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const response = await fetch('http://localhost:8000/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData,
    });

    if (!response.ok) throw new Error('Login failed');

    const tokens = await response.json();
    localStorage.setItem('access_token', tokens.access_token);
    localStorage.setItem('refresh_token', tokens.refresh_token);
    
    await checkAuth();
  };

  const logout = async () => {
    const refreshToken = localStorage.getItem('refresh_token');
    if (refreshToken) {
      await fetch('http://localhost:8000/logout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
    }

    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
  };

  return { user, loading, login, logout };
}
```

---

## Interactive Documentation

FastAPI automatically generates interactive API documentation:

### Swagger UI
Visit: `http://localhost:8000/docs`

- Test all endpoints directly in the browser
- See request/response schemas
- Try out authentication flows

### ReDoc
Visit: `http://localhost:8000/redoc`

- Alternative documentation format
- Clean, readable interface

---

## CORS Configuration

The API has CORS enabled for frontend integration:

```python
# Currently allows all origins (development)
# In production, specify your frontend domain:
allow_origins=["http://localhost:3000", "https://yourdomain.com"]
```

**Current Configuration:**
- ✅ All origins allowed (development)
- ✅ All methods allowed
- ✅ All headers allowed
- ✅ Credentials allowed

---

## Rate Limiting

Currently, there is **no rate limiting** implemented. For production, consider adding:
- Rate limiting per IP
- Rate limiting per user
- Request throttling

---

## Security Notes

### Production Checklist

- [ ] Change `SECRET_KEY` to a secure random value
- [ ] Set `DATABASE_URL` via environment variable
- [ ] Configure CORS to allow only your frontend domain
- [ ] Use HTTPS in production
- [ ] Implement rate limiting
- [ ] Add request validation
- [ ] Set up logging and monitoring
- [ ] Use secure password requirements
- [ ] Implement password reset functionality

### Current Security Features

✅ Passwords hashed with bcrypt  
✅ JWT tokens with expiration  
✅ Token rotation on refresh  
✅ Refresh token revocation  
✅ CORS protection  
✅ Input validation  

---

## Testing

### Test the API

1. **Interactive Testing:** Use Swagger UI at `http://localhost:8000/docs`

2. **Python Test Client:**
   ```bash
   python test_client.py
   ```

3. **PDF Extraction Test:**
   ```bash
   python test_pdf_endpoint.py your-file.pdf
   ```

---

## Support

For issues or questions:
1. Check the interactive docs: `http://localhost:8000/docs`
2. Review error messages in responses
3. Check server logs for detailed errors

---

**Last Updated:** 2024  
**API Version:** 1.0


