# LinkedIn Automated BDR System

An AI-powered automation pipeline for identifying and engaging with job postings on LinkedIn. This system automates the entire process of job searching, company research, profile generation, and multi-channel outreach.

## 🌟 Features

- 🤖 Automated job scraping from LinkedIn
- 🔍 AI-powered company and role research
- 👤 Synthetic candidate profile generation
- 📧 Multi-channel outreach (Email + LinkedIn)
- 📅 Automated follow-up scheduling
- 📈 Sentiment analysis of company news
- 📊 Data tracking via Google Sheets

## 🚀 Prerequisites

- Python 3.8+
- Gmail account with App Password enabled
- LinkedIn account
- Required API keys (see Configuration section)

## ⚙️ Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/linkedin-bdr-system.git
cd linkedin-bdr-system
```

2. Create and activate a virtual environment:
```bash
# On macOS/Linux
python -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
.\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

## 🔑 Required API Keys

1. **OpenAI API Key**
   - Sign up at [OpenAI](https://platform.openai.com/)
   - Get API key from dashboard

2. **News API Key**
   - Register at [NewsAPI](https://newsapi.org/)
   - Get API key from account settings

3. **Hunter.io API Key**
   - Sign up at [Hunter](https://hunter.io/)
   - Get API key from dashboard

4. **ScrapingDog API Key**
   - Register at [ScrapingDog](https://scrapingdog.com/)
   - Get API key from account settings

5. **PhantomBuster API Key**
   - Sign up at [PhantomBuster](https://phantombuster.com/)
   - Get API key from settings

## 📧 Email Setup

1. Enable 2FA on your Gmail account
2. Generate App Password:
   - Go to Google Account settings
   - Security → 2-Step Verification
   - Scroll to App passwords
   - Generate new app password for "Mail"
   - Copy password to .env file

## 📊 Google Sheet Setup

1. Create a new Google Sheet
2. Go to [Sheety](https://sheety.co/)
3. Connect your Google Sheet
4. Get your Sheety API URL
5. Add URL to .env file

## 🚀 Usage

### Interactive Mode
```bash
python main.py
```
Follow the prompts to:
- Enter job role
- Select location
- Set number of jobs to process

### Command Line Mode
```bash
python main.py --role "Software Engineer" --location "San Francisco Bay Area" --max-jobs 5
```

## 📁 Project Structure

```
linkedin-bdr-system/
├── main.py                 # Main entry point
├── pipeline.py            # Pipeline orchestration
├── getting_info.py        # Job scraping
├── company_research.py    # Company analysis
├── profile_generator.py   # Profile generation
├── outreach_manager.py    # Email/LinkedIn messaging
├── config.py             # Configuration
├── validators.py         # Input validation
├── requirements.txt      # Dependencies
└── .env.example         # Environment template
```

## ⚠️ Rate Limiting

The system implements rate limiting to respect API limits:
- 2-second delay between job processing
- Exponential backoff for failed API calls
- Maximum 3 retry attempts

## 🔍 Monitoring

- Check `linkedin_outreach.log` for detailed logs
- Monitor your Google Sheet for:
  - Job listings
  - Company research
  - Generated profiles
  - Outreach status
  - Follow-up schedules

## ⚡ Best Practices

1. Always test with a small number of jobs first
2. Monitor the logs for any rate limiting or API issues
3. Keep your API keys and credentials secure
4. Regularly check your Google Sheet for status updates
5. Review generated content before sending

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT-4 API
- LinkedIn for platform access
- All API service providers 