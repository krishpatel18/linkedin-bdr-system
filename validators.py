from typing import Dict, List, Optional
import re
from datetime import datetime

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

class JobDataValidator:
    @staticmethod
    def validate_job_listing(job_data: Dict) -> bool:
        """Validate job listing data"""
        required_fields = ['job_id', 'job_position', 'company_name', 'job_location', 'job_description']
        
        # Check required fields
        for field in required_fields:
            if not job_data.get(field):
                raise ValidationError(f"Missing required field: {field}")
        
        # Validate job description length
        if len(job_data['job_description']) < 50:
            raise ValidationError("Job description too short")
            
        return True

class ProfileValidator:
    @staticmethod
    def validate_profile(profile: Dict) -> bool:
        """Validate generated profile data"""
        required_fields = ['headline', 'summary', 'skills', 'experience', 'education']
        
        # Check required fields
        for field in required_fields:
            if not profile.get(field):
                raise ValidationError(f"Missing required field: {field}")
        
        # Validate skills
        if not isinstance(profile['skills'], list) or len(profile['skills']) < 3:
            raise ValidationError("Profile must have at least 3 skills")
        
        # Validate experience
        if not isinstance(profile['experience'], list) or len(profile['experience']) < 1:
            raise ValidationError("Profile must have at least 1 experience entry")
            
        # Validate education
        if not isinstance(profile['education'], list) or len(profile['education']) < 1:
            raise ValidationError("Profile must have at least 1 education entry")
            
        return True

class OutreachValidator:
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email address format"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationError(f"Invalid email format: {email}")
        return True
    
    @staticmethod
    def validate_linkedin_url(url: str) -> bool:
        """Validate LinkedIn profile URL format"""
        linkedin_pattern = r'^https?://(?:www\.)?linkedin\.com/in/[\w\-]+/?$'
        if not re.match(linkedin_pattern, url):
            raise ValidationError(f"Invalid LinkedIn URL format: {url}")
        return True
    
    @staticmethod
    def validate_message_content(content: Dict) -> bool:
        """Validate message content"""
        required_fields = ['subject', 'body']
        
        # Check required fields
        for field in required_fields:
            if not content.get(field):
                raise ValidationError(f"Missing required field in message: {field}")
            
        # Check content length
        if len(content['body']) < 50:
            raise ValidationError("Message body too short")
            
        if len(content['subject']) < 5:
            raise ValidationError("Subject line too short")
            
        return True

class CompanyResearchValidator:
    @staticmethod
    def validate_company_info(info: Dict) -> bool:
        """Validate company research data"""
        required_fields = ['company_info', 'role_analysis', 'recent_news']
        
        # Check required fields
        for field in required_fields:
            if field not in info:
                raise ValidationError(f"Missing required field in company research: {field}")
                
        # Validate news data
        if not isinstance(info['recent_news'], list):
            raise ValidationError("Recent news must be a list")
            
        return True

def validate_pipeline_input(role: str, location: str, max_jobs: int) -> bool:
    """Validate pipeline input parameters"""
    if not role or len(role) < 3:
        raise ValidationError("Role must be at least 3 characters")
        
    if not location or len(location) < 3:
        raise ValidationError("Location must be at least 3 characters")
        
    if max_jobs < 1 or max_jobs > 50:
        raise ValidationError("max_jobs must be between 1 and 50")
        
    return True 