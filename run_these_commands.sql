-- Copy and paste these commands into your psql prompt (postgres=#)

-- Step 1: Create the database
CREATE DATABASE auth_db;

-- Step 2: Create a user for the application
CREATE USER auth_user WITH PASSWORD 'Qqwerty1!';

-- Step 3: Grant privileges to the user
GRANT ALL PRIVILEGES ON DATABASE auth_db TO auth_user;

-- Step 4: Connect to the new database
\c auth_db

-- Step 5: Grant schema privileges
GRANT ALL ON SCHEMA public TO auth_user;

-- Step 6: Verify everything is set up
\l                    -- List all databases (should see auth_db)
\du                   -- List all users (should see auth_user)
\dt                   -- List tables (will be empty until you run the FastAPI app)

-- Done! Now exit
\q


