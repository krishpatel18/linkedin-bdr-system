import os
from typing import Dict
import smtplib
from email.message import EmailMessage
from openai import OpenAI
from datetime import datetime, timedelta
import logging
from linkedin_api import Linkedin
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
LINKEDIN_USERNAME = os.getenv("LINKEDIN_USERNAME")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

logger = logging.getLogger(__name__)

class OutreachManager:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.linkedin = Linkedin(LINKEDIN_USERNAME, LINKEDIN_PASSWORD)
        self.followup_sheet_url = os.getenv("SHEETY_FOLLOWUP_URL")
        
    def send_email(self, job_data: Dict, profile: Dict, company_research: Dict) -> bool:
        """Send personalized email to hiring manager"""
        try:
            # Generate email content
            email_content = self._generate_email_content(
                job_data,
                profile,
                company_research
            )
            
            # Create email message
            msg = EmailMessage()
            msg["Subject"] = email_content["subject"]
            msg["From"] = EMAIL_ADDRESS
            msg["To"] = job_data.get("recruiter_email", "")
            
            # Construct email body
            body = f"""{email_content['greeting']}

{email_content['opening']}

{email_content['body']}

{email_content['closing']}

{email_content['signature']}"""
            
            msg.set_content(body)
            
            # Send email
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                smtp.send_message(msg)
                
            logger.info(f"Email sent to {msg['To']}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False
            
    def send_linkedin_message(self, job_data: Dict, profile: Dict, company_research: Dict) -> bool:
        """Send LinkedIn InMail to hiring manager"""
        try:
            # Get recruiter profile URL
            recruiter_url = job_data.get("recruiter_profile_link", "")
            if not recruiter_url:
                return False
                
            # Generate message content
            message_content = self._generate_linkedin_message(
                job_data,
                profile,
                company_research
            )
            
            # Extract profile ID from URL
            profile_id = recruiter_url.split("/in/")[-1].strip("/")
            
            # Send message
            self.linkedin.send_message(
                profile_id,
                message_content["body"]
            )
            
            logger.info(f"LinkedIn message sent to {profile_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to send LinkedIn message: {str(e)}")
            return False
            
    def schedule_followup(self, job_data: Dict) -> None:
        """Schedule follow-up messages"""
        try:
            # Calculate follow-up dates
            application_date = datetime.now()
            first_followup = application_date + timedelta(days=5)
            second_followup = application_date + timedelta(days=10)
            
            # Create follow-up schedule
            followups = {
                "job_id": job_data.get("job_id"),
                "recruiter_email": job_data.get("recruiter_email"),
                "followups": [
                    {
                        "date": first_followup.strftime("%Y-%m-%d"),
                        "type": "email",
                        "status": "scheduled"
                    },
                    {
                        "date": second_followup.strftime("%Y-%m-%d"),
                        "type": "linkedin",
                        "status": "scheduled"
                    }
                ]
            }
            
            # Store in Google Sheet
            self._store_followup(followups)
            
            logger.info(f"Follow-ups scheduled for job {job_data.get('job_id')}")
        except Exception as e:
            logger.error(f"Failed to schedule follow-ups: {str(e)}")
            
    def _store_followup(self, followup_data: Dict) -> None:
        """Store follow-up information in Google Sheet"""
        try:
            # Format data for Sheety
            for followup in followup_data["followups"]:
                payload = {
                    "followup": {
                        "jobId": followup_data["job_id"],
                        "recruiterEmail": followup_data["recruiter_email"],
                        "followupDate": followup["date"],
                        "followupType": followup["type"],
                        "status": followup["status"]
                    }
                }
                
                # Send to Sheety
                response = requests.post(self.followup_sheet_url, json=payload)
                response.raise_for_status()
                
            logger.info(f"Stored follow-ups for job {followup_data['job_id']}")
        except Exception as e:
            logger.error(f"Failed to store follow-up: {str(e)}")
            
    def _generate_email_content(self, job_data: Dict, profile: Dict, company_research: Dict) -> Dict:
        """Generate personalized email content"""
        try:
            prompt = f"""Create a personalized email for this job application:
            
            Job: {job_data.get('job_position')} at {job_data.get('company_name')}
            Recruiter: {job_data.get('recruiter_name')}
            
            Company Research:
            {company_research}
            
            Candidate Profile:
            {profile}
            
            Requirements:
            1. Engaging subject line
            2. Personal connection to company/role
            3. Highlight matching qualifications
            4. Show company knowledge
            5. Clear call to action
            
            Format as JSON with:
            - subject
            - greeting
            - opening
            - body
            - closing
            - signature"""
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            return eval(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Failed to generate email content: {str(e)}")
            return {}
            
    def _generate_linkedin_message(self, job_data: Dict, profile: Dict, company_research: Dict) -> Dict:
        """Generate personalized LinkedIn message"""
        try:
            prompt = f"""Create a personalized LinkedIn message for this job application:
            
            Job: {job_data.get('job_position')} at {job_data.get('company_name')}
            Recruiter: {job_data.get('recruiter_name')}
            
            Company Research:
            {company_research}
            
            Candidate Profile:
            {profile}
            
            Requirements:
            1. Brief but impactful
            2. Show genuine interest
            3. Highlight key qualification
            4. Professional tone
            5. Clear next step
            
            Format as JSON with body field."""
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            return eval(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Failed to generate LinkedIn message: {str(e)}")
            return {} 