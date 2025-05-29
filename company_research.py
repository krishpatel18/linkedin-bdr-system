import os
from typing import Dict, List
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

logger = logging.getLogger(__name__)

class CompanyResearcher:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        
    def get_company_info(self, company_name: str) -> Dict:
        """Get comprehensive company information using OpenAI"""
        try:
            prompt = f"""Analyze the company {company_name} and provide:
            1. Company culture and values
            2. Growth trajectory and market position
            3. Technology stack and engineering practices
            4. Recent achievements or milestones
            5. Competitive advantages
            Format as a structured JSON."""
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            return eval(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Failed to get company info: {str(e)}")
            return {}
            
    def analyze_role(self, job_description: str) -> Dict:
        """Analyze job requirements and expectations"""
        try:
            prompt = f"""Analyze this job description and provide:
            1. Key technical requirements
            2. Soft skills needed
            3. Experience level expected
            4. Unique aspects of the role
            5. Team structure hints
            Format as a structured JSON.
            
            Description: {job_description}"""
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            return eval(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Failed to analyze role: {str(e)}")
            return {}
            
    def get_company_news(self, company_name: str) -> List[Dict]:
        """Get recent news about the company"""
        try:
            url = f"https://newsapi.org/v2/everything"
            params = {
                "q": company_name,
                "sortBy": "publishedAt",
                "apiKey": NEWS_API_KEY,
                "language": "en",
                "pageSize": 5
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            news_data = response.json()
            
            # Process and analyze news sentiment
            articles = []
            for article in news_data.get("articles", []):
                # Analyze sentiment of the article
                sentiment = self._analyze_news_sentiment(article["title"] + " " + article["description"])
                
                articles.append({
                    "title": article["title"],
                    "date": article["publishedAt"],
                    "url": article["url"],
                    "sentiment": sentiment
                })
                
            return articles
        except Exception as e:
            logger.error(f"Failed to get company news: {str(e)}")
            return []
            
    def _analyze_news_sentiment(self, text: str) -> str:
        """Analyze sentiment of news article using OpenAI"""
        try:
            prompt = f"""Analyze the sentiment of this news text and classify as POSITIVE, NEGATIVE, or NEUTRAL:
            {text}"""
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Failed to analyze sentiment: {str(e)}")
            return "NEUTRAL" 