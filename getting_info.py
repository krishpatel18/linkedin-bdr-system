import requests
import os
import time
from dotenv import load_dotenv
import urllib.parse
from serpapi import GoogleSearch

# Load environment variables
load_dotenv()
API_KEY = os.getenv("SCRAPINGDOG_API_KEY")
HUNTER_API_KEY = os.getenv("HUNTER_API_KEY")
SERP_API_KEY = os.getenv("SERP_API_KEY")
PHANTOMBUSTER_API_KEY = os.getenv("PHANTOMBUSTER_API_KEY")
PROFILE_SCRAPER_ID = os.getenv("PHANTOMBUSTER_PROFILE_SCRAPER_ID")
#SEARCH_EXPORT_ID = os.getenv("PHANTOMBUSTER_SEARCH_EXPORT_ID")
SHEETY_URL = "https://api.sheety.co/9d830cd8f7cb7e6c180eb20ac92818d7/linkedInHiringOutreachSheet/information"

# Supported location mapping
LOCATIONS = {
    "US": "103644278",
    "Canada": "101174742",
    "Toronto, ON": "102264111",
    "Vancouver, BC": "101997229",
    "Montreal, QC": "104057199",
    "San Francisco Bay Area": "90000084",
    "New York City": "102571732",
    "London, UK": "102257491",
    "Bangalore, India": "102713980",
    "Singapore": "106693272",
}

# Get user input
role = input("Enter role of interest: ")
location = input("Enter the location of interest: ")
geo_id = LOCATIONS.get(location, LOCATIONS["Canada"])

def fetch_job_listings(role, geo_id):
    """Fetch job listings for the given role and geo_id."""
    url = "https://api.scrapingdog.com/linkedinjobs/"
    params = {
        "api_key": API_KEY,
        "field": role,
        "geoid": geo_id,
        "page": "1"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching job listings: {e}")
        return []

def fetch_job_details(job_id):
    """Fetch detailed information for a specific job."""
    url = "https://api.scrapingdog.com/linkedinjobs"
    params = {
        "api_key": API_KEY,
        "job_id": job_id
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        #print(data)
        #print("\n\n\n\n")
        if isinstance(data, list) and data:
            return data[0]
        elif isinstance(data, dict):
            return data
        else:
            print(f"Unexpected data format for job_id {job_id}")
            return None
    except requests.RequestException as e:
        print(f"Error fetching job details for {job_id}: {e}")
        return None

def extract_recruiter_info(job_data):
    """Extract recruiter details safely."""
    recruiter_info = job_data.get('recruiter_details', [])
    if isinstance(recruiter_info, list) and recruiter_info:
        recruiter = recruiter_info[0]
        return (
            recruiter.get('recruiter_name', ''),
            recruiter.get('recruiter_title', ''),
            recruiter.get('recruiter_profile_url', '')
        ) 
    return '', '', ''


def trigger_phantom(phantom_id, input_obj):
    """Trigger a PhantomBuster Phantom and return the result."""
    headers = {
        "Content-Type": "application/json",
        "X-Phantombuster-Key-1": PHANTOMBUSTER_API_KEY
    }
    trigger_url = f"https://api.phantombuster.com/api/v2/agent/{phantom_id}/launch"

    payload = {
        "output": "result-object",
        "arguments": {
            "input": input_obj
        }
    }

    try:
        response = requests.post(trigger_url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"PhantomBuster trigger failed: {e}")
        return None



'''---------HERE----------'''

def recruiter_contact_info(recruiter_info, job_data):
    recruiter_name, recruiter_title, recruiter_profile_url = recruiter_info
    company_name = job_data.get("company_name", "")
    
    if not recruiter_name:
        recruiter_name = "Hiring Manager"
        recruiter_title = "Talent Acquisition"

    # Fallback LinkedIn profile URL
    if not recruiter_profile_url and recruiter_name and company_name:
        params = {
        "engine": "google",
        "q": f"{recruiter_name} {company_name} site:linkedin.com",
        "api_key": SERP_API_KEY
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        if "organic_results" in results and results["organic_results"]:
            recruiter_profile_url = results["organic_results"][0]["link"]
        else:
            recruiter_profile_url = ''
        '''
        if not recruiter_profile_url:
            # Fallback to PhantomBuster LinkedIn Search Export
            phantom_input = {
                "search": f"{recruiter_name} {company_name} site:linkedin.com"
            }
            result = trigger_phantom(SEARCH_EXPORT_ID, phantom_input)
            if result and result.get("container") and len(result["container"].get("csvUrl", "")) > 0:
                # Ideally download and parse CSV here, or rely on PhantomBuster webhook
                recruiter_profile_url = "[LinkedIn profile from PhantomBuster search]"
        '''

    if recruiter_profile_url and recruiter_name == 'Hiring Manager':
        phantom_input = {
            "profileUrl": recruiter_profile_url
        }
        result = trigger_phantom(PROFILE_SCRAPER_ID, phantom_input)
        if result and result.get("container") and "firstName" in result["container"]:
            recruiter_name = f"{result['container'].get('firstName', '')} {result['container'].get('lastName', '')}"
            recruiter_title = result["container"].get("jobTitle", recruiter_title)


    recruiter_email = find_email_via_hunter(recruiter_name, company_name)
    
    return recruiter_name, recruiter_title, recruiter_profile_url, recruiter_email

def find_email_via_hunter(recruiter_name, company_name):
    """Query Hunter.io API to find recruiter email based on name and domain."""
    if not recruiter_name or not company_name:
        return ""

    # Step 1: Get domain from company name
    domain_search_url = f"https://api.hunter.io/v2/domain-search"
    domain_params = {
        "company": company_name,
        "api_key": HUNTER_API_KEY
    }
    try:
        r = requests.get(domain_search_url, params=domain_params)
        r.raise_for_status()
        data = r.json()
        domain = data.get("data", {}).get("domain")
    except Exception as e:
        print(f"Could not get domain for {company_name}: {e}")
        return ""

    if not domain:
        return ""

    # Step 2: Use Hunter email finder
    names = recruiter_name.split()
    if len(names) < 2:
        return ""
    first_name, last_name = names[0], names[-1]

    email_finder_url = "https://api.hunter.io/v2/email-finder"
    email_params = {
        "domain": domain,
        "first_name": first_name,
        "last_name": last_name,
        "api_key": HUNTER_API_KEY
    }

    try:
        r = requests.get(email_finder_url, params=email_params)
        r.raise_for_status()
        data = r.json()
        return data.get("data", {}).get("email", "")
    except Exception as e:
        print(f"Could not find email for {recruiter_name} at {domain}: {e}")
        return ""



'''
def recruiter_contact_info(recruiter_info, job_details):
    recruiter_name = recruiter_info('recruiter_name', '')
    recruiter_title = recruiter_info('recruiter_title', '')
    recruiter_profile_url = recruiter_info('recruiter_profile_url', '')
    company_name = job_details.get("company_name", "")
    position = "Hiring Manager"

    if(recruiter_name == None):
        #Use Linkedin Search to get recruiter name, company, and title as needed
'''

def upload_to_sheety(job_data, recruiter_info):
    """Upload job and recruiter details to Sheety."""
    payload = {
        "information": {
            "jobPosition": job_data.get("job_position", ""),
            "jobLocation": job_data.get("job_location", ""),
            "companyName": job_data.get("company_name", ""),
            "companyLinkedinId": job_data.get("company_linkedin_id", ""),
            "jobDescription": job_data.get("job_description", ""),
            "seniorityLevel": job_data.get("Seniority_level", ""),
            "employmentType": job_data.get("Employment_type", ""),
            "jobFunction": job_data.get("Job_function", ""),
            "industries": job_data.get("Industries", ""),
            "jobApplyLink": job_data.get("job_apply_link", ""),
            "recruiterName": recruiter_info[0],
            "recruiterTitle": recruiter_info[1],
            "recruiterProfileLink": recruiter_info[2],
            "recruiterEmail": recruiter_info[3]
        }
    }

    try:
        response = requests.post(SHEETY_URL, json=payload)
        if response.status_code == 200:
            print("Uploaded to Sheety:", payload["information"]["jobPosition"])
        else:
            print(f"Sheety upload failed: {response.status_code} - {response.text}")
    except requests.RequestException as e:
        print(f"Failed to upload to Sheety: {e}")

def main():
    jobs_data = fetch_job_listings(role, geo_id)

    if not isinstance(jobs_data, list):
        print("No job data returned or incorrect format.")
        return

    for i, job in enumerate(jobs_data):
        if i >= 3:  # Limit API calls
            break

        print(f"\nProcessing job {i + 1}/{min(3, len(jobs_data))}: {job.get('job_id')}")
        job_id = job.get('job_id')
        if not job_id:
            print("Missing job_id; skipping.")
            continue

        job_details = fetch_job_details(job_id)
        if not job_details:
            continue

        recruiter_raw = extract_recruiter_info(job_details)
        recruiter_final = recruiter_contact_info(recruiter_raw, job_details)
        #print(jobs_data) # To see if the job has recruiter info
        upload_to_sheety(job_details, recruiter_final)

        time.sleep(1)  # To respect API rate limits

if __name__ == "__main__":
    main()
