
"""
Configuration settings for the YouTube script generation project.
This file contains all the necessary parameters for script generation, video settings, and character configurations.
"""

# YouTube Video Settings
YOUTUBE_SETTINGS = {
    "background_video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
}

# Character Settings
CHARACTERS = {
    "character1": {
        "name": "walter",
        "image_path": "samples/images/walter.png",  
        "audio_json_path": "samples/audio/walter.json",
    },
    "character2":{
        "name": "jesse",
        "image_path": "samples/images/jesse.png",
        "audio_json_path": "samples/audio/jesse.json",
    }
}

# Script Generation Settings
SCRIPT_SETTINGS = {
    "language": "en",
    "tone": "humorous",
    "target_audience": "18-24 year old male",
    "keywords": ["funny", "humor", "comedy"],
}

# Content Generation Notes
CONTENT_NOTES = {
    "main_topic": "FullStack Development",  
    "subtopics": ["Frontend Development", "Backend Development", "Database Development", "DevOps"],  
    "key_points": ["Frontend Development", "Backend Development", "Database Development", "DevOps"], 
    "special_instructions": """
    The script should be funny and humorous in walter white and jesse pinkman style from breaking bad series
    The script should be in english
    """,
    "references": [],  
}

GLOBAL_CONFIG = {
    "YOUTUBE_SETTINGS": YOUTUBE_SETTINGS,
    "CHARACTERS": CHARACTERS,
    "SCRIPT_SETTINGS": SCRIPT_SETTINGS,
}