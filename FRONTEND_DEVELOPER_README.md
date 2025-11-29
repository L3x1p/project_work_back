# Frontend Developer Guide

Welcome! This document will help you integrate with the backend API.

## 🚀 Quick Start

1. **Server must be running:**
   ```bash
   # Backend developer should run this
   uvicorn main:app --reload
   ```

2. **Base URL:**
   ```
   http://localhost:8000
   ```

3. **Interactive API Docs:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## 📚 Documentation Files

- **`API_DOCUMENTATION.md`** - Complete API reference (READ THIS FIRST!)
- **`QUICK_REFERENCE.md`** - Quick lookup for endpoints
- **`EXAMPLE_REQUESTS.http`** - Example requests for testing

## 🔑 Authentication Flow

### Step-by-Step

1. **User registers:**
   ```javascript
   POST /register
   { username, password }
   ```

2. **User logs in:**
   ```javascript
   POST /login
   // Returns: { access_token, refresh_token }
   ```

3. **Store tokens:**
   ```javascript
   localStorage.setItem('access_token', access_token);
   localStorage.setItem('refresh_token', refresh_token);
   ```

4. **Use access token for protected routes:**
   ```javascript
   GET /me
   Headers: { Authorization: 'Bearer ' + access_token }
   ```

5. **When access token expires (401 error):**
   ```javascript
   POST /refresh
   { refresh_token }
   // Get new tokens, update storage
   ```

6. **User logs out:**
   ```javascript
   POST /logout
   { refresh_token }
   // Clear tokens from storage
   ```

## 💡 Important Notes

### ⚠️ Login Endpoint Uses Form Data

The `/login` endpoint expects `application/x-www-form-urlencoded`, NOT JSON!

```javascript
// ✅ Correct
const formData = new URLSearchParams();
formData.append('username', username);
formData.append('password', password);

fetch('/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: formData
});

// ❌ Wrong
fetch('/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username, password })
});
```

### 🔄 Token Refresh Pattern

Always handle token expiration:

```javascript
async function apiCall(url, options = {}) {
  const token = localStorage.getItem('access_token');
  
  let response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`
    }
  });

  // If token expired, refresh and retry
  if (response.status === 401) {
    await refreshToken();
    // Retry with new token
    const newToken = localStorage.getItem('access_token');
    response = await fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${newToken}`
      }
    });
  }

  return response;
}
```

### 📄 PDF Upload

PDF extraction doesn't require authentication:

```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const response = await fetch('http://localhost:8000/extract-text', {
  method: 'POST',
  body: formData
  // No Content-Type header needed - browser sets it automatically
});
```

## 🛠️ Recommended Setup

### Using Axios (Recommended)

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
});

// Add token to all requests
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auto-refresh on 401
api.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      try {
        await refreshToken();
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
```

### Using Fetch with Helper

```javascript
// api.js
const API_BASE = 'http://localhost:8000';

export async function apiRequest(endpoint, options = {}) {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
  });

  if (response.status === 401) {
    await refreshToken();
    return apiRequest(endpoint, options); // Retry
  }

  return response.json();
}

export async function refreshToken() {
  const refreshToken = localStorage.getItem('refresh_token');
  const response = await fetch(`${API_BASE}/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });

  if (!response.ok) {
    throw new Error('Refresh failed');
  }

  const { access_token, refresh_token } = await response.json();
  localStorage.setItem('access_token', access_token);
  localStorage.setItem('refresh_token', refresh_token);
}
```

## 📦 Example React Hook

```typescript
// useAuth.ts
import { useState, useEffect } from 'react';

export function useAuth() {
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
        setUser(await response.json());
      }
    } catch (error) {
      console.error(error);
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

## 🧪 Testing

### Test Authentication Flow

1. Register a user
2. Login and save tokens
3. Call `/me` with access token
4. Wait 30+ minutes (or manually expire token)
5. Call `/me` again - should get 401
6. Call `/refresh` to get new tokens
7. Call `/me` again - should work

### Test PDF Extraction

1. Select a PDF file
2. Upload to `/extract-text`
3. Check response for extracted text

## 🐛 Common Issues

### CORS Errors
- Make sure server is running
- Check CORS is enabled (it is by default)
- Verify you're using the correct base URL

### 401 Unauthorized
- Token expired → Use `/refresh` endpoint
- Token missing → Add `Authorization` header
- Invalid token → User needs to login again

### Login Not Working
- Make sure you're using `application/x-www-form-urlencoded`
- Check username/password are correct
- Verify server is running

### PDF Upload Fails
- Check file is actually a PDF
- Verify `Content-Type` is `multipart/form-data`
- Don't manually set Content-Type header (browser does it)

## 📞 Need Help?

1. Check `API_DOCUMENTATION.md` for detailed info
2. Use Swagger UI at http://localhost:8000/docs
3. Check browser console for errors
4. Check network tab for request/response details

## ✅ Checklist for Integration

- [ ] Server is running on port 8000
- [ ] Can access http://localhost:8000/docs
- [ ] Register endpoint works
- [ ] Login endpoint works (using form data!)
- [ ] Tokens are stored securely
- [ ] Access token is added to protected requests
- [ ] Token refresh is implemented
- [ ] Logout clears tokens
- [ ] PDF upload works
- [ ] Error handling is implemented

---

**Happy Coding! 🎉**


