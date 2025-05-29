import os
from dotenv import load_dotenv
from getting_info import JobScraper, CompanyResearcher
from linkedin_messaging import ProfileGenerator, OutreachManager
import logging
from typing import Dict, List
import time
from tenacity import retry, stop_after_attempt, wait_exponential

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('linkedin_outreach.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LinkedInOutreachPipeline:
    def __init__(self):
        self.job_scraper = JobScraper()
        self.company_researcher = CompanyResearcher()
        self.profile_generator = ProfileGenerator()
        self.outreach_manager = OutreachManager()
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _safe_api_call(self, func, *args, **kwargs):
        """Wrapper for safe API calls with retry logic"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"API call failed: {str(e)}")
            raise
            
    def research_company(self, company_name: str, job_description: str) -> Dict:
        """Perform comprehensive company research"""
        try:
            # Get company details
            company_info = self._safe_api_call(
                self.company_researcher.get_company_info,
                company_name
            )
            
            # Analyze role requirements
            role_analysis = self._safe_api_call(
                self.company_researcher.analyze_role,
                job_description
            )
            
            # Get recent news and developments
            company_news = self._safe_api_call(
                self.company_researcher.get_company_news,
                company_name
            )
            
            return {
                "company_info": company_info,
                "role_analysis": role_analysis,
                "recent_news": company_news
            }
        except Exception as e:
            logger.error(f"Company research failed for {company_name}: {str(e)}")
            return {}

    def generate_targeted_profile(self, job_data: Dict, company_research: Dict) -> Dict:
        """Generate a targeted candidate profile"""
        try:
            return self._safe_api_call(
                self.profile_generator.generate_profile,
                job_data,
                company_research
            )
        except Exception as e:
            logger.error(f"Profile generation failed: {str(e)}")
            return {}

    def execute_outreach(self, job_data: Dict, profile: Dict, company_research: Dict) -> bool:
        """Execute multi-channel outreach"""
        try:
            # Send email
            email_success = self._safe_api_call(
                self.outreach_manager.send_email,
                job_data,
                profile,
                company_research
            )
            
            # Send LinkedIn InMail
            linkedin_success = self._safe_api_call(
                self.outreach_manager.send_linkedin_message,
                job_data,
                profile,
                company_research
            )
            
            # Schedule follow-up
            if email_success or linkedin_success:
                self.outreach_manager.schedule_followup(job_data)
            
            return email_success or linkedin_success
        except Exception as e:
            logger.error(f"Outreach failed: {str(e)}")
            return False

    def run_pipeline(self, role: str, location: str, max_jobs: int = 5):
        """Run the complete outreach pipeline"""
        logger.info(f"Starting pipeline for {role} in {location}")
        
        try:
            # 1. Get job listings
            jobs = self._safe_api_call(self.job_scraper.fetch_job_listings, role, location)
            
            for job in jobs[:max_jobs]:
                job_id = job.get('job_id')
                if not job_id:
                    continue
                    
                logger.info(f"Processing job {job_id}")
                
                # 2. Get detailed job info
                job_details = self._safe_api_call(
                    self.job_scraper.fetch_job_details,
                    job_id
                )
                
                if not job_details:
                    continue
                
                # 3. Research company
                company_research = self.research_company(
                    job_details.get('company_name', ''),
                    job_details.get('job_description', '')
                )
                
                # 4. Generate targeted profile
                profile = self.generate_targeted_profile(job_details, company_research)
                
                if not profile:
                    continue
                
                # 5. Execute outreach
                success = self.execute_outreach(job_details, profile, company_research)
                
                if success:
                    logger.info(f"Successfully processed job {job_id}")
                else:
                    logger.warning(f"Failed to process job {job_id}")
                
                # Rate limiting
                time.sleep(2)
                
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            raise

if __name__ == "__main__":
    pipeline = LinkedInOutreachPipeline()
    pipeline.run_pipeline("Software Engineer", "San Francisco Bay Area", max_jobs=3) 