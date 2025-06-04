from google import genai
import os
import json
from pathlib import Path

from scripts.config import *

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


def generate_script(topic: str) -> dict:
    """
    Generate a script for Walter White and Jesse Pinkman discussing the given fullstack development topic.
    Returns a dictionary with numbered dialogues containing character lines.
    """
    prompt = f"""Create a {SCRIPT_SETTINGS['tone']} yet educational script about {topic}.
    The script should be in {SCRIPT_SETTINGS['language']} and should be completed within 55-60 seconds.
    Target audience: {SCRIPT_SETTINGS['target_audience']}
    There should be 2 characters in the script one is {CHARACTERS['character1']['name']} and the other is {CHARACTERS['character2']['name']}.
    
    {CONTENT_NOTES['special_instructions']}
    
    Format the response as a valid JSON with numbered dialogues, each containing the character's line.
    
    Example format:
    {{
        "1": {{
            "walter": "Jesse, listen carefully. Let me explain React Hooks."
        }},
        "2": {{
            "jesse": "Yo! Mister White! What are Hooks?"
        }},
        "3": {{
            "walter": "They're the future of React components, Jesse!"
        }}
    }}
    """
    
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )
        
        # Try to parse the response as JSON
        try:
            script = json.loads(response.text)
        except json.JSONDecodeError:
            # If JSON parsing fails, try to clean the response
            cleaned_text = response.text.strip()
            # Remove any markdown code block markers
            cleaned_text = cleaned_text.replace('```json', '').replace('```', '').strip()
            try:
                script = json.loads(cleaned_text)
            except json.JSONDecodeError as e:
                print(f"Invalid JSON response: {response.text}")
                raise ValueError(f"Failed to parse script as JSON: {str(e)}")
        
        # Validate script structure
        if not isinstance(script, dict):
            raise ValueError("Script must be a dictionary")
        
        # Validate each dialogue entry
        for dialogue_num, dialogue in script.items():
            if not isinstance(dialogue, dict):
                raise ValueError(f"Dialogue {dialogue_num} must be a dictionary")
            
            if not any(char in dialogue for char in ['walter', 'jesse']):
                raise ValueError(f"Dialogue {dialogue_num} must have either walter or jesse")
        
        return script
        
    except Exception as e:
        print(f"Script generation failed: {str(e)}")
        raise

def save_script(script: dict) -> None:
    """
    Save the generated script to a JSON file.
    """
    try:
        output_path = os.path.join('generated/scripts', 'generated_script.json')
        with open(output_path, 'w') as f:
            json.dump(script, f, indent=4)
        print(f"Script saved to {output_path}")
    except Exception as e:
        print(f"Failed to save script: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        script = generate_script('React in Frontend Development')
        save_script(script)
        print("Script generated and saved successfully")
    except Exception as e:
        print(f"Script generation failed: {str(e)}")
        raise 