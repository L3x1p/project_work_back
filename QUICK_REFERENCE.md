# API Quick Reference

## Base URL
```
http://localhost:8000
```

## Authentication Endpoints

### Register
```bash
POST /register
Content-Type: application/json

{
  "username": "user123",
  "password": "password123"
}
```

### Login
```bash
POST /login
Content-Type: application/x-www-form-urlencoded

username=user123&password=password123
```

**Response:**
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer"
}
```

### Refresh Token
```bash
POST /refresh
Content-Type: application/json

{
  "refresh_token": "..."
}
```

### Logout
```bash
POST /logout
Content-Type: application/json

{
  "refresh_token": "..."
}
```

### Get Current User
```bash
GET /me
Authorization: Bearer <access_token>
```

## PDF Extraction

### Extract Text
```bash
POST /extract-text
Content-Type: multipart/form-data

file: [PDF file]
```

## cURL Examples

### Register
```bash
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass"}'
```

### Login
```bash
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpass"
```

### Get Current User
```bash
curl -X GET "http://localhost:8000/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Refresh Token
```bash
curl -X POST "http://localhost:8000/refresh" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"YOUR_REFRESH_TOKEN"}'
```

### Extract PDF Text
```bash
curl -X POST "http://localhost:8000/extract-text" \
  -F "file=@document.pdf"
```

## JavaScript Quick Examples

### Login & Store Tokens
```javascript
const formData = new URLSearchParams();
formData.append('username', 'user123');
formData.append('password', 'pass123');

const response = await fetch('http://localhost:8000/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: formData
});

const { access_token, refresh_token } = await response.json();
localStorage.setItem('access_token', access_token);
localStorage.setItem('refresh_token', refresh_token);
```

### Authenticated Request
```javascript
const token = localStorage.getItem('access_token');

const response = await fetch('http://localhost:8000/me', {
  headers: { 'Authorization': `Bearer ${token}` }
});

const user = await response.json();
```

### Extract PDF
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const response = await fetch('http://localhost:8000/extract-text', {
  method: 'POST',
  body: formData
});

const { text, pages } = await response.json();
```

## Error Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 500 | Server Error |

## Token Expiration

- **Access Token:** 30 minutes
- **Refresh Token:** 7 days

## Common Patterns

### Auto-refresh on 401
```javascript
async function apiCall(url, options = {}) {
  let response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`
    }
  });

  if (response.status === 401) {
    // Refresh token
    await refreshToken();
    // Retry
    response = await fetch(url, options);
  }

  return response;
}
```

### Request Interceptor (Axios)
```javascript
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```


