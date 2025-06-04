import os
import argparse
from scripts.upload_instagram import upload_reel
from scripts.upload_youtube import upload_short
from scripts.error_handler import handle_errors, logging
from scripts.topic_generator import generate_topic
from scripts.script_generator import generate_script, save_script
from scripts.voiceover_generator import generate_voiceover
from scripts.video_generator import generate_video

# Create necessary directories
os.makedirs("generated", exist_ok=True)
os.makedirs("generated/audios", exist_ok=True)
os.makedirs("generated/videos", exist_ok=True)
os.makedirs("generated/scripts", exist_ok=True)
os.makedirs("generated/topics", exist_ok=True)

@handle_errors("MainWorkflow")
def run_workflow(start_task: int = 1) -> dict:
    """
    Run the workflow from a specified task number.
    Args:
        start_task: Task number to start from (1-6)
    Returns a dictionary with the status of each step and output paths.
    """
    try:
        result = {
            "status": "success",
            "topic": None,
            "script_path": "generated/scripts/generated_script.json",
            "audio_path": "generated/audios/combined_voiceover.mp3",
            "video_path": "generated/videos/final_video.mp4"
        }
        
        # Step 1: Generate topic
        if start_task <= 1:
            logging.info("Generating topic...")
            topic = generate_topic()
            result["topic"] = topic
            logging.info(f"Generated topic: {topic}")
        
        # Step 2: Generate script
        if start_task <= 2:
            logging.info("Generating script...")
            script = generate_script(result["topic"])
            save_script(script, result["script_path"])
            logging.info(f"Script saved to {result['script_path']}")
        
        # Step 3: Generate voiceover
        if start_task <= 3:
            logging.info("Generating voiceover...")
            audio_file = generate_voiceover(result["script_path"], result["audio_path"])
            result["audio_path"] = audio_file
            logging.info(f"Voiceover saved to {audio_file}")
        
        # Step 4: Generate video
        if start_task <= 4:
            logging.info("Generating video...")
            video_file = generate_video(
                background_video="samples/video.mp4",
                audio_file=result["audio_path"],
                script_file=result["script_path"],
                output_path=result["video_path"]
            )
            result["video_path"] = video_file
            logging.info(f"Video saved to {video_file}")
        
        # Step 5: Upload video to Instagram
        if start_task <= 5:
            logging.info("Uploading video to Instagram...")
            upload_reel(result["video_path"])
            logging.info("Video uploaded to Instagram successfully!")
        
        # Step 6: Upload video to YouTube
        if start_task <= 6:
            logging.info("Uploading video to YouTube...")
            upload_short(result["video_path"])
            logging.info("Video uploaded to YouTube successfully!")
        
        return result
        
    except Exception as e:
        logging.error(f"Workflow failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }

def main():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("-task", type=int, default=1, help="Task number to start from (1-6)")
        args = parser.parse_args()
        
        if not 1 <= args.task <= 6:
            raise ValueError("Task number must be between 1 and 6")
            
        result = run_workflow(args.task)
        if result["status"] == "success":
            print("\nWorkflow completed successfully!")
            if result["topic"]:
                print(f"Topic: {result['topic']}")
            print(f"Script: {result['script_path']}")
            print(f"Audio: {result['audio_path']}")
            print(f"Video: {result['video_path']}")
        else:
            print(f"\nWorkflow failed: {result['error']}")
    except Exception as e:
        logging.error(f"Main workflow failed: {str(e)}")
        raise
    
if __name__ == "__main__":
    main()