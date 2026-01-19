"""
Full Pipeline Testing Script
Tests the complete workflow:
1. Upload PDF and extract career fields
2. Scrape jobs using career fields and skills
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


def test_pdf_upload(pdf_path: str, token: Optional[str] = None) -> dict:
    """Test PDF upload and career field extraction"""
    print_section("STEP 1: PDF UPLOAD & CAREER FIELD EXTRACTION")
    
    if not Path(pdf_path).exists():
        print(f"❌ Error: PDF file not found: {pdf_path}")
        return None
    
    print(f"📄 Uploading PDF: {pdf_path}")
    
    url = f"{BASE_URL}/extract-text"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': (Path(pdf_path).name, f, 'application/pdf')}
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
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Error: Cannot connect to API at {BASE_URL}")
        print("   Make sure the FastAPI server is running!")
        return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


def test_job_scraping(city: str, max_pages: int = 1) -> dict:
    """Test job scraping endpoint"""
    print_section("STEP 2: JOB SCRAPING")
    
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
                print(f"\n   First 3 jobs from career field search:")
                for i, job in enumerate(jobs_cf[:3], 1):
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
                print(f"\n   First 3 jobs from skills search:")
                for i, job in enumerate(jobs_skills[:3], 1):
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
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Error: Cannot connect to API at {BASE_URL}")
        print("   Make sure the FastAPI server is running!")
        return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


def save_results(pdf_result: dict, jobs_result: dict, output_file: str = "pipeline_test_results.json"):
    """Save test results to JSON file"""
    results = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "pdf_extraction": pdf_result,
        "job_scraping": jobs_result
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Full results saved to: {output_file}")


def main():
    """Main testing function"""
    print_section("FULL PIPELINE TESTING SCRIPT")
    
    # Get PDF path from command line or ask user
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        pdf_path = input("📄 Enter path to PDF file: ").strip()
        if not pdf_path:
            print("❌ PDF path is required!")
            return
    
    # Optional: Get authentication token
    use_auth = input("\n🔐 Use authentication? (y/n, default: n): ").strip().lower()
    token = None
    if use_auth == 'y':
        username = input("   Username: ").strip()
        password = input("   Password: ").strip()
        
        # Try to login
        login_url = f"{BASE_URL}/login"
        try:
            response = requests.post(
                login_url,
                data={"username": username, "password": password}
            )
            if response.status_code == 200:
                token = response.json().get("access_token")
                print("✅ Authentication successful!")
            else:
                print("⚠️  Authentication failed, continuing without auth...")
        except Exception as e:
            print(f"⚠️  Authentication error: {e}, continuing without auth...")
    
    # Step 1: Test PDF upload
    pdf_result = test_pdf_upload(pdf_path, token)
    
    if not pdf_result:
        print("\n❌ PDF upload failed. Cannot continue with job scraping.")
        return
    
    # Wait a bit for database to be updated
    print("\n⏳ Waiting 2 seconds for database to update...")
    time.sleep(2)
    
    # Step 2: Test job scraping
    city = input("\n📍 Enter city for job search (e.g., 'New York', 'London'): ").strip()
    if not city:
        print("❌ City is required!")
        return
    
    max_pages_input = input("📄 Number of pages to scrape (default: 1, max: 3): ").strip()
    try:
        max_pages = min(int(max_pages_input) if max_pages_input else 1, 3)
    except ValueError:
        max_pages = 1
    
    jobs_result = test_job_scraping(city, max_pages)
    
    # Save results
    if pdf_result and jobs_result:
        save_results(pdf_result, jobs_result)
    
    # Summary
    print_section("TEST SUMMARY")
    if pdf_result:
        print("✅ PDF Upload & Extraction: SUCCESS")
    else:
        print("❌ PDF Upload & Extraction: FAILED")
    
    if jobs_result:
        print("✅ Job Scraping: SUCCESS")
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
