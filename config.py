import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration management for the application"""
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    NEWS_API_KEY = os.getenv("NEWS_API_KEY")
    HUNTER_API_KEY = os.getenv("HUNTER_API_KEY")
    SCRAPINGDOG_API_KEY = os.getenv("SCRAPINGDOG_API_KEY")
    PHANTOMBUSTER_API_KEY = os.getenv("PHANTOMBUSTER_API_KEY")
    
    # Email Configuration
    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 465
    
    # LinkedIn Configuration
    LINKEDIN_USERNAME = os.getenv("LINKEDIN_USERNAME")
    LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")
    
    # Sheety Configuration
    SHEETY_URL = os.getenv("SHEETY_URL")
    
    # Application Settings
    MAX_JOBS_PER_RUN = int(os.getenv("MAX_JOBS_PER_RUN", "5"))
    RATE_LIMIT_DELAY = int(os.getenv("RATE_LIMIT_DELAY", "2"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    
    # Location IDs
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
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that all required configuration is present"""
        required_keys = [
            "OPENAI_API_KEY",
            "NEWS_API_KEY",
            "HUNTER_API_KEY",
            "SCRAPINGDOG_API_KEY",
            "PHANTOMBUSTER_API_KEY",
            "EMAIL_ADDRESS",
            "EMAIL_PASSWORD",
            "LINKEDIN_USERNAME",
            "LINKEDIN_PASSWORD",
            "SHEETY_URL"
        ]
        
        missing_keys = []
        for key in required_keys:
            if not getattr(cls, key):
                missing_keys.append(key)
                
        if missing_keys:
            print(f"Missing required configuration: {', '.join(missing_keys)}")
            return False
            
        return True
    
    @classmethod
    def get_environment(cls) -> str:
        """Get current environment"""
        return os.getenv("ENVIRONMENT", "development")
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production"""
        return cls.get_environment().lower() == "production"
    
    @classmethod
    def get_api_settings(cls) -> Dict[str, Any]:
        """Get API-related settings"""
        return {
            "max_retries": cls.MAX_RETRIES,
            "rate_limit_delay": cls.RATE_LIMIT_DELAY,
            "timeout": 30 if cls.is_production() else 10
        }
    
    @classmethod
    def get_email_settings(cls) -> Dict[str, Any]:
        """Get email-related settings"""
        return {
            "smtp_server": cls.SMTP_SERVER,
            "smtp_port": cls.SMTP_PORT,
            "email": cls.EMAIL_ADDRESS,
            "password": cls.EMAIL_PASSWORD
        }
    
    @classmethod
    def get_linkedin_settings(cls) -> Dict[str, Any]:
        """Get LinkedIn-related settings"""
        return {
            "username": cls.LINKEDIN_USERNAME,
            "password": cls.LINKEDIN_PASSWORD
        } 