-- PostgreSQL Database Setup Script
-- Run this as postgres superuser: psql -U postgres -f setup_database.sql

-- Step 1: Create database
CREATE DATABASE auth_db;

-- Step 2: Create user (optional - you can use postgres user instead)
CREATE USER auth_user WITH PASSWORD 'change_this_password';

-- Step 3: Grant privileges
GRANT ALL PRIVILEGES ON DATABASE auth_db TO auth_user;

-- Step 4: Connect to the database
\c auth_db

-- Step 5: Grant schema privileges
GRANT ALL ON SCHEMA public TO auth_user;

-- Step 6: The 'users' table will be created automatically by SQLAlchemy
-- when you run the FastAPI app. Structure will be:
-- 
-- CREATE TABLE users (
--     id SERIAL PRIMARY KEY,
--     username VARCHAR UNIQUE NOT NULL,
--     hashed_password VARCHAR NOT NULL,
--     is_active BOOLEAN DEFAULT TRUE
-- );

-- Done! Now update DATABASE_URL in main.py to:
-- postgresql://auth_user:change_this_password@localhost:5432/auth_db


