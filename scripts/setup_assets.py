import os
import shutil
from error_handler import handle_errors, logging
from config import CHARACTERS
import subprocess
from helpers.dowload_sample import download_sample_video
from config import YOUTUBE_SETTINGS

@handle_errors("AssetSetup")
def setup_assets():
    """
    Check and setup required assets - video, audio profiles and images.
    Downloads/creates missing assets and validates their existence.
    """
    # Create required directories
    os.makedirs("samples/video", exist_ok=True) 
    os.makedirs("samples/audio", exist_ok=True)
    os.makedirs("samples/images", exist_ok=True)

    # Check video
    video_path = "samples/video/video.mp4"
    if not os.path.exists(video_path):
        logging.info("Video not found. Downloading sample video...")
        download_sample_video(YOUTUBE_SETTINGS["background_video_url"])
        raise NotImplementedError("Video download not implemented")

    # Check audio profiles
    audio_files_exist = True
    for character in CHARACTERS.values():
        if not os.path.exists(character["audio_json_path"]):
            audio_files_exist = False
            break

    if not audio_files_exist:
        logging.info("Audio profiles not found. Generating speaker profiles...")
        try:
            subprocess.run(["python", "create_speakers.py"], check=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to create speaker profiles: {str(e)}")
            raise

    # Validate images
    for character_name, character_data in CHARACTERS.items():
        image_path = character_data["image_path"]
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Required image not found: {image_path}")

    logging.info("All assets validated successfully")

if __name__ == "__main__":
    setup_assets()
