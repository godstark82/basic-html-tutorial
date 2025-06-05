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

# Credentials
USERNAME = "fullstackwalter"
PASSWORD = "Lk@328001"
SESSION_FILE = f"{USERNAME}_session.json"

# Path to the video
VIDEO_PATH = "./final_video.mp4"

def generate_caption():
    try:
        with open('./generated/scripts/generated_script.json', 'r') as f:
            script = json.load(f)

        dialogue = ""
        for line in script.values():
            if 'walter' in line:
                dialogue += f"Walter: {line['walter']}\n"
            elif 'jesse' in line:
                dialogue += f"Jesse: {line['jesse']}\n"

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

def login_with_session(cl: Client):
    if os.path.exists(SESSION_FILE):
        try:
            cl.load_settings(SESSION_FILE)
            cl.login(USERNAME, PASSWORD)
            print("✅ Logged in using saved session.")
        except Exception as e:
            print("⚠️ Failed to login using saved session. Retrying fresh login...")
            cl.set_settings({})
            cl.login(USERNAME, PASSWORD)
            cl.dump_settings(SESSION_FILE)
            print("✅ Logged in fresh and saved new session.")
    else:
        cl.login(USERNAME, PASSWORD)
        cl.dump_settings(SESSION_FILE)
        print("✅ Logged in and saved new session.")

def upload_reel(video_path: str = VIDEO_PATH):
    try:
        # Generate caption
        caption = generate_caption()

        # Instagram Client
        cl = Client()
        login_with_session(cl)

        # Upload the Reel
        media = cl.clip_upload(video_path, caption)

        print("✅ Reel uploaded successfully!")
        print("📎 Reel URL:", f"https://www.instagram.com/reel/{media.pk}/")
        print("📝 Used caption:", caption)

    except Exception as e:
        print("❌ Failed to upload Reel:")
        print(e)

if __name__ == "__main__":
    upload_reel()
