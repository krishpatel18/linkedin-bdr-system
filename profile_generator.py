import os
from typing import Dict
from openai import OpenAI
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

logger = logging.getLogger(__name__)

class ProfileGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        
    def generate_profile(self, job_data: Dict, company_research: Dict) -> Dict:
        """Generate a targeted candidate profile based on job and company research"""
        try:
            # Extract relevant information
            job_title = job_data.get("job_position", "")
            company_name = job_data.get("company_name", "")
            job_description = job_data.get("job_description", "")
            
            # Get company culture and tech stack
            company_info = company_research.get("company_info", {})
            role_analysis = company_research.get("role_analysis", {})
            
            prompt = f"""Create a highly targeted candidate profile for this position:

            Job Title: {job_title}
            Company: {company_name}
            Job Description: {job_description}

            Company Culture: {company_info.get('culture', '')}
            Tech Stack: {company_info.get('tech_stack', '')}
            Role Requirements: {role_analysis}

            Generate a profile that:
            1. Matches the technical requirements exactly
            2. Aligns with the company culture
            3. Shows progression toward this role
            4. Includes relevant achievements
            5. Demonstrates cultural fit
            
            Format as a structured JSON with:
            - headline
            - summary
            - skills (technical and soft)
            - experience (list of roles)
            - education
            - achievements
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            profile = eval(response.choices[0].message.content)
            
            # Enhance profile with company-specific details
            enhanced_profile = self._enhance_profile_with_company_details(
                profile,
                company_research
            )
            
            return enhanced_profile
        except Exception as e:
            logger.error(f"Failed to generate profile: {str(e)}")
            return {}
            
    def _enhance_profile_with_company_details(self, profile: Dict, company_research: Dict) -> Dict:
        """Add company-specific enhancements to the profile"""
        try:
            # Get company news and info
            company_news = company_research.get("recent_news", [])
            company_info = company_research.get("company_info", {})
            
            # Add relevant interests based on company focus
            profile["interests"] = [
                tech for tech in company_info.get("tech_stack", [])
                if tech.lower() not in [skill.lower() for skill in profile.get("skills", [])]
            ]
            
            # Add relevant achievements that align with company news
            if company_news:
                profile["relevant_industry_knowledge"] = [
                    news["title"] for news in company_news
                    if news["sentiment"] == "POSITIVE"
                ][:2]
            
            # Add specific cultural alignment points
            if "culture" in company_info:
                profile["cultural_alignment"] = self._generate_cultural_alignment(
                    company_info["culture"]
                )
            
            return profile
        except Exception as e:
            logger.error(f"Failed to enhance profile: {str(e)}")
            return profile
            
    def _generate_cultural_alignment(self, company_culture: str) -> Dict:
        """Generate specific examples of cultural alignment"""
        try:
            prompt = f"""Based on this company culture:
            {company_culture}
            
            Generate 3 specific examples of how the candidate's background demonstrates alignment with this culture.
            Format as a JSON list."""
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            return eval(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Failed to generate cultural alignment: {str(e)}")
            return [] 