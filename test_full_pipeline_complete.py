"""
Complete Full Pipeline Test
Tests: User Registration → Login → PDF Upload → Career Analysis → Job Scraping
"""
import sys
import json
import requests
import time
from pathlib import Path
from typing import Optional

# API base URL
BASE_URL = "http://localhost:8000"  # Change if your API runs on different port


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_subsection(title: str):
    """Print a formatted subsection header"""
    print("\n" + "-" * 80)
    print(f"  {title}")
    print("-" * 80 + "\n")


def test_user_registration(username: str, password: str) -> Optional[dict]:
    """Test user registration"""
    print_section("STEP 1: USER REGISTRATION")
    
    print(f"📝 Registering new user...")
    print(f"   Username: {username}")
    
    url = f"{BASE_URL}/register"
    payload = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 201:
            data = response.json()
            print("✅ User registered successfully!")
            print(f"   User ID: {data.get('id', 'N/A')}")
            print(f"   Username: {data.get('username', 'N/A')}")
            print(f"   Active: {data.get('is_active', 'N/A')}")
            return data
        elif response.status_code == 400:
            error_data = response.json()
            if "already registered" in error_data.get('detail', '').lower():
                print("⚠️  User already exists, continuing with login...")
                return None
            else:
                print(f"❌ Registration failed: {error_data.get('detail', 'Unknown error')}")
                return None
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Error: Cannot connect to API at {BASE_URL}")
        print("   Make sure the FastAPI server is running!")
        return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


def test_user_login(username: str, password: str) -> Optional[str]:
    """Test user login and get access token"""
    print_section("STEP 2: USER LOGIN")
    
    print(f"🔐 Logging in...")
    print(f"   Username: {username}")
    
    url = f"{BASE_URL}/login"
    data = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            refresh_token = token_data.get("refresh_token")
            
            print("✅ Login successful!")
            print(f"   Access Token: {access_token[:50]}...")
            print(f"   Refresh Token: {refresh_token[:50]}...")
            return access_token
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


def test_pdf_upload(pdf_path: str, token: str) -> Optional[dict]:
    """Test PDF upload and career field extraction"""
    print_section("STEP 3: PDF UPLOAD & CAREER ANALYSIS")
    
    if not Path(pdf_path).exists():
        print(f"❌ Error: PDF file not found: {pdf_path}")
        return None
    
    print(f"📄 Uploading PDF: {pdf_path}")
    
    url = f"{BASE_URL}/extract-text"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': (Path(pdf_path).name, f, 'application/pdf')}
            print("⏳ Processing PDF and analyzing career fields... (this may take 30-60 seconds)")
            response = requests.post(url, files=files, headers=headers, timeout=120)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ PDF uploaded and processed successfully!")
            print(f"\n📊 Results:")
            print(f"   - Filename: {data.get('filename', 'N/A')}")
            print(f"   - Pages: {data.get('pages', 0)}")
            print(f"   - Characters: {data.get('characters', 0)}")
            print(f"   - Saved to DB: {data.get('saved_to_db', False)}")
            
            career_fields = data.get('career_fields', [])
            print(f"   - Career Fields Found: {len(career_fields)}")
            
            if career_fields:
                print("\n💼 Career Fields:")
                for i, field in enumerate(career_fields, 1):
                    print(f"   {i}. {field.get('field', 'N/A')}")
                    print(f"      Summary: {field.get('summary', 'N/A')[:100]}...")
                    skills = field.get('key_skills_mentioned', [])
                    if skills:
                        print(f"      Skills: {', '.join(skills[:5])}")
            
            overall_summary = data.get('overall_summary', '')
            if overall_summary:
                print(f"\n📝 Overall Summary: {overall_summary[:200]}...")
            
            if 'error' in data and data['error']:
                print(f"\n⚠️  Warning: {data['error']}")
            
            return data
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


def test_job_scraping(city: str, max_pages: int = 1) -> Optional[dict]:
    """Test job scraping endpoint"""
    print_section("STEP 4: JOB SCRAPING")
    
    print(f"🔍 Scraping jobs for city: {city}")
    print(f"📄 Max pages: {max_pages}")
    print("\n⏳ This may take a while (30-60 seconds)...")
    
    url = f"{BASE_URL}/scrape-jobs"
    params = {
        "city": city,
        "max_pages": max_pages
    }
    
    try:
        start_time = time.time()
        response = requests.get(url, params=params, timeout=120)
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Job scraping completed in {elapsed_time:.2f} seconds!")
            
            print(f"\n📊 Results:")
            print(f"   - City: {data.get('city', 'N/A')}")
            print(f"   - Total Jobs Found: {data.get('total_jobs', 0)}")
            
            # Career field search results
            career_field_search = data.get('career_field_search', {})
            print(f"\n💼 Career Field Search:")
            career_field = career_field_search.get('career_field', {})
            print(f"   - Career Field: {career_field.get('field_name', 'N/A')}")
            print(f"   - Keywords: {career_field_search.get('keywords', 'N/A')}")
            print(f"   - Jobs Found: {career_field_search.get('jobs_found', 0)}")
            
            jobs_cf = career_field_search.get('jobs', [])
            if jobs_cf:
                print(f"\n   First 5 jobs from career field search:")
                for i, job in enumerate(jobs_cf[:5], 1):
                    print(f"   {i}. {job.get('title', 'N/A')}")
                    print(f"      Company: {job.get('company', 'N/A')}")
                    print(f"      Location: {job.get('location', 'N/A')}")
            
            # Skills search results
            skills_search = data.get('skills_search', {})
            print(f"\n🛠️  Skills Search:")
            skills = skills_search.get('skills', [])
            print(f"   - Skills Used: {', '.join([s.get('skill_name', '') for s in skills])}")
            print(f"   - Keywords: {skills_search.get('keywords', 'N/A')}")
            print(f"   - Jobs Found: {skills_search.get('jobs_found', 0)}")
            
            jobs_skills = skills_search.get('jobs', [])
            if jobs_skills:
                print(f"\n   First 5 jobs from skills search:")
                for i, job in enumerate(jobs_skills[:5], 1):
                    print(f"   {i}. {job.get('title', 'N/A')}")
                    print(f"      Company: {job.get('company', 'N/A')}")
                    print(f"      Location: {job.get('location', 'N/A')}")
            
            return data
        elif response.status_code == 404:
            error_data = response.json()
            print(f"❌ Error: {error_data.get('detail', 'No data found in database')}")
            print("   Please upload PDFs first to generate career fields and skills!")
            return None
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


def save_results(results: dict, output_file: str = "full_pipeline_test_results.json"):
    """Save test results to JSON file"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Full results saved to: {output_file}")


def main():
    """Main testing function"""
    print_section("COMPLETE FULL PIPELINE TEST")
    print("This test covers:")
    print("  1. User Registration")
    print("  2. User Login")
    print("  3. PDF Upload & Career Analysis")
    print("  4. Job Scraping")
    print()
    
    # Get PDF path from command line or ask user
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        pdf_path = input("📄 Enter path to PDF file (resume/CV): ").strip()
        if not pdf_path:
            print("❌ PDF path is required!")
            return
    
    # Generate unique username
    import random
    username = f"test_user_{random.randint(1000, 9999)}"
    password = "test123"  # Short password to avoid bcrypt 72-byte limit
    
    print(f"\n📋 Test Configuration:")
    print(f"   Username: {username}")
    print(f"   Password: {password}")
    print(f"   PDF: {pdf_path}")
    
    results = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "username": username,
        "steps": {}
    }
    
    # Step 1: Register user
    user_data = test_user_registration(username, password)
    results["steps"]["registration"] = user_data if user_data else "skipped (user exists)"
    
    # Step 2: Login
    token = test_user_login(username, password)
    if not token:
        print("\n❌ Login failed. Cannot continue with PDF upload.")
        return
    results["steps"]["login"] = "success"
    
    # Step 3: Upload PDF
    pdf_result = test_pdf_upload(pdf_path, token)
    if not pdf_result:
        print("\n❌ PDF upload failed. Cannot continue with job scraping.")
        return
    results["steps"]["pdf_upload"] = pdf_result
    
    # Wait for database to update
    print("\n⏳ Waiting 3 seconds for database to update...")
    time.sleep(3)
    
    # Step 4: Scrape jobs
    city = input("\n📍 Enter city for job search (e.g., 'London', 'New York'): ").strip()
    if not city:
        print("❌ City is required!")
        return
    
    max_pages_input = input("📄 Number of pages to scrape (default: 1, max: 3): ").strip()
    try:
        max_pages = min(int(max_pages_input) if max_pages_input else 1, 3)
    except ValueError:
        max_pages = 1
    
    jobs_result = test_job_scraping(city, max_pages)
    results["steps"]["job_scraping"] = jobs_result if jobs_result else "failed"
    
    # Save results
    save_results(results)
    
    # Final summary
    print_section("TEST SUMMARY")
    
    if user_data or results["steps"]["registration"] == "skipped (user exists)":
        print("✅ User Registration: SUCCESS")
    else:
        print("❌ User Registration: FAILED")
    
    if token:
        print("✅ User Login: SUCCESS")
    else:
        print("❌ User Login: FAILED")
    
    if pdf_result:
        print("✅ PDF Upload & Analysis: SUCCESS")
        print(f"   Found {len(pdf_result.get('career_fields', []))} career fields")
    else:
        print("❌ PDF Upload & Analysis: FAILED")
    
    if jobs_result:
        print("✅ Job Scraping: SUCCESS")
        print(f"   Found {jobs_result.get('total_jobs', 0)} total jobs")
    else:
        print("❌ Job Scraping: FAILED")
    
    print("\n" + "=" * 80)
    print("Testing completed!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user.")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
