"""
Script to scrape LinkedIn jobs based on a random user's skills from the database.
Takes random user's skills, asks for location, and scrapes matching jobs.
"""
import os
import sys
import json
import urllib.parse
import aiohttp
import asyncio
import random
from typing import Optional, Dict, List, Tuple
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import User, UserSkill

# Database URL - same as in main.py
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://auth_user:Qqwerty1!@25.22.135.242:5433/auth_db"
)

# LinkedIn API credentials
csrtToken = "ajax:2512664078070293346"
cookie = 'bcookie="v=2&97296263-ab2d-4b3c-82fd-e322862d1a48"; bscookie="v=1&20251125165721e37c5d63-5894-4256-8309-e9145077a431AQEj96LPfeh-eeXiuQLRkP-S9_7QOxQN"; li_gc=MTswOzE3NjQwODk4NDE7MjswMjF9SejEHT/ZqpDYCK1Gjhv+xxv7DKt1aILcWqdoQawm4A==; fid=AQH-xqfWSnOdTgAAAZrAinPDZlThqddHTtlVmWrDfsyJem6PfRLqt2QsVOmORwgViUTbzoqRl3sIsA; li_alerts=e30=; JSESSIONID="ajax:2512664078070293346"; timezone=Europe/Berlin; li_theme=light; li_theme_set=app; _pxvid=348c6dcd-cad3-11f0-8c69-1073da85626d; dfpfpt=a25359227189422c9c59a5ed65c60321; sdui_ver=sdui-flagship:0.1.20962+SduiFlagship0; li_sugr=763bce5e-b32c-46d7-a358-33ed244529e9; s_fid=7B456ECFDAB5C200-185B360A92FDD0A2; s_ips=1305; s_tp=1305; li_at=AQEDAT_4KeUDzgyKAAABmsDBW0gAAAGa5M3fSE4AH0YJLZKAO2PwqBKc1rDZaqvls2_QOh-8_sTeniX1MugZN6jr5WG6WdY22f4Tw03jtVWVvzzBQwgBE5FzfMSWocD2jZdZ06B0NxXQKyqUjN0exLp7; liap=true; gpv_pn=www.linkedin.com%2Fself-serve-checkout%2Fpurchase-multi-seats%2Fid-redacted; s_tslv=1764170524908; UserMatchHistory=AQI9Cyw2zqLPRQAAAZrQknBDnqwfOK5jfbgnq6XayWvnQYW7NAmVzEs40Dk3aygPkv7dmjvShgRDbA; AnalyticsSyncHistory=AQJyDbIid_UfqAAAAZrQknBDwsl7fq-juTsq4wSJdsyeLYdX15A16SlPSigj2KaYb2GAXS1LL9AGsneLDzvWBQ; lms_ads=AQF-0JOyMr2NSAAAAZrQknFUjNMzQspzFyypZWMABoeNCYXSWsbXufTyZKAGqpEtjKAsW5uYfVRqyWOzeQoJhIdzHkLigB9m; lms_analytics=AQF-0JOyMr2NSAAAAZrQknFUjNMzQspzFyypZWMABoeNCYXSWsbXufTyZKAGqpEtjKAsW5uYfVRqyWOzeQoJhIdzHkLigB9m; lidc="b=TB61:s=T:r=T:a=T:p=T:g=5257:u=229:x=1:i=1764524144:t=1764604395:v=2:sig=AQEioN6PYuy0pdV5ZoyS9VIK-q6qQnLK"; lang=v=2&lang=ru-ru; fptctx2=taBcrIH61PuCVH7eNCyH0B9zcK90d%252bIeoo1r5v7Zc26fsakuivt53U%252fQilJw5R13u54ST0vZrMf4bazCAaXYBHsSxAjcwae1RrK2OWmIpQGLrJffL%252fVMld9xqmUxlbuFW%252bh6P4qKA64ppqTpzBBlEwKyBJr2hVica%252bHgUkwCP26j%252f%252fx8V2ezeIxvJqpoOhad4K1WVsGw0BFfrorrl%252bO9Mo4S9Ut1RKf1NZTQMWTjEiN8%252bOc33o%252bG0HR3w7Am6QKspQj%252f2rArMaU5yN%252b0VDmqli22A8jqIBde2SAfoxDxLfi8uLGF6fDieA%252fKS2USCWTX9Nw1q7x62zdlodheCl4iCkN9wwKMhrUSeyhtFhbCrGw%253d; li_mc=MTsyMTsxNzY0NTM0NjUxOzI7MDIxvdzcp4wdCBRTajmbcz0pCteqWqzAe5Ml7wUzS++wmmI=; __cf_bm=kmLX6Qobg4oLfKpeRr6DkmgFoLt2.bGZ0I4TMA9jX3E-1764534651-1.0.1.1-oqzkuIE3PvaBFn0zsUOo33irKpM_3waCmTauU3Cc8sLiMalqWG3IpoWHHDeh5nAvZpHNTgVZyb7KH4T7uMbVSBY8eQldvPI5DoqqR6cwNbk'


async def crawl_linkedin_api(url: str) -> Optional[Dict]:
    """Async function to crawl LinkedIn API"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "Accept": "application/vnd.linkedin.normalized+json+2.1",
        "Referer": "https://www.linkedin.com/search/results/people/?keywords=software%20engineer&origin=GLOBAL_SEARCH_HEADER&sid=crG",
        "csrf-token": csrtToken,
        "Cookie": cookie,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Request failed with status code: {response.status}")
                    return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def isJob(obj):
    """Check if object is a job posting"""
    if (
        "$type" not in obj
        or obj["$type"] != "com.linkedin.voyager.dash.jobs.JobPosting"
    ):
        return False
    return True


async def findPlace(place: str) -> Optional[str]:
    """Async function to find place URN"""
    url = "https://www.linkedin.com/voyager/api/graphql?variables=(keywords:{},query:(typeaheadFilterQuery:(geoSearchTypes:List(POSTCODE_1,POSTCODE_2,POPULATED_PLACE,ADMIN_DIVISION_1,ADMIN_DIVISION_2,COUNTRY_REGION,MARKET_AREA,COUNTRY_CLUSTER)),typeaheadUseCase:JOBS),type:GEO)&queryId=voyagerSearchDashReusableTypeahead.54529a68d290553c6f24e28ab3448654".format(
        place
    )

    data = await crawl_linkedin_api(url)
    if data and "included" in data and data["included"]:
        return data["included"][0]["entityUrn"].split(":")[-1]
    return None


async def getJobData(jobUrn: str) -> Optional[Dict]:
    """Async function to get job details"""
    urn = jobUrn.split(":")[-1]
    url = "https://www.linkedin.com/voyager/api/jobs/jobPostings/{}?decorationId=com.linkedin.voyager.deco.jobs.web.shared.WebFullJobPosting-65&topN=1&topNRequestedFlavors=List(TOP_APPLICANT,IN_NETWORK,COMPANY_RECRUIT,SCHOOL_RECRUIT,HIDDEN_GEM,ACTIVELY_HIRING_COMPANY)".format(
        urn
    )

    data = await crawl_linkedin_api(url)
    if data:
        if "applyMethod" not in data or "companyApplyUrl" not in data.get("applyMethod", {}):
            return {
                "apply_link": data.get("data", {}).get("jobPostingUrl", ""),
                "description": data.get("data", {}).get("description", {}).get("text", ""),
                "image": grabDataFromObj(
                    data.get("included", []),
                    [
                        "com.linkedin.voyager.organization.Company",
                        "com.linkedin.voyager.organization.CompanyLogoImage",
                    ],
                    [
                        ["image", "rootUrl"],
                        ["image", "artifacts", 2, "fileIdentifyingUrlPathSegment"],
                    ],
                ),
            }
        else:
            return {
                "apply_link": data.get("data", {}).get("applyMethod", {}).get("companyApplyUrl", ""),
                "description": data.get("data", {}).get("description", {}).get("text", ""),
                "image": grabDataFromObj(
                    data.get("included", []),
                    [
                        "com.linkedin.voyager.organization.Company",
                        "com.linkedin.voyager.organization.CompanyLogoImage",
                    ],
                    [
                        ["image", "rootUrl"],
                        ["image", "artifacts", 2, "fileIdentifyingUrlPathSegment"],
                    ],
                ),
            }
    return None


def grabDataFromObj(obj, types, indexes):
    """Extract data from nested object structure"""
    currentItem = obj

    # First find the object with the specified type
    for t in types:
        currentItem = searchInside(currentItem, t)
        if currentItem is None:
            return None

    # Then get the values from the specified paths
    values = []
    for index in indexes:
        currentValueItem = currentItem
        for i in index:
            if isinstance(i, int):
                if isinstance(currentValueItem, list) and len(currentValueItem) > i:
                    currentValueItem = currentValueItem[i]
                else:
                    return None
            else:
                if i not in currentValueItem:
                    return None
                currentValueItem = currentValueItem[i]

        if isinstance(currentValueItem, str):
            values.append(currentValueItem)

    # Return None if we didn't get all the required values
    if len(values) != len(indexes):
        return None

    # Combine the values to form the complete URL
    return "".join(values)


def searchInside(obj, t):
    """Search for object with specific type"""
    if isinstance(obj, list):
        for item in obj:
            if "$type" in item and item["$type"] == t:
                return item
    else:
        for key, item in obj.items():
            if isinstance(item, int):
                continue
            if item is not None:
                if "$type" in item and item["$type"] == t:
                    return item

    return None


def get_random_user_skills(db_session, max_skills: int = 5) -> Tuple[Optional[User], List[str]]:
    """Get a random user and their skills from database"""
    # Get all users who have skills
    users_with_skills = db_session.query(User).join(UserSkill).distinct().all()
    
    if not users_with_skills:
        return None, []
    
    # Pick a random user
    random_user = random.choice(users_with_skills)
    
    # Get their skills
    skills = db_session.query(UserSkill).filter(
        UserSkill.user_id == random_user.id
    ).all()
    
    # Get skill names and limit to max_skills
    skill_names = [skill.skill_name for skill in skills[:max_skills]]
    
    return random_user, skill_names


def combine_skills_to_keywords(skills: List[str]) -> str:
    """Combine skills into a search keyword string"""
    # Take first 3-5 skills and combine them
    selected_skills = skills[:5] if len(skills) > 5 else skills
    # Join with spaces for LinkedIn search
    return " ".join(selected_skills)


async def scrape_jobs(keywords: str, place: str, max_pages: int = 3) -> List[Dict]:
    """Scrape LinkedIn jobs based on keywords and location"""
    print(f"\n🔍 Searching for jobs with keywords: '{keywords}'")
    print(f"📍 Location: {place}")
    print(f"📄 Max pages: {max_pages}\n")
    
    # Find place URN
    print("Finding location...")
    place_urn = await findPlace(urllib.parse.quote(place))
    if place_urn is None:
        print(f"❌ Could not find location: {place}")
        return []
    
    print(f"✅ Found location URN: {place_urn}")
    
    jobs = []
    count = 0
    old_count = 0
    page_size = 25
    keywords_encoded = urllib.parse.quote(keywords)
    
    for page in range(max_pages):
        print(f"\n📄 Scraping page {page + 1}/{max_pages}...")
        
        url = "https://www.linkedin.com/voyager/api/voyagerJobsDashJobCards?decorationId=com.linkedin.voyager.dash.deco.jobs.search.JobSearchCardsCollection-218&count={}&q=jobSearch&query=(origin:JOB_SEARCH_PAGE_SEARCH_BUTTON,keywords:{},locationUnion:(geoId:{}),selectedFilters:(distance:List(0)),spellCorrectionEnabled:true)&start={}".format(
            page_size, keywords_encoded, place_urn, count
        )
        
        data = await crawl_linkedin_api(url)
        
        old_count = count
        if data and "included" in data:
            included = data["included"]
            page_jobs = 0
            for obj in included:
                if isJob(obj):
                    job_urn = obj.get("entityUrn", "")
                    job_title = obj.get("title", "Unknown")
                    
                    print(f"  ⏳ Fetching details for: {job_title}")
                    job_data = await getJobData(job_urn)
                    
                    jobs.append({
                        "title": job_title,
                        "urn": job_urn,
                        "company": obj.get("companyDetails", {}).get("company", {}).get("name", "Unknown"),
                        "location": obj.get("formattedLocation", "Unknown"),
                        "apply_link": job_data.get("apply_link", "") if job_data else "",
                        "description": job_data.get("description", "") if job_data else "",
                        "image": job_data.get("image", "") if job_data else "",
                    })
                    page_jobs += 1
            
            print(f"  ✅ Found {page_jobs} jobs on this page")
            count = count + page_size
        
        if old_count == count:
            print("  ⚠️  No more jobs found, stopping...")
            break
        
        # Small delay to avoid rate limiting
        await asyncio.sleep(1)
    
    return jobs


async def main():
    """Main function"""
    print("=" * 80)
    print("LINKEDIN JOB SCRAPER - Based on Random User Skills")
    print("=" * 80)
    
    # Connect to database
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Get random user and their skills
        print("\n📊 Fetching random user's skills from database...")
        user, skills = get_random_user_skills(db)
        
        if not user or not skills:
            print("❌ No users with skills found in database!")
            print("   Please upload some PDFs first to generate skills.")
            return
        
        print(f"✅ Selected user: {user.username} (ID: {user.id})")
        print(f"✅ Found {len(skills)} skills: {', '.join(skills)}")
        
        # Combine skills into keywords
        keywords = combine_skills_to_keywords(skills)
        print(f"✅ Search keywords: {keywords}")
        
        # Ask for location
        print("\n" + "-" * 80)
        location = input("📍 Enter location (e.g., 'New York', 'London', 'San Francisco'): ").strip()
        
        if not location:
            print("❌ Location is required!")
            return
        
        # Ask for number of pages (optional)
        pages_input = input("📄 Number of pages to scrape (default: 3, max: 10): ").strip()
        try:
            max_pages = min(int(pages_input) if pages_input else 3, 10)
        except ValueError:
            max_pages = 3
        
        # Scrape jobs
        jobs = await scrape_jobs(keywords, location, max_pages)
        
        # Display results
        print("\n" + "=" * 80)
        print(f"📊 RESULTS: Found {len(jobs)} jobs")
        print("=" * 80)
        
        if jobs:
            # Save to JSON file
            output_file = f"jobs_{user.username}_{location.replace(' ', '_')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "user": {
                        "id": user.id,
                        "username": user.username
                    },
                    "skills_used": skills,
                    "keywords": keywords,
                    "location": location,
                    "total_jobs": len(jobs),
                    "jobs": jobs
                }, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Results saved to: {output_file}")
            
            # Display first 5 jobs
            print("\n📋 First 5 jobs:")
            print("-" * 80)
            for i, job in enumerate(jobs[:5], 1):
                print(f"\n{i}. {job['title']}")
                print(f"   Company: {job['company']}")
                print(f"   Location: {job['location']}")
                if job.get('apply_link'):
                    print(f"   Apply: {job['apply_link']}")
        else:
            print("❌ No jobs found. Try different keywords or location.")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())

