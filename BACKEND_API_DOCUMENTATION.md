# Backend API Documentation

## Overview

This is a FastAPI-based backend service that provides user authentication and PDF-based career field analysis using LLM (Large Language Model). The service uses JWT tokens for authentication and integrates with a LLaMA Chat API microservice for career analysis.

**Base URL**: `http://localhost:8000` (default, configurable)

**API Documentation**: Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Table of Contents

1. [Authentication](#authentication)
2. [Endpoints](#endpoints)
3. [Data Models](#data-models)
4. [Career Analysis Flow](#career-analysis-flow)
5. [Error Handling](#error-handling)
6. [Examples](#examples)

---

## Authentication

The API uses JWT (JSON Web Tokens) for authentication with a refresh token mechanism.

### Authentication Flow

1. **Register** → Get user account
2. **Login** → Get `access_token` and `refresh_token`
3. **Use `access_token`** → Include in `Authorization: Bearer <token>` header for protected endpoints
4. **Refresh** → When `access_token` expires, use `refresh_token` to get new tokens
5. **Logout** → Revoke `refresh_token`

### Token Details

- **Access Token**: Short-lived (30 minutes), used for API requests
- **Refresh Token**: Long-lived (7 days), stored in database, used to get new access tokens
- **Token Type**: Always `"bearer"`

### Using Authentication

For protected endpoints, include the access token in the request header:

```
Authorization: Bearer <access_token>
```

---

## Endpoints

### 1. Root Endpoint

**GET** `/`

Get API information and available endpoints.

**Authentication**: Not required

**Response**:
```json
{
  "message": "User Authentication API with Career Field Analysis",
  "endpoints": {
    "register": "POST /register - Register a new user",
    "login": "POST /login - Login and get access/refresh tokens",
    "refresh": "POST /refresh - Get new access token using refresh token",
    "logout": "POST /logout - Revoke refresh token",
    "me": "GET /me - Get current user info (requires authentication)",
    "extract-text": "POST /extract-text - Extract text from PDF and analyze potential career fields using LLM"
  }
}
```

---

### 2. Register User

**POST** `/register`

Register a new user account.

**Authentication**: Not required

**Request Body**:
```json
{
  "username": "john_doe",
  "password": "secure_password123"
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "username": "john_doe",
  "is_active": true
}
```

**Error Responses**:
- `400 Bad Request`: Username already registered
  ```json
  {
    "detail": "Username already registered"
  }
  ```

---

### 3. Login

**POST** `/login`

Authenticate user and get access/refresh tokens.

**Authentication**: Not required

**Request Body** (form-data):
```
username: john_doe
password: secure_password123
```

**Note**: This endpoint uses `application/x-www-form-urlencoded` format (OAuth2PasswordRequestForm).

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "random_refresh_token_string_here",
  "token_type": "bearer"
}
```

**Error Responses**:
- `401 Unauthorized`: Incorrect username or password
  ```json
  {
    "detail": "Incorrect username or password"
  }
  ```

---

### 4. Refresh Token

**POST** `/refresh`

Get a new access token and refresh token using the current refresh token.

**Authentication**: Not required (but requires valid refresh_token)

**Request Body**:
```json
{
  "refresh_token": "random_refresh_token_string_here"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "new_random_refresh_token_string_here",
  "token_type": "bearer"
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or expired refresh token
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

**Note**: The old refresh token is deleted and a new one is issued (token rotation for security).

---

### 5. Logout

**POST** `/logout`

Revoke a refresh token (logout).

**Authentication**: Not required (but requires valid refresh_token)

**Request Body**:
```json
{
  "refresh_token": "random_refresh_token_string_here"
}
```

**Response** (200 OK):
```json
{
  "message": "Successfully logged out"
}
```

---

### 6. Get Current User

**GET** `/me`

Get the current authenticated user's information.

**Authentication**: **Required** (Bearer token)

**Headers**:
```
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
{
  "id": 1,
  "username": "john_doe",
  "is_active": true
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or missing token
  ```json
  {
    "detail": "Could not validate credentials"
  }
  ```

---

### 7. Extract Text and Analyze Career Fields

**POST** `/extract-text`

Upload a PDF file, extract text, and analyze potential career fields using LLM.

**Authentication**: **Optional** (if authenticated, results are saved to database)

**Request**:
- **Content-Type**: `multipart/form-data`
- **Body**: Form data with `file` field containing the PDF file

**Headers** (optional):
```
Authorization: Bearer <access_token>
```

**Request Example** (JavaScript):
```javascript
const formData = new FormData();
formData.append('file', pdfFile);

fetch('http://localhost:8000/extract-text', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + accessToken  // Optional
  },
  body: formData
})
```

**Response** (200 OK):
```json
{
  "filename": "resume.pdf",
  "pages": 2,
  "characters": 1234,
  "career_fields": [
    {
      "field": "Software Engineering",
      "summary": "Strong technical background in programming...",
      "key_skills_mentioned": [
        "Python",
        "JavaScript",
        "React",
        "AWS"
      ]
    },
    {
      "field": "Data Science",
      "summary": "Experience with data analysis and machine learning...",
      "key_skills_mentioned": [
        "Python",
        "Pandas",
        "SQL",
        "Machine Learning"
      ]
    }
  ],
  "overall_summary": "Candidate shows strong technical skills in software development and data science...",
  "saved_to_db": true
}
```

**Response Fields**:
- `filename`: Original PDF filename
- `pages`: Number of pages in the PDF
- `characters`: Number of characters extracted
- `career_fields`: Array of potential career fields (3-5 fields)
  - `field`: Career field name (e.g., "Software Engineering")
  - `summary`: Brief explanation of why this field fits
  - `key_skills_mentioned`: Array of relevant skills
- `overall_summary`: Overall career potential summary
- `saved_to_db`: `true` if user was authenticated and data was saved, `false` otherwise

**Error Responses**:
- `400 Bad Request`: Invalid file type
  ```json
  {
    "detail": "File must be a PDF (application/pdf)"
  }
  ```

- `200 OK` (with error field): LLM processing error
  ```json
  {
    "filename": "resume.pdf",
    "pages": 2,
    "characters": 1234,
    "error": "Cannot connect to LLM service...",
    "career_fields": [],
    "overall_summary": ""
  }
  ```

- `200 OK` (with error field): No text found in PDF
  ```json
  {
    "filename": "resume.pdf",
    "error": "No text found in PDF (might be scanned/image-based)",
    "pages": 2,
    "career_fields": [],
    "overall_summary": ""
  }
  ```

**Important Notes**:
- If user is **authenticated**: Career fields and skills are automatically saved to the database
- If user is **not authenticated**: Analysis is performed but not saved
- Skills are stored without duplicates (same skill for same user is only stored once)
- Processing may take 30-60 seconds depending on PDF size and LLM response time

---

## Data Models

### User Model
```json
{
  "id": 1,
  "username": "john_doe",
  "is_active": true
}
```

### Career Field (from API response)
```json
{
  "field": "Software Engineering",
  "summary": "Brief explanation...",
  "key_skills_mentioned": ["Python", "JavaScript"]
}
```

### Database Models (for reference)

**CareerField** (stored in database when user is authenticated):
- `id`: Integer (primary key)
- `user_id`: Integer (foreign key to users)
- `field_name`: String
- `summary`: String (nullable)
- `created_at`: DateTime

**UserSkill** (stored in database when user is authenticated):
- `id`: Integer (primary key)
- `user_id`: Integer (foreign key to users)
- `career_field_id`: Integer (foreign key to career_fields)
- `skill_name`: String
- `created_at`: DateTime
- **Unique constraint**: `(user_id, skill_name)` - prevents duplicate skills per user

---

## Career Analysis Flow

1. **User uploads PDF** → `/extract-text` endpoint
2. **Backend extracts text** → Using `pdfplumber` library
3. **Text sent to LLM service** → LLaMA Chat API at `http://localhost:8002/chat`
4. **LLM analyzes text** → Returns JSON with career fields and skills
5. **Backend processes response** → Parses JSON, validates structure
6. **If authenticated** → Saves to database:
   - Creates `CareerField` records
   - Creates `UserSkill` records (no duplicates)
7. **Returns response** → Career fields, skills, and summary to frontend

### LLM Service Requirements

The backend requires a LLaMA Chat API service running on `http://localhost:8002` (configurable via `LLAMA_CHAT_API_URL` environment variable).

The LLM service should have:
- `POST /chat` endpoint
- Accepts: `{"message": "...", "temperature": 0.7, "max_tokens": 800, "top_p": 0.9}`
- Returns: `{"response": "...", "session_id": "...", "tokens_used": null}`

See `API_DOCUMENTATION.md` for LLM service details.

---

## Error Handling

### Standard HTTP Status Codes

- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required or invalid credentials
- `500 Internal Server Error`: Server error

### Error Response Format

Most errors return:
```json
{
  "detail": "Error message here"
}
```

Some endpoints (like `/extract-text`) may include additional fields:
```json
{
  "error": "Error message",
  "career_fields": [],
  "overall_summary": ""
}
```

### Common Error Scenarios

1. **Expired Access Token**
   - Status: `401 Unauthorized`
   - Solution: Use `/refresh` endpoint with refresh token

2. **Invalid Refresh Token**
   - Status: `401 Unauthorized`
   - Solution: User must login again

3. **LLM Service Unavailable**
   - Status: `200 OK` (with error field)
   - Error message indicates connection issue
   - Solution: Ensure LLM service is running

4. **PDF Processing Error**
   - Status: `500 Internal Server Error`
   - Solution: Check PDF format, ensure it's not corrupted

---

## Examples

### Complete Authentication Flow (JavaScript)

```javascript
// 1. Register
const registerResponse = await fetch('http://localhost:8000/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'john_doe',
    password: 'secure_password123'
  })
});
const user = await registerResponse.json();

// 2. Login
const loginFormData = new URLSearchParams();
loginFormData.append('username', 'john_doe');
loginFormData.append('password', 'secure_password123');

const loginResponse = await fetch('http://localhost:8000/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: loginFormData
});
const { access_token, refresh_token } = await loginResponse.json();

// 3. Use access token for protected endpoint
const meResponse = await fetch('http://localhost:8000/me', {
  headers: {
    'Authorization': `Bearer ${access_token}`
  }
});
const currentUser = await meResponse.json();

// 4. Upload PDF and analyze career
const formData = new FormData();
formData.append('file', pdfFile);

const analysisResponse = await fetch('http://localhost:8000/extract-text', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`
  },
  body: formData
});
const careerAnalysis = await analysisResponse.json();
console.log(careerAnalysis.career_fields);
```

### Refresh Token Example

```javascript
// When access token expires
const refreshResponse = await fetch('http://localhost:8000/refresh', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    refresh_token: refresh_token
  })
});
const { access_token: newAccessToken, refresh_token: newRefreshToken } = await refreshResponse.json();

// Update tokens
access_token = newAccessToken;
refresh_token = newRefreshToken;
```

### PDF Upload Example (React)

```jsx
import { useState } from 'react';

function PDFUploader({ accessToken }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleUpload = async () => {
    if (!file) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/extract-text', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`
        },
        body: formData
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input
        type="file"
        accept=".pdf"
        onChange={(e) => setFile(e.target.files[0])}
      />
      <button onClick={handleUpload} disabled={loading || !file}>
        {loading ? 'Analyzing...' : 'Analyze Career Fields'}
      </button>
      
      {result && (
        <div>
          <h3>Career Fields Found: {result.career_fields.length}</h3>
          {result.career_fields.map((field, idx) => (
            <div key={idx}>
              <h4>{field.field}</h4>
              <p>{field.summary}</p>
              <p>Skills: {field.key_skills_mentioned.join(', ')}</p>
            </div>
          ))}
          <p>{result.overall_summary}</p>
        </div>
      )}
    </div>
  );
}
```

---

## Configuration

### Environment Variables

- `DATABASE_URL`: PostgreSQL connection string (default: `postgresql://auth_user:Qqwerty1!@localhost:5433/auth_db`)
- `SECRET_KEY`: JWT secret key (default: `your-secret-key-change-this-in-production`)
- `LLAMA_CHAT_API_URL`: LLM service URL (default: `http://localhost:8002`)

### CORS

The API is configured to allow CORS from all origins (`*`). In production, update the CORS settings in `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Testing

### Using Swagger UI

1. Start the server: `uvicorn main:app --reload`
2. Visit `http://localhost:8000/docs`
3. Test endpoints directly from the browser

### Using cURL

```bash
# Register
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass"}'

# Login
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpass"

# Upload PDF
curl -X POST "http://localhost:8000/extract-text" \
  -H "Authorization: Bearer <access_token>" \
  -F "file=@resume.pdf"
```

---

## Notes for Frontend Developers

1. **Token Storage**: Store `access_token` and `refresh_token` securely (e.g., localStorage, sessionStorage, or httpOnly cookies)

2. **Token Refresh**: Implement automatic token refresh when access token expires (check for 401 responses)

3. **File Upload**: Use `FormData` for PDF uploads, not JSON

4. **Loading States**: PDF analysis can take 30-60 seconds, show appropriate loading indicators

5. **Error Handling**: Check for `error` field in `/extract-text` response, not just HTTP status codes

6. **Authentication**: `/extract-text` works without authentication, but data won't be saved. Always include token if available.

7. **Career Fields**: The API returns 3-5 career fields per analysis. Display them in a user-friendly format.

8. **Skills**: Skills are automatically deduplicated in the database, but the API response may show duplicates across different career fields (this is normal).

---

## Support

For issues or questions:
- Check the Swagger UI documentation at `/docs`
- Review error messages in API responses
- Ensure LLM service is running for career analysis to work

---

**Last Updated**: 2024
**API Version**: 1.0.0


