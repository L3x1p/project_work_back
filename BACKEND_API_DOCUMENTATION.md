# Backend API Documentation

**Base URL**: `http://localhost:8000`

**API Docs**: `http://localhost:8000/docs` (Swagger UI)

---

## Complete Pipeline Flow

1. **User Registration** → Create account
2. **User Login** → Get access token
3. **Upload PDF (CV/Resume)** → Extract career fields & skills
4. **Scrape Jobs** → Get job recommendations based on career fields & skills

---

## Endpoints

### 1. Register User

**POST** `/register`

**Request:**
```json
{
  "username": "john_doe",
  "password": "password123"
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

---

### 2. Login

**POST** `/login`

**Request:** (form-data)
```
username: john_doe
password: password123
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "random_token_string",
  "token_type": "bearer"
}
```

**Use `access_token` in Authorization header for protected endpoints:**
```
Authorization: Bearer <access_token>
```

---

### 3. Upload PDF & Analyze Career Fields

**POST** `/extract-text`

**Headers:**
```
Authorization: Bearer <access_token>  (optional - if provided, saves to DB)
Content-Type: multipart/form-data
```

**Request:** (form-data)
```
file: <PDF file>
```

**Response:** `200 OK`
```json
{
  "filename": "resume.pdf",
  "pages": 2,
  "characters": 1500,
  "saved_to_db": true,
  "career_fields": [
    {
      "field": "Software Engineering",
      "summary": "Experience in developing applications...",
      "key_skills_mentioned": ["Python", "JavaScript", "React"]
    },
    {
      "field": "Data Science",
      "summary": "Strong background in data analysis...",
      "key_skills_mentioned": ["Python", "Pandas", "Machine Learning"]
    }
  ],
  "overall_summary": "Strong technical background with expertise in..."
}
```

**Note:** If `Authorization` header is provided, career fields and skills are automatically saved to database.

---

### 4. Scrape Jobs

**GET** `/scrape-jobs?city=London&max_pages=1`

**Query Parameters:**
- `city` (required): City name (e.g., "London", "New York", "San Francisco")
- `max_pages` (optional): Number of pages to scrape (default: 1, max: 3)

**Response:** `200 OK`
```json
{
  "city": "London",
  "max_pages": 1,
  "total_jobs": 45,
  "career_field_search": {
    "career_field": {
      "id": 1,
      "field_name": "Software Engineering",
      "summary": "Experience in..."
    },
    "keywords": "Software Engineering",
    "jobs_found": 25,
    "jobs": [
      {
        "title": "Senior Software Engineer",
        "urn": "urn:li:fsd_jobPosting:123456",
        "company": "Tech Corp",
        "location": "London, UK",
        "apply_link": "https://www.linkedin.com/jobs/view/123456",
        "description": null,
        "image": null
      }
    ]
  },
  "skills_search": {
    "skills": [
      {"id": 1, "skill_name": "Python"},
      {"id": 2, "skill_name": "JavaScript"}
    ],
    "keywords": "Python JavaScript",
    "jobs_found": 20,
    "jobs": [...]
  }
}
```

**Error:** `404 Not Found` - If no career fields or skills in database
```json
{
  "detail": "No career fields found in database. Please upload PDFs first."
}
```

---

### 5. Refresh Token

**POST** `/refresh`

**Request:**
```json
{
  "refresh_token": "random_token_string"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "new_access_token...",
  "refresh_token": "new_refresh_token...",
  "token_type": "bearer"
}
```

---

### 6. Logout

**POST** `/logout`

**Request:**
```json
{
  "refresh_token": "random_token_string"
}
```

**Response:** `200 OK`
```json
{
  "message": "Successfully logged out"
}
```

---

### 7. Get Current User

**GET** `/me`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "username": "john_doe",
  "is_active": true
}
```

---

## Frontend Implementation Guide

### Complete User Flow

```javascript
// 1. Register
const registerResponse = await fetch('http://localhost:8000/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'john', password: 'pass123' })
});

// 2. Login
const formData = new FormData();
formData.append('username', 'john');
formData.append('password', 'pass123');

const loginResponse = await fetch('http://localhost:8000/login', {
  method: 'POST',
  body: formData
});
const { access_token, refresh_token } = await loginResponse.json();

// 3. Upload PDF
const pdfFormData = new FormData();
pdfFormData.append('file', pdfFile);

const uploadResponse = await fetch('http://localhost:8000/extract-text', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${access_token}` },
  body: pdfFormData
});
const careerData = await uploadResponse.json();

// 4. Scrape Jobs
const jobsResponse = await fetch(
  'http://localhost:8000/scrape-jobs?city=London&max_pages=1',
  {
    headers: { 'Authorization': `Bearer ${access_token}` }
  }
);
const jobsData = await jobsResponse.json();
```

---

## Error Responses

**400 Bad Request** - Invalid input
```json
{
  "detail": "Username already registered"
}
```

**401 Unauthorized** - Invalid/missing token
```json
{
  "detail": "Could not validate credentials"
}
```

**404 Not Found** - Resource not found
```json
{
  "detail": "No career fields found in database. Please upload PDFs first."
}
```

**500 Internal Server Error** - Server error
```json
{
  "detail": "Error processing PDF..."
}
```

---

## Important Notes

- **Access tokens expire in 30 minutes** - Use refresh token to get new ones
- **PDF upload requires authentication** to save data to database
- **Job scraping** uses random career fields/skills from database - upload PDFs first
- **CORS is enabled** - Frontend can call API from any origin
- **PDF processing takes 30-60 seconds** - Show loading indicator

---

## Data Models

### Career Field
```json
{
  "field": "Software Engineering",
  "summary": "Brief explanation...",
  "key_skills_mentioned": ["Python", "JavaScript"]
}
```

### Job
```json
{
  "title": "Software Engineer",
  "company": "Tech Corp",
  "location": "London, UK",
  "apply_link": "https://...",
  "urn": "urn:li:fsd_jobPosting:123456"
}
```

---

## Testing

Test the complete pipeline:
```bash
python test_full_pipeline_complete.py your_resume.pdf
```
