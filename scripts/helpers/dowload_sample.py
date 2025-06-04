import os
from pytube import YouTube

def download_sample_video(youtube_url):
    # Check if video already exists
    video_path = 'samples/video/video.mp4'
    if os.path.exists(video_path):
        print("Sample video already exists, skipping download")
        return
        
    try:
        # Create samples/video directory if it doesn't exist
        os.makedirs('samples/video', exist_ok=True)
        
        # Initialize YouTube object
        yt = YouTube(youtube_url)
        
        # Get the highest resolution stream
        video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        
        # Download the video
        print(f"Downloading: {yt.title}")
        video.download(output_path='samples/video', filename='video.mp4')
        print("Download completed successfully!")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Replace with your desired YouTube video URL
    download_sample_video(video_url)

