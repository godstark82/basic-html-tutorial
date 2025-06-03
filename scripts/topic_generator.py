from google import genai
import os
import json
from error_handler import handle_errors, logging

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
    logging.error(f"Gemini client failed: {str(e)}")
    raise

TOPICS_FILE = "data/used_topics.json"
GENERATED_TOPIC_FILE = "generated_topic.txt"

@handle_errors("TopicGenerator")
def generate_topic(user_topic: str = None) -> str:
    """
    Generate a random development topic using Gemini AI, ensuring it hasn't been used before.
    """
    try:
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        # Load used topics
        used_topics = set()
        if os.path.exists(TOPICS_FILE):
            with open(TOPICS_FILE, 'r') as f:
                used_topics = set(json.load(f))
        
        # If user provided a topic, use it
        if user_topic:
            if user_topic in used_topics:
                logging.warning(f"Topic '{user_topic}' has been used before")
            # Save user topic to both files
            with open(GENERATED_TOPIC_FILE, 'w') as f:
                f.write(user_topic)
            used_topics.add(user_topic)
            with open(TOPICS_FILE, 'w') as f:
                json.dump(list(used_topics), f)
            return user_topic
        
        # Generate new topic using Gemini
        prompt = """Generate a unique fullstack development topic that can be explained in 1 minute.
        Format the topic in English.
        The topic should be related to fullstack web development, programming, or software engineering.
        Return ONLY the topic name, nothing else."""
        
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )
        
        topic = response.text.strip()
        
        # Keep generating until we get a unique topic
        max_attempts = 5
        attempts = 0
        while topic in used_topics and attempts < max_attempts:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt
            )
            topic = response.text.strip()
            attempts += 1
        
        if attempts >= max_attempts:
            # If we can't generate a unique topic, clear the used topics
            used_topics.clear()
            with open(TOPICS_FILE, 'w') as f:
                json.dump(list(used_topics), f)
            logging.info("Cleared used topics due to difficulty generating new unique topic")
        
        # Add new topic to used topics and save to both files
        used_topics.add(topic)
        with open(TOPICS_FILE, 'w') as f:
            json.dump(list(used_topics), f)
            
        # Save current topic to generated_topic.txt
        with open(GENERATED_TOPIC_FILE, 'w') as f:
            f.write(topic)
        
        logging.info(f"Generated new topic: {topic}")
        return topic
        
    except Exception as e:
        logging.error(f"Topic generation failed: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        topic = generate_topic()
        print(f"Generated topic: {topic}")
    except Exception as e:
        logging.error(f"Topic generation failed: {str(e)}")
        raise 