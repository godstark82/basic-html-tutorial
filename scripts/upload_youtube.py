from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google import genai
import os
import json
import logging
from google.auth.transport.requests import Request

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# OAuth 2.0 credentials
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
CLIENT_SECRETS_FILE = "client_secrets.json"

# Video details
VIDEO_PATH = "generated/videos/final_video.mp4"
GEMINI_MODEL = os.getenv('GEMINI_MODEL')
YOUTUBE_TOKEN = os.getenv('YOUTUBE_TOKEN')
if not GEMINI_MODEL:
    raise ValueError("GEMINI_MODEL not set")

def get_video_details():
    """Get video title and description using Gemini AI based on current topic"""
    try:
        # Read current topic
        with open('./generated_topic.txt', 'r') as f:
            topic = f.read().strip()
            
        client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
        
        # Generate title prompt
        title_prompt = f"""Create a catchy YouTube Shorts title for a video explaining '{topic}'.
        The title should be engaging, include emojis, and be optimized for reach.
        Keep it under 100 characters. Make it Breaking Bad themed."""
        
        title_response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=title_prompt
        )
        
        # Generate description prompt
        desc_prompt = f"""Create an engaging YouTube Shorts description for a video explaining '{topic}'.
        Include relevant trending hashtags related to:
        - Breaking Bad
        - Full Stack Development
        - Programming
        - Tech Education
        Make it catchy and optimized for reach. Keep it under 500 characters."""
        
        desc_response = client.models.generate_content(
            model=GEMINI_MODEL, 
            contents=desc_prompt
        )
        
        title = title_response.text.strip() if title_response.text.strip() else f"Breaking Bad Explains: {topic} 🧪💻"
        desc = desc_response.text.strip() if desc_response.text.strip() else f"{topic} explained Breaking Bad style! #shorts #coding #breakingbad"
        
        # Validate title is not empty
        if not title or len(title.strip()) == 0:
            title = f"Breaking Bad Explains: {topic} 🧪💻"
            
        return title, desc
        
    except Exception as e:
        logger.error(f"Failed to generate video details: {e}")
        # Read topic from file as fallback
        with open('generated_topic.txt', 'r') as f:
            topic = f.read().strip()
        return f"Breaking Bad Explains: {topic} 🧪💻", f"{topic} explained Breaking Bad style! #shorts #coding #breakingbad"

def get_credentials():
    """Get valid credentials from environment variable or user auth."""
    credentials = None
    
    # Try to load credentials from environment variable
    if YOUTUBE_TOKEN:
        token_data = json.loads(YOUTUBE_TOKEN)
        credentials = Credentials.from_authorized_user_info(token_data, SCOPES)
    
    # If no valid credentials, get new ones
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            credentials = flow.run_local_server(port=0)
        
        # Save credentials to environment variable
        token_json = credentials.to_json()
        # Update YOUTUBE_TOKEN in .env
        env_path = '.env'
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                env_lines = f.readlines()
            
            # Find and replace or append YOUTUBE_TOKEN
            token_updated = False
            for i, line in enumerate(env_lines):
                if line.startswith('YOUTUBE_TOKEN='):
                    env_lines[i] = f'YOUTUBE_TOKEN={token_json}\n'
                    token_updated = True
                    break
            
            if not token_updated:
                env_lines.append(f'\nYOUTUBE_TOKEN={token_json}\n')
                
            with open(env_path, 'w') as f:
                f.writelines(env_lines)
        else:
            with open(env_path, 'w') as f:
                f.write(f'YOUTUBE_TOKEN={token_json}\n')
        logger.info("New credentials generated. Please update YOUTUBE_TOKEN in .env with:")
        logger.info(token_json)
            
    return credentials

def upload_short(video_path: str = VIDEO_PATH):
    try:
        # Get AI generated title and description
        title, description = get_video_details()
        
        # Get credentials and build service
        credentials = get_credentials()
        youtube = build('youtube', 'v3', credentials=credentials)
        
        # Ensure title is not empty and valid
        if not title or len(title.strip()) == 0:
            with open('generated_topic.txt', 'r') as f:
                topic = f.read().strip()
            title = f"Breaking Bad Explains: {topic} 🧪💻"
            
        # Truncate title if too long (YouTube limit is 100 characters)
        title = title[:100]
        
        # Prepare video upload
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': ['shorts', 'coding', 'programming', 'breakingbad', 'techeducation', 'fullstack'],
                'categoryId': '28'  # Science & Technology category
            },
            'status': {
                'privacyStatus': 'public',
                'selfDeclaredMadeForKids': False
            }
        }
        
        # Create MediaFileUpload object
        media = MediaFileUpload(video_path, 
                              mimetype='video/mp4',
                              resumable=True)
        
        # Execute upload
        request = youtube.videos().insert(
            part='snippet,status',
            body=body,
            media_body=media
        )
        
        response = request.execute()
        
        logger.info("Video uploaded to YouTube successfully!")
        logger.info(f"Video URL: https://youtu.be/{response['id']}")
        logger.info(f"Title: {title}")
        logger.info(f"Description: {description}")
        
    except Exception as e:
        logger.error(f"Failed to upload Short: {e}")

if __name__ == "__main__":
    upload_short()
