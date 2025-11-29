# User Authentication API

FastAPI application with user registration and login endpoints using PostgreSQL and SQLAlchemy.

## Features

- ✅ User registration with username and password
- ✅ User login with JWT token authentication
- ✅ Password hashing using bcrypt
- ✅ Protected endpoints with JWT tokens
- ✅ PostgreSQL database with SQLAlchemy ORM

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Database

Update the `DATABASE_URL` in `main.py` or set it as an environment variable:

```python
DATABASE_URL = "postgresql://username:password@localhost:5432/dbname"
```

Or set environment variable:
```bash
# Windows PowerShell
$env:DATABASE_URL="postgresql://username:password@localhost:5432/dbname"

# Linux/Mac
export DATABASE_URL="postgresql://username:password@localhost:5432/dbname"
```

### 3. Create PostgreSQL Database

```sql
CREATE DATABASE dbname;
```

### 4. Run the Server

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### 1. Register User
**POST** `/register`

Request body:
```json
{
  "username": "testuser",
  "password": "testpassword123"
}
```

Response:
```json
{
  "id": 1,
  "username": "testuser",
  "is_active": true
}
```

### 2. Login
**POST** `/login`

Request body (form data):
```
username: testuser
password: testpassword123
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Get Current User
**GET** `/me`

Headers:
```
Authorization: Bearer <access_token>
```

Response:
```json
{
  "id": 1,
  "username": "testuser",
  "is_active": true
}
```

## Testing

Run the test client:
```bash
python test_client.py
```

## Interactive API Documentation

Visit `http://localhost:8000/docs` for Swagger UI documentation.

## Security Notes

- Passwords are hashed using bcrypt before storage
- JWT tokens expire after 30 minutes (configurable)
- Change `SECRET_KEY` in production
- Use environment variables for sensitive data


