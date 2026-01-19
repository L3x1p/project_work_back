from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.ext.mutable import MutableList
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
from typing import Optional, List
import pdfplumber
from io import BytesIO
import random
from career_summarizer_service import summarize_career_fields
from linkedin_scraper import scrape_jobs

# ============================================
# Configuration
# ============================================

# Database URL - update with your PostgreSQL credentials
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://auth_user:Qqwerty1!@25.22.135.242:5433/auth_db"
)

# JWT Settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7  # Refresh tokens last 7 days

# ============================================
# Database Setup
# ============================================

# Create engine with connection timeout for better error handling
engine = create_engine(
    DATABASE_URL,
    connect_args={"connect_timeout": 10},  # 10 second timeout
    pool_pre_ping=True  # Verify connections before using them
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy User Model
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

# SQLAlchemy Refresh Token Model
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# SQLAlchemy Career Field Model
class CareerField(Base):
    __tablename__ = "career_fields"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # nullable for anonymous uploads
    field_name = Column(String, nullable=False)
    summary = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to skills
    skills = relationship("UserSkill", back_populates="career_field", cascade="all, delete-orphan")

# SQLAlchemy User Skill Model (to store unique skills)
class UserSkill(Base):
    __tablename__ = "user_skills"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # nullable for anonymous uploads
    career_field_id = Column(Integer, ForeignKey("career_fields.id", ondelete="CASCADE"), nullable=True)
    skill_name = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    career_field = relationship("CareerField", back_populates="skills")
    
    # Unique constraint: same skill for same user should not be duplicated
    __table_args__ = (UniqueConstraint("user_id", "skill_name", name="uix_user_skill"),)

# Create tables
Base.metadata.create_all(bind=engine)

# ============================================
# Password Hashing
# ============================================

# Use bcrypt with explicit rounds to avoid version issues
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Explicitly set rounds
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash using bcrypt directly"""
    # Bcrypt has a 72 byte limit, so truncate if necessary
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    # Use bcrypt directly to avoid passlib version issues
    try:
        return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))
    except Exception:
        # Fallback to passlib if direct bcrypt fails
        return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt directly to avoid passlib issues"""
    # Bcrypt has a 72 byte limit, so truncate if necessary
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    # Use bcrypt directly to avoid passlib version issues
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

# ============================================
# JWT Token Functions
# ============================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT refresh token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def generate_refresh_token_string() -> str:
    """Generate a random refresh token string"""
    import secrets
    return secrets.token_urlsafe(32)

# ============================================
# Database Dependency
# ============================================

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================
# Pydantic Models
# ============================================

class UserCreate(BaseModel):
    """Model for user registration"""
    username: str
    password: str

class UserResponse(BaseModel):
    """Model for user response"""
    id: int
    username: str
    is_active: bool
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    """Model for token response"""
    access_token: str
    refresh_token: str
    token_type: str

class TokenRefresh(BaseModel):
    """Model for refresh token request"""
    refresh_token: str

class TokenData(BaseModel):
    """Model for token data"""
    username: Optional[str] = None

# ============================================
# FastAPI App
# ============================================

app = FastAPI(title="User Authentication API", description="Registration and Login endpoints")

# CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", auto_error=False)

# ============================================
# Helper Functions
# ============================================

def get_user_by_username(db: Session, username: str):
    """Get user by username from database"""
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    """Authenticate user by checking username and password"""
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# ============================================
# Endpoints
# ============================================

@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    
    - **username**: Unique username for the user
    - **password**: User's password (will be hashed)
    
    Returns the created user information
    """
    # Check if user already exists
    db_user = get_user_by_username(db, username=user_data.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@app.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Login endpoint
    
    - **username**: User's username
    - **password**: User's password
    
    Returns both access token and refresh token for authentication
    """
    # Authenticate user
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token (short-lived)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # Create refresh token (long-lived, stored in database)
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token_string = generate_refresh_token_string()
    
    # Store refresh token in database
    db_refresh_token = RefreshToken(
        token=refresh_token_string,
        user_id=user.id,
        expires_at=datetime.utcnow() + refresh_token_expires
    )
    db.add(db_refresh_token)
    db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token_string,
        "token_type": "bearer"
    }

@app.post("/refresh", response_model=Token)
async def refresh_token(token_data: TokenRefresh, db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token
    
    - **refresh_token**: The refresh token received during login
    
    Returns a new access token and refresh token
    """
    # Find refresh token in database
    db_refresh_token = db.query(RefreshToken).filter(
        RefreshToken.token == token_data.refresh_token
    ).first()
    
    if not db_refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Check if token is expired
    if db_refresh_token.expires_at < datetime.utcnow():
        # Delete expired token
        db.delete(db_refresh_token)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired"
        )
    
    # Get user
    user = db.query(User).filter(User.id == db_refresh_token.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # Optionally rotate refresh token (delete old, create new)
    # This is a security best practice
    db.delete(db_refresh_token)
    
    # Create new refresh token
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    new_refresh_token_string = generate_refresh_token_string()
    
    db_new_refresh_token = RefreshToken(
        token=new_refresh_token_string,
        user_id=user.id,
        expires_at=datetime.utcnow() + refresh_token_expires
    )
    db.add(db_new_refresh_token)
    db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token_string,
        "token_type": "bearer"
    }

@app.post("/logout")
async def logout(token_data: TokenRefresh, db: Session = Depends(get_db)):
    """
    Logout endpoint - revokes refresh token
    
    - **refresh_token**: The refresh token to revoke
    """
    db_refresh_token = db.query(RefreshToken).filter(
        RefreshToken.token == token_data.refresh_token
    ).first()
    
    if db_refresh_token:
        db.delete(db_refresh_token)
        db.commit()
    
    return {"message": "Successfully logged out"}

@app.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user's information
    
    Requires a valid access token in the Authorization header
    """
    return current_user

@app.post("/extract-text")
async def extract_text(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme)
):
    """
    Extract text from uploaded PDF file and analyze potential career fields using LLM
    
    - **file**: PDF file to extract text from (e.g., resume, CV, bio)
    - **Authorization** (optional): Bearer token for authenticated users
    
    Returns a JSON response with career fields analysis and saves to database
    """
    # Validate file type (check both content_type and filename)
    if file.content_type and file.content_type != "application/pdf":
        # Some browsers might not send content-type, so also check filename
        if not (file.filename and file.filename.lower().endswith('.pdf')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be a PDF (application/pdf)"
            )
    elif file.filename and not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a PDF (.pdf extension required)"
        )
    
    # Try to get user if token is provided (optional authentication)
    current_user = None
    user_id = None
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username:
                current_user = get_user_by_username(db, username=username)
                if current_user:
                    user_id = current_user.id
        except (JWTError, Exception):
            pass  # Continue without authentication
    
    try:
        # Read file content into memory
        contents = await file.read()
        
        # Extract text using pdfplumber (needs BytesIO for in-memory PDF)
        extracted_text = ""
        page_count = 0
        
        with pdfplumber.open(BytesIO(contents)) as pdf:
            page_count = len(pdf.pages)
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    extracted_text += page_text + "\n\n"
        
        # If no text found
        if not extracted_text.strip():
            return JSONResponse(
                status_code=200,
                content={
                    "filename": file.filename,
                    "error": "No text found in PDF (might be scanned/image-based)",
                    "pages": page_count,
                    "career_fields": [],
                    "overall_summary": ""
                }
            )
        
        # Use the career summarizer service to analyze the extracted text
        career_analysis = await summarize_career_fields(extracted_text.strip())
        
        # Check if there was an error in LLM processing
        if "error" in career_analysis and career_analysis["error"]:
            # Return extracted text info along with error
            return JSONResponse(
                status_code=200,
                content={
                    "filename": file.filename,
                    "pages": page_count,
                    "characters": len(extracted_text),
                    "error": career_analysis["error"],
                    "career_fields": career_analysis.get("career_fields", []),
                    "overall_summary": career_analysis.get("overall_summary", "")
                }
            )
        
        # Save career fields and skills to database (only if user is authenticated)
        if user_id:
            try:
                # Collect all unique skills from all career fields
                all_skills = set()
                career_fields_data = career_analysis.get("career_fields", [])
                
                # Save each career field
                for field_data in career_fields_data:
                    field_name = field_data.get("field", "")
                    summary = field_data.get("summary", "")
                    skills = field_data.get("key_skills_mentioned", [])
                    
                    if field_name:
                        # Create or get career field
                        career_field = CareerField(
                            user_id=user_id,
                            field_name=field_name,
                            summary=summary
                        )
                        db.add(career_field)
                        db.flush()  # Get the ID without committing
                        
                        # Add skills for this career field
                        for skill_name in skills:
                            if skill_name and skill_name.strip():
                                skill_name_clean = skill_name.strip()
                                all_skills.add(skill_name_clean)
                                
                                # Check if this skill already exists for this user
                                existing_skill = db.query(UserSkill).filter(
                                    UserSkill.user_id == user_id,
                                    UserSkill.skill_name == skill_name_clean
                                ).first()
                                
                                if not existing_skill:
                                    # Create new skill (no duplicate)
                                    user_skill = UserSkill(
                                        user_id=user_id,
                                        career_field_id=career_field.id,
                                        skill_name=skill_name_clean
                                    )
                                    db.add(user_skill)
                
                db.commit()
            except Exception as db_error:
                db.rollback()
                # Log error but don't fail the request
                print(f"Error saving to database: {str(db_error)}")
        
        # Return career fields analysis with file metadata
        return JSONResponse(
            status_code=200,
            content={
                "filename": file.filename,
                "pages": page_count,
                "characters": len(extracted_text),
                "career_fields": career_analysis.get("career_fields", []),
                "overall_summary": career_analysis.get("overall_summary", ""),
                "saved_to_db": user_id is not None
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing PDF and analyzing career fields: {str(e)}"
        )

@app.get("/scrape-jobs")
async def scrape_jobs_endpoint(
    city: str,
    max_pages: int = 1,
    db: Session = Depends(get_db)
):
    """
    Scrape LinkedIn jobs based on random career field and random skills from database.
    
    - **city**: City name for job search (e.g., "New York", "London", "San Francisco")
    - **max_pages**: Maximum number of pages to scrape (default: 1, max: 3)
    
    Returns jobs found using:
    1. A random career field from database
    2. Random skills from database
    """
    if max_pages > 3:
        max_pages = 3
    if max_pages < 1:
        max_pages = 1
    
    # Get random career field
    career_fields = db.query(CareerField).filter(CareerField.field_name.isnot(None)).all()
    if not career_fields:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No career fields found in database. Please upload PDFs first."
        )
    
    random_career_field = random.choice(career_fields)
    career_field_keywords = random_career_field.field_name
    
    # Get random skills
    all_skills = db.query(UserSkill).filter(UserSkill.skill_name.isnot(None)).all()
    if not all_skills:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No skills found in database. Please upload PDFs first."
        )
    
    # Get 3-5 random skills
    num_skills = min(random.randint(3, 5), len(all_skills))
    random_skills = random.sample(all_skills, num_skills)
    skills_keywords = " ".join([skill.skill_name for skill in random_skills])
    
    # Scrape jobs using career field
    jobs_by_career_field = await scrape_jobs(career_field_keywords, city, max_pages)
    
    # Scrape jobs using skills
    jobs_by_skills = await scrape_jobs(skills_keywords, city, max_pages)
    
    return {
        "city": city,
        "max_pages": max_pages,
        "career_field_search": {
            "career_field": {
                "id": random_career_field.id,
                "field_name": random_career_field.field_name,
                "summary": random_career_field.summary
            },
            "keywords": career_field_keywords,
            "jobs_found": len(jobs_by_career_field),
            "jobs": jobs_by_career_field
        },
        "skills_search": {
            "skills": [{"id": skill.id, "skill_name": skill.skill_name} for skill in random_skills],
            "keywords": skills_keywords,
            "jobs_found": len(jobs_by_skills),
            "jobs": jobs_by_skills
        },
        "total_jobs": len(jobs_by_career_field) + len(jobs_by_skills)
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "User Authentication API with Career Field Analysis",
        "endpoints": {
            "register": "POST /register - Register a new user",
            "login": "POST /login - Login and get access/refresh tokens",
            "refresh": "POST /refresh - Get new access token using refresh token",
            "logout": "POST /logout - Revoke refresh token",
            "me": "GET /me - Get current user info (requires authentication)",
            "extract-text": "POST /extract-text - Extract text from PDF and analyze potential career fields using LLM",
            "scrape-jobs": "GET /scrape-jobs?city=<city>&max_pages=<pages> - Scrape LinkedIn jobs using random career field and skills"
        }
    }

