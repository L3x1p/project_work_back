"""
LinkedIn job scraping module - using the working crawler implementation
"""
import urllib.parse
import asyncio
import requests
from typing import Optional, List, Dict


# LinkedIn API credentials (from linkdn_crawler.py)
CSRF_TOKEN = 'ajax:-7835579736576380789'
COOKIE = 'bcookie="v=2&cbdf1a5b-6b15-46d8-8e6e-63b8514b10b9"; bscookie="v=1&20240310034951eaeec32b-9e5f-4b0b-8f76-ea8174b60eceAQFt2LRtneXzEpoWU9qba4EFfqsrP11e"; JSESSIONID="ajax:-7835579736576380789"; liap=true; li_sugr=363f5de2-d7b1-4e24-8c33-e0fce10a2316; li_theme=light; li_theme_set=app; dfpfpt=f947313ecc96458b81b6e614b74f78c7; timezone=Europe/Paris; li_at=AQEDAT_4KeUFJtBOAAABkikHm-8AAAGb733VUE4AV1yJHEX1IQ0aTUlHczf-xZH7Qx6v6ylEHZ7vz8Zq56gSZASG6jpzPueKYPC3W3Qh0n0uoFxGoBMlZwY46JjEgzJWT-Xj7tKFvh8hiTq1o3tXYgG6; lang=v=2&lang=ru-ru; li_mc=MTsyMTsxNzY4ODMwNDkxOzE7MDIxx1nGOQjhrCsiG/xZrsndvlzBTRevo1h00lS1ACTtQEo=; __cf_bm=_tMA3zIHiu5dT8mDCw0oQVejUY6piK_4bm2dgslaVGk-1768830491-1.0.1.1-w85fK3Rs4DMWCWWm8qYeD4uTsvAHB0GcLG45erreLB4kZ.s9DwU6o4djuY8GJdVlxpNYwtzQYLLbCYS9Sbt13qc4zbpk_dDuzdNZ7ukwii4; AnalyticsSyncHistory=AQLpy1ndH6-yAgAAAZvWg3qLUxdWVa7jPqPZcT75O1Mc-gRWtHhwSCHiRkb94fokqSEseDLI36cmNiNbcUoTeA; lms_ads=AQH9aY7IfE3lVgAAAZvWg3v2RZBb86hFwRPqI6arumSRn3jscR5_4IQOoDM0XZpTDlHzYQA7SGMrlW3x1fbpfBHZtYRgNl2c; lms_analytics=AQH9aY7IfE3lVgAAAZvWg3v2RZBb86hFwRPqI6arumSRn3jscR5_4IQOoDM0XZpTDlHzYQA7SGMrlW3x1fbpfBHZtYRgNl2c; fptctx2=taBcrIH61PuCVH7eNCyH0APzNoEiOrOqF4FbdtfiWWKxe4w5xCuGmPE2aH%252b46%252bFquvt4qAhz0G6fwYP%252fzNNX0idiAsMV%252f9p6fWWBxJCC2FLGTu%252f8UCFau9XqewkNQdhJ2tYzSq05QapE4ym6eEzPSxeIbu3kYjrDrr20evlalycEQfzY0632TA6vPKDBTiZQWMQRnVZD4m%252bS6o407Gw%252b9C2MsLISuFUc5PE0jDmLZ%252fyLQTUX3AEYvhGGbuiVK0dH8NLd3g8bQRyyOidFk4VOa37s%252bL%252f9SKXJbW7UYGCcz48KOhQJDAZSUVSqDA45kx%252b5v2vLNom9ymHTCABgI52RC8izsDHqSLIQo16KSehdhgs%253d; sdui_ver=sdui-flagship:0.1.24688+SduiFlagship0; UserMatchHistory=AQIrj3Hq3oFGdAAAAZvWirCCxlzMhy7ZttFGeDMaksd7O7wrjHDeI0D9AuiGz4J9HADrqziXxHU5PJseLOwWzmRoMEg5eHkEuE3BkBy4FB3BFPhP611p_EFxkBYYKhqWrAkMHc2hHyzcIr6v7LnnTFjPIAE5g9jV0qFryeXIfCZCaJcNUPI6PIIs5Kx6JdVUyCw0NyQpiqb6uhOgvoHrpV5HLsScLTTaHdHgWsjnazJAmrKxI8ML7T6aZWEYQPjLSP6BarT_Jm7Ammw6lDXBDHSWaGNXqN2CLL3aVRS8gHMp57RfHQsxseb-brp3hgbzV1NSiL5PoT8XiVs; lidc="b=VB61:s=V:r=V:a=V:p=V:g=6557:u=234:x=1:i=1768830974:t=1768912006:v=2:sig=AQGE7c3GoztYS7-Gyz8gyIW2cnQ46I8B"'


def crawl_linkedin_api(url: str) -> Optional[Dict]:
    """Synchronous function to crawl LinkedIn API"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
        'Accept': 'application/vnd.linkedin.normalized+json+2.1',
        'Referer': 'https://www.linkedin.com/search/results/people/?keywords=software%20engineer&origin=GLOBAL_SEARCH_HEADER&sid=crG',
        'csrf-token': CSRF_TOKEN,
        'Cookie': COOKIE
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return None
    except Exception as e:
        return None


def is_job(obj):
    """Check if object is a job posting"""
    if '$type' not in obj or obj['$type'] != 'com.linkedin.voyager.dash.jobs.JobPosting':
        return Falsef
    return True


def find_place(place: str) -> Optional[str]:
    """Find place URN"""
    url = "https://www.linkedin.com/voyager/api/graphql?variables=(keywords:{},query:(typeaheadFilterQuery:(geoSearchTypes:List(POSTCODE_1,POSTCODE_2,POPULATED_PLACE,ADMIN_DIVISION_1,ADMIN_DIVISION_2,COUNTRY_REGION,MARKET_AREA,COUNTRY_CLUSTER)),typeaheadUseCase:JOBS),type:GEO)&queryId=voyagerSearchDashReusableTypeahead.54529a68d290553c6f24e28ab3448654".format(place)

    data = crawl_linkedin_api(url)
    if data:
        included = data.get('included', [])
        if included:
            return included[0]['entityUrn'].split(':')[-1]

    return None


async def scrape_jobs(keywords: str, place: str, max_pages: int = 1) -> List[Dict]:
    """
    Scrape LinkedIn jobs based on keywords and location.
    Async wrapper around the synchronous crawler.
    
    Args:
        keywords: Job search keywords
        place: City/location name
        max_pages: Maximum number of pages to scrape
    
    Returns:
        List of job dictionaries with 'title', 'urn', 'company', 'location' fields
    """
    # Run synchronous operations in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    
    # Find place URN
    place_encoded = urllib.parse.quote(place)
    place_urn = await loop.run_in_executor(None, find_place, place_encoded)
    
    if place_urn is None:
        return []
    
    jobs = []
    count = 0
    old_count = 0
    page_size = 25
    keywords_encoded = urllib.parse.quote(keywords)
    
    for page in range(max_pages):
        url = "https://www.linkedin.com/voyager/api/voyagerJobsDashJobCards?decorationId=com.linkedin.voyager.dash.deco.jobs.search.JobSearchCardsCollection-218&count={}&q=jobSearch&query=(origin:JOB_SEARCH_PAGE_SEARCH_BUTTON,keywords:{},locationUnion:(geoId:{}),selectedFilters:(distance:List(0)),spellCorrectionEnabled:true)&start={}".format(
            page_size, keywords_encoded, place_urn, count
        )
        
        # Run synchronous request in thread pool
        data = await loop.run_in_executor(None, crawl_linkedin_api, url)
        
        old_count = count
        if data:
            included = data.get('included', [])
            for obj in included:
                if is_job(obj):
                    # Extract job information with better field extraction
                    job_title = obj.get('title', '')
                    job_urn = obj.get('entityUrn', '')
                    
                    # Extract company name - try multiple paths
                    company_name = ''
                    if 'companyDetails' in obj:
                        company_details = obj.get('companyDetails', {})
                        if 'company' in company_details:
                            company_name = company_details.get('company', {}).get('name', '')
                        elif 'companyName' in company_details:
                            company_name = company_details.get('companyName', '')
                    
                    # If still empty, try other paths
                    if not company_name:
                        company_name = obj.get('companyName', '') or obj.get('company', '')
                    
                    # Extract location - try multiple paths
                    location = obj.get('formattedLocation', '') or obj.get('location', '') or obj.get('formattedLocationText', '')
                    
                    # Construct LinkedIn job URL from URN
                    apply_link = ''
                    if job_urn:
                        # Extract job ID from URN (format: urn:li:fsd_jobPosting:123456)
                        try:
                            job_id = job_urn.split(':')[-1] if ':' in job_urn else job_urn
                            apply_link = f"https://www.linkedin.com/jobs/view/{job_id}"
                        except:
                            pass
                    
                    # Only add job if we have at least a title
                    if job_title:
                        jobs.append({
                            'title': job_title,
                            'urn': job_urn,
                            'company': company_name if company_name else None,
                            'location': location if location else None,
                            'apply_link': apply_link,
                            'description': None,  # Description requires separate API call, can be added later
                            'image': None
                        })
            
            count = count + page_size
        
        if old_count == count:
            break
        
        # Small delay to avoid rate limiting
        await asyncio.sleep(1)
    
    return jobs

