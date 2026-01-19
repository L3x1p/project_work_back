import requests
import json
import time
import sys
import urllib.parse

csrtToken = 'ajax:-7835579736576380789'
cookie  = 'bcookie="v=2&cbdf1a5b-6b15-46d8-8e6e-63b8514b10b9"; bscookie="v=1&20240310034951eaeec32b-9e5f-4b0b-8f76-ea8174b60eceAQFt2LRtneXzEpoWU9qba4EFfqsrP11e"; JSESSIONID="ajax:-7835579736576380789"; liap=true; li_sugr=363f5de2-d7b1-4e24-8c33-e0fce10a2316; li_theme=light; li_theme_set=app; dfpfpt=f947313ecc96458b81b6e614b74f78c7; timezone=Europe/Paris; li_at=AQEDAT_4KeUFJtBOAAABkikHm-8AAAGb733VUE4AV1yJHEX1IQ0aTUlHczf-xZH7Qx6v6ylEHZ7vz8Zq56gSZASG6jpzPueKYPC3W3Qh0n0uoFxGoBMlZwY46JjEgzJWT-Xj7tKFvh8hiTq1o3tXYgG6; lang=v=2&lang=ru-ru; li_mc=MTsyMTsxNzY4ODMwNDkxOzE7MDIxx1nGOQjhrCsiG/xZrsndvlzBTRevo1h00lS1ACTtQEo=; __cf_bm=_tMA3zIHiu5dT8mDCw0oQVejUY6piK_4bm2dgslaVGk-1768830491-1.0.1.1-w85fK3Rs4DMWCWWm8qYeD4uTsvAHB0GcLG45erreLB4kZ.s9DwU6o4djuY8GJdVlxpNYwtzQYLLbCYS9Sbt13qc4zbpk_dDuzdNZ7ukwii4; AnalyticsSyncHistory=AQLpy1ndH6-yAgAAAZvWg3qLUxdWVa7jPqPZcT75O1Mc-gRWtHhwSCHiRkb94fokqSEseDLI36cmNiNbcUoTeA; lms_ads=AQH9aY7IfE3lVgAAAZvWg3v2RZBb86hFwRPqI6arumSRn3jscR5_4IQOoDM0XZpTDlHzYQA7SGMrlW3x1fbpfBHZtYRgNl2c; lms_analytics=AQH9aY7IfE3lVgAAAZvWg3v2RZBb86hFwRPqI6arumSRn3jscR5_4IQOoDM0XZpTDlHzYQA7SGMrlW3x1fbpfBHZtYRgNl2c; fptctx2=taBcrIH61PuCVH7eNCyH0APzNoEiOrOqF4FbdtfiWWKxe4w5xCuGmPE2aH%252b46%252bFquvt4qAhz0G6fwYP%252fzNNX0idiAsMV%252f9p6fWWBxJCC2FLGTu%252f8UCFau9XqewkNQdhJ2tYzSq05QapE4ym6eEzPSxeIbu3kYjrDrr20evlalycEQfzY0632TA6vPKDBTiZQWMQRnVZD4m%252bS6o407Gw%252b9C2MsLISuFUc5PE0jDmLZ%252fyLQTUX3AEYvhGGbuiVK0dH8NLd3g8bQRyyOidFk4VOa37s%252bL%252f9SKXJbW7UYGCcz48KOhQJDAZSUVSqDA45kx%252b5v2vLNom9ymHTCABgI52RC8izsDHqSLIQo16KSehdhgs%253d; sdui_ver=sdui-flagship:0.1.24688+SduiFlagship0; UserMatchHistory=AQIrj3Hq3oFGdAAAAZvWirCCxlzMhy7ZttFGeDMaksd7O7wrjHDeI0D9AuiGz4J9HADrqziXxHU5PJseLOwWzmRoMEg5eHkEuE3BkBy4FB3BFPhP611p_EFxkBYYKhqWrAkMHc2hHyzcIr6v7LnnTFjPIAE5g9jV0qFryeXIfCZCaJcNUPI6PIIs5Kx6JdVUyCw0NyQpiqb6uhOgvoHrpV5HLsScLTTaHdHgWsjnazJAmrKxI8ML7T6aZWEYQPjLSP6BarT_Jm7Ammw6lDXBDHSWaGNXqN2CLL3aVRS8gHMp57RfHQsxseb-brp3hgbzV1NSiL5PoT8XiVs; lidc="b=VB61:s=V:r=V:a=V:p=V:g=6557:u=234:x=1:i=1768830974:t=1768912006:v=2:sig=AQGE7c3GoztYS7-Gyz8gyIW2cnQ46I8B"'


def crawl_linkedin_api(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
        'Accept': 'application/vnd.linkedin.normalized+json+2.1',
        'Referer': 'https://www.linkedin.com/search/results/people/?keywords=software%20engineer&origin=GLOBAL_SEARCH_HEADER&sid=crG',
        'csrf-token': csrtToken,
        'Cookie': cookie
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Request failed with status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def isJob(obj):
    if '$type' not in obj or obj['$type'] != 'com.linkedin.voyager.dash.jobs.JobPosting':
        return False

    return True

#not working yet
def findPlace(place):

    url = "https://www.linkedin.com/voyager/api/graphql?variables=(keywords:{},query:(typeaheadFilterQuery:(geoSearchTypes:List(POSTCODE_1,POSTCODE_2,POPULATED_PLACE,ADMIN_DIVISION_1,ADMIN_DIVISION_2,COUNTRY_REGION,MARKET_AREA,COUNTRY_CLUSTER)),typeaheadUseCase:JOBS),type:GEO)&queryId=voyagerSearchDashReusableTypeahead.54529a68d290553c6f24e28ab3448654".format(place)

    data = crawl_linkedin_api(url)
    if data:
        included = data['included']
        if included:
            return included[0]['entityUrn'].split(':')[-1]

    return None

#not working yet
def getJobData(jobUrn):

    url = "https://www.linkedin.com/voyager/api/graphql?variables=(cardSectionTypes:List(TOP_CARD,HOW_YOU_FIT_CARD),jobPostingUrn:{},includeSecondaryActionsV2:true,includeHowYouFitCard:true,includeFitLevelCard:true)&queryId=voyagerJobsDashJobPostingDetailSections.17ee06580bc57b725f7da94df52dc34f".format(urllib.parse.quote(jobUrn))

    data = crawl_linkedin_api(url)
    if data:
        return {

        }

    return None

def grabDataFromObj(obj, dataId):
    return ''


def main():
    if len(sys.argv) > 1:
        keywords = urllib.parse.quote(sys.argv[1])
    else:
        print("Write the job keywords")
        return 0

    if len(sys.argv) > 2:
        place = urllib.parse.quote(sys.argv[2])
    else:
        print("Write the place")
        return 0
    if len(sys.argv) > 3:
        page = int(sys.argv[3])
    else:
        print("Write the page count")
        return 0

    placeUrn = findPlace(place)
    if placeUrn is None:
        print("Could not find the place")
        return 0

    jobs = []
    count = 0;
    oldCount = 0
    pageSize = 25

    for i in range(page):
        url = "https://www.linkedin.com/voyager/api/voyagerJobsDashJobCards?decorationId=com.linkedin.voyager.dash.deco.jobs.search.JobSearchCardsCollection-218&count={}&q=jobSearch&query=(origin:JOB_SEARCH_PAGE_SEARCH_BUTTON,keywords:{},locationUnion:(geoId:{}),selectedFilters:(distance:List(0)),spellCorrectionEnabled:true)&start={}".format(pageSize,keywords,placeUrn,count)

        data = crawl_linkedin_api(url)

        oldCount = count
        if data:
            included = data['included'];
            for obj in included:
                if isJob(obj):
                    jobs.append({
                        'name' : obj['title'],
                        'urn' : obj['entityUrn'],
                        'data' : getJobData(obj['entityUrn'])
                        })
            count = count + pageSize

        if oldCount == count :
            break
            

    print(json.dumps(jobs, indent=4));

if __name__ == "__main__":
    main()