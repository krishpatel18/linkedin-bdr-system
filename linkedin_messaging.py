import smtplib
from email.message import EmailMessage
import requests
import os
import json
from datetime import date
from openai import OpenAI
from dotenv import load_dotenv

# Load API keys
load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_key)

# Email credentials (best to use environment variables for real use)
EMAIL_ADDRESS = "XXX@gmail.com"
EMAIL_PASSWORD = "XXXX XXXX XXXX XXXX" #google "gmail account password"

# Function schema for profile generation
profile_functions = [{
    "name": "generate_candidate_profile",
    "description": "Generate a realistic candidate profile for a specific job",
    "parameters": {
        "type": "object",
        "properties": {
            "headline": {"type": "string"},
            "skills": {"type": "array", "items": {"type": "string"}},
            "education": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "school": {"type": "string"},
                        "degree": {"type": "string"},
                        "graduation_year": {"type": "integer"},
                        "gpa": {"type": "string"},
                        "clubs": {"type": "array", "items": {"type": "string"}}
                    }
                }
            },
            "experience": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "company": {"type": "string"},
                        "start_year": {"type": "integer"},
                        "end_year": {"type": "integer"},
                        "summary": {"type": "string"}
                    }
                }
            }
        },
        "required": ["headline", "skills", "education", "experience"]
    }
}]

# Function schema for email generation
email_functions = [{
    "name": "generate_cold_email",
    "description": "Generate a personalized cold email for a job application",
    "parameters": {
        "type": "object",
        "properties": {
            "subject": {"type": "string", "description": "Email subject line"},
            "greeting": {"type": "string", "description": "Professional greeting"},
            "opening": {"type": "string", "description": "Opening paragraph introducing the candidate"},
            "body": {"type": "string", "description": "Main body highlighting relevant experience and skills"},
            "closing": {"type": "string", "description": "Closing paragraph with call to action"},
            "signature": {"type": "string", "description": "Professional signature"}
        },
        "required": ["subject", "greeting", "opening", "body", "closing", "signature"]
    }
}]

def fetch_jobs_from_sheety() -> list:
    print("📥 Fetching jobs from Sheety...")
    sheety_url = "https://api.sheety.co/9b36d771e1301974c839c6f822fda491/linkedInHiringOutreachSheet/information"
    
    response = requests.get(sheety_url)
    response.raise_for_status()
    rows = response.json().get("information", [])
    
    jobs = []
    for row in rows:
        job = {
            "id": row.get("id"),
            "jobTitle": row.get("jobTitle", "").strip(),
            "company": row.get("company", "").strip(),
            "location": row.get("location", "").strip(),
            "jobDescription": row.get("jobDescription", "").strip(),
            "jobLink": row.get("jobLink", "").strip(),
            "hiringTeam": row.get("hiringTeam", "").strip(),
        }
        jobs.append(job)
    
    print(f"✅ Found {len(jobs)} jobs.")
    return jobs

def generate_candidate_profile(job: dict) -> dict:
    today = date.today().strftime("%B %d, %Y")
    
    profile_prompt = f"""
You are a professional recruiter creating realistic candidate profiles. Today is {today}.

Create a comprehensive, fake but believable candidate profile that would be HIGHLY QUALIFIED for this specific role:

Job Title: {job['jobTitle']}
Company: {job['company']}
Location: {job['location']}
Job Description: {job['jobDescription']}

INSTRUCTIONS FOR PROFILE CREATION:
- Create a candidate who has 3-7 years of relevant experience
- Include 2-3 previous jobs that build toward this role logically
- Add 6-10 technical and soft skills that directly match the job requirements
- Include realistic education (degree, GPA between 3.2-3.8, relevant coursework/clubs)
- Make work experience summaries specific and achievement-focused
- Ensure the career progression makes logical sense
- Include some skills/experience that go slightly beyond the minimum requirements
- Make the candidate stand out but not unrealistically perfect

Focus on creating someone who would genuinely be in the top 20% of applicants for this role.
"""
    
    print("🧠 Generating structured candidate profile via function call...")
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": profile_prompt}],
        functions=profile_functions,
        function_call={"name": "generate_candidate_profile"}
    )
    
    args = response.choices[0].message.function_call.arguments
    return json.loads(args)

def generate_cold_email(job: dict, profile: dict) -> dict:
    # Create a candidate name for the email
    candidate_name = "Alex Thompson"  # You can make this dynamic
    candidate_email = "alex.thompson.professional@gmail.com"  # You can make this dynamic
    
    # Extract key information for email generation
    skills_text = ", ".join(profile['skills'][:5])  # Top 5 skills
    recent_experience = profile['experience'][0] if profile['experience'] else {}
    education_text = f"{profile['education'][0]['degree']} from {profile['education'][0]['school']}" if profile['education'] else "Relevant education"
    
    email_prompt = f"""
You are an expert cold email copywriter specializing in job applications. Write a compelling cold outreach email.

YOUR TASK: Create a cold email that will get this candidate noticed by hiring managers and result in an interview request.

CANDIDATE DETAILS:
Name: {candidate_name}
Professional Headline: {profile['headline']}
Top Skills: {skills_text}
Education: {education_text}
Most Recent Role: {recent_experience.get('title', 'Professional Experience')} at {recent_experience.get('company', 'Previous Company')}
Key Achievement: {recent_experience.get('summary', 'Relevant professional experience')}

TARGET JOB:
Position: {job['jobTitle']}
Company: {job['company']}
Location: {job['location']}
Requirements: {job['jobDescription']}
Contact: {job['hiringTeam']}

EMAIL WRITING GUIDELINES:
- Subject line should be attention-grabbing but professional
- Opening must hook the reader immediately - no generic intros
- Focus on VALUE the candidate brings, not what they want
- Use specific metrics/achievements when possible
- Show you researched the company (mention something specific about them)
- Create urgency without being pushy
- End with a confident, specific call-to-action
- Tone: Confident, professional, but human and conversational
- Length: 150-200 words for body (concise but impactful)
- Avoid buzzwords and clichés THIS IS SUPER IMPORTANT
- Make it feel personal, not mass-produced

The email should make the hiring manager think: "I need to meet this person."
"""
    
    print("✉️ Generating personalized cold email...")
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": email_prompt}],
        functions=email_functions,
        function_call={"name": "generate_cold_email"}
    )
    
    args = response.choices[0].message.function_call.arguments
    return json.loads(args)

def send_cold_email(job: dict, email_content: dict, recipient_email: str = None):
    # SAFETY: Always default to test email to prevent accidental sends to real hiring managers
    if not recipient_email:
        recipient_email = 'XX@gmail.com'  # Safe default - your test email
    
    # Create email message
    msg = EmailMessage()
    msg["Subject"] = email_content['subject']
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = recipient_email
    
    # Construct full email body
    full_email_body = f"""{email_content['greeting']}

{email_content['opening']}

{email_content['body']}

{email_content['closing']}

{email_content['signature']}"""
    
    msg.set_content(full_email_body)
    
    print(f"📧 Sending email to {recipient_email}...")
    print(f"📧 Subject: {email_content['subject']}")
    
    try:
        # Connect to Gmail SMTP server and send
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print("✅ Email sent successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {str(e)}")
        return False

def main():
    jobs = fetch_jobs_from_sheety()
    if not jobs:
        print("❌ No jobs found. Exiting.")
        return
    
    # Use the first job for demonstration
    job = jobs[0]
    print(f"\n🎯 Processing job: {job['jobTitle']} at {job['company']}")
    
    # Generate candidate profile
    profile = generate_candidate_profile(job)
    print("\n🎭 Generated Candidate Profile:")
    print(json.dumps(profile, indent=2))
    
    # Generate cold email
    email_content = generate_cold_email(job, profile)
    print("\n✉️ Generated Cold Email:")
    print("="*50)
    print(f"Subject: {email_content['subject']}")
    print("-"*50)
    print(f"{email_content['greeting']}\n")
    print(f"{email_content['opening']}\n")
    print(f"{email_content['body']}\n")
    print(f"{email_content['closing']}\n")
    print(f"{email_content['signature']}")
    print("="*50)
    
    # Ask for confirmation before sending
    send_confirmation = input("\n🤔 Do you want to send this email? (y/n): ").lower().strip()
    
    if send_confirmation == 'y':
        # SAFETY NOTE: Default recipient is your test email for safe testing
        recipient = input("📧 Enter recipient email (or press Enter for safe test email nickyoogle@gmail.com): ").strip()
        if not recipient:
            recipient = 'nickyoogle@gmail.com'  # Safe default for testing
        
        success = send_cold_email(job, email_content, recipient)
        if success:
            print("🎉 Cold email campaign completed successfully!")
        else:
            print("😞 Email sending failed. Please check your credentials and try again.")
    else:
        print("📝 Email generated but not sent. You can copy the content above to send manually.")

if __name__ == "__main__":
    main()