from instagrapi import Client
import json
from google import genai
import os

# Configure Gemini API
GOOGLE_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL = os.getenv('GEMINI_MODEL')
if not GOOGLE_API_KEY:
    raise ValueError("GEMINI_API_KEY not set")
if not GEMINI_MODEL:
    raise ValueError("GEMINI_MODEL not set")

try:
    client = genai.Client(api_key=GOOGLE_API_KEY)
except Exception as e:
    print(f"Gemini client failed: {str(e)}")
    raise

# Credentials (make sure to use environment variables or a secure method in production)
USERNAME = "fullstackwalter"
PASSWORD = "Lk@328001"

# Path to the video (must be under 90 seconds for Reels)
VIDEO_PATH = "./final_video.mp4"

def generate_caption():
    try:
        # Read the script file
        with open('./generated/scripts/generated_script.json', 'r') as f:
            script = json.load(f)
        
        # Extract dialogue
        dialogue = ""
        for line in script.values():
            if 'walter' in line:
                dialogue += f"Walter: {line['walter']}\n"
            elif 'jesse' in line:
                dialogue += f"Jesse: {line['jesse']}\n"
                
        # Generate caption using Gemini
        prompt = f"""
        Based on this Breaking Bad dialogue:
        {dialogue}
        
        Generate an engaging Instagram reel caption that:
        1. Captures the essence of the scene
        2. Uses relevant Breaking Bad references
        3. Includes trending hashtags
        4. Is engaging and shareable
        5. Maximum 300 characters
        """
        
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )
        return response.text
        
    except Exception as e:
        print(f"Error generating caption: {e}")
        return "Breaking Bad Teaching You How To Be A Good Person 🎬 #BreakingBad #WalterWhite #JessePinkman #AI #viral"

def upload_reel(video_path: str = VIDEO_PATH):
    try:
        # Generate dynamic caption
        caption = generate_caption()
        
        # Initialize client and login
        cl = Client()
        cl.login(USERNAME, PASSWORD)

        # Upload Reel (clip)
        media = cl.clip_upload(video_path, caption)

        print("✅ Reel uploaded successfully!")
        print("📎 Reel URL:", f"https://www.instagram.com/reel/{media.pk}/")
        print("📝 Used caption:", caption)

    except Exception as e:
        print("❌ Failed to upload Reel:")
        print(e)

if __name__ == "__main__":
    upload_reel()
