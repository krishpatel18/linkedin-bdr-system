import argparse
import os
from dotenv import load_dotenv
from pipeline import LinkedInOutreachPipeline
from config import Config
import logging
from validators import ValidationError

def setup_logging():
    """Configure logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('linkedin_outreach.log'),
            logging.StreamHandler()
        ]
    )

def validate_environment():
    """Validate that all required environment variables are set"""
    if not Config.validate_config():
        print("\nPlease set up your .env file with the required credentials.")
        print("You can copy .env.example and fill in your values.")
        exit(1)

def get_user_input():
    """Get job search parameters from user"""
    print("\n=== LinkedIn Job Search Parameters ===")
    
    # Get role
    while True:
        role = input("\nEnter job role (e.g., 'Software Engineer'): ").strip()
        if len(role) >= 3:
            break
        print("Role must be at least 3 characters long.")
    
    # Get location
    print("\nAvailable Locations:")
    for loc in Config.LOCATIONS.keys():
        print(f"- {loc}")
    
    while True:
        location = input("\nEnter location from the list above: ").strip()
        if location in Config.LOCATIONS:
            break
        print("Please select a location from the list above.")
    
    # Get number of jobs
    while True:
        try:
            max_jobs = int(input("\nNumber of jobs to process (1-50): ").strip())
            if 1 <= max_jobs <= 50:
                break
            print("Please enter a number between 1 and 50.")
        except ValueError:
            print("Please enter a valid number.")
    
    return role, location, max_jobs

def run_pipeline_interactive():
    """Run the pipeline in interactive mode"""
    print("\n=== LinkedIn Automated BDR System ===")
    
    # Validate environment
    validate_environment()
    
    # Get user input
    role, location, max_jobs = get_user_input()
    
    # Confirm settings
    print("\nPipeline Settings:")
    print(f"Role: {role}")
    print(f"Location: {location}")
    print(f"Number of jobs: {max_jobs}")
    
    confirm = input("\nProceed with these settings? (y/n): ").lower().strip()
    if confirm != 'y':
        print("Pipeline cancelled.")
        return
    
    # Initialize and run pipeline
    try:
        pipeline = LinkedInOutreachPipeline()
        pipeline.run_pipeline(role, location, max_jobs)
        print("\nPipeline completed successfully!")
        print("Check linkedin_outreach.log for detailed information.")
    except ValidationError as e:
        print(f"\nValidation Error: {str(e)}")
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("Check linkedin_outreach.log for error details.")

def run_pipeline_cli():
    """Run the pipeline with command line arguments"""
    parser = argparse.ArgumentParser(description='LinkedIn Automated BDR System')
    parser.add_argument('--role', required=True, help='Job role to search for')
    parser.add_argument('--location', required=True, help='Location to search in')
    parser.add_argument('--max-jobs', type=int, default=5, help='Number of jobs to process (1-50)')
    
    args = parser.parse_args()
    
    try:
        pipeline = LinkedInOutreachPipeline()
        pipeline.run_pipeline(args.role, args.location, args.max_jobs)
        print("Pipeline completed successfully!")
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)

if __name__ == "__main__":
    setup_logging()
    
    # Check if command line arguments were provided
    if len(os.sys.argv) > 1:
        run_pipeline_cli()
    else:
        run_pipeline_interactive() 