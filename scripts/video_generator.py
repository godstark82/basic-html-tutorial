import os
import moviepy.config
from moviepy.video.fx.resize import resize
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ImageClip
import json
import moviepy
from pydub import AudioSegment
from pydub.utils import mediainfo
from scripts.helpers.dowload_sample import download_sample_video
import scripts.config as config

IMAGE_MAGICK_PATH = os.getenv('IMAGEMAGICK_BINARY')

if not IMAGE_MAGICK_PATH:
    raise ValueError("IMAGEMAGICK_BINARY is not set")

moviepy.config.IMAGEMAGICK_BINARY = IMAGE_MAGICK_PATH


def generate_video(
    audio_file: str, 
    script_file: str,
    output_path: str = "final_video.mp4"
) -> str:
    """
    Generate a vertical video with background footage, audio, subtitles and character images.
    Returns the path to the generated video.
    """
    background_video_url = config.YOUTUBE_SETTINGS['background_video_url']
    try:
        download_sample_video(background_video_url)
        
        # Load the script
        with open(script_file, 'r') as f:
            script = json.load(f)
        
        # Load video and audio
        video = VideoFileClip('samples/video/video.mp4')
        audio = AudioFileClip(audio_file)
        
        # Load character images and scale them appropriately
        character1_img = ImageClip(config.CHARACTERS["character1"]["image_path"]).resize(width=video.w * 0.45).set_position(('left', 'bottom'))
        character2_img = ImageClip(config.CHARACTERS["character2"]["image_path"]).resize(width=video.w * 0.45).set_position(('right', 'bottom'))
        
        # Crop video to 9:16 aspect ratio (1440x2560 for 1440p)
        w, h = video.size
        target_w = h * 9/16
        x_center = w/2
        crop_x1 = x_center - target_w/2
        video = video.crop(x1=crop_x1, width=target_w)
        
        # Resize to 1440p while maintaining 9:16 aspect ratio
        video = video.resize(width=1440)  # Height will automatically be 2560 to maintain aspect ratio
        
        # Trim video to match audio duration
        video = video.subclip(0, audio.duration)
        
        # Create subtitle and character clips
        subtitle_clips = []
        character_clips = []
        current_time = 0
        
        # Style for Character1's subtitles
        character1_style = {
            'font': 'Arial-Bold',
            'fontsize': 85,  # Increased font size for higher resolution
            'color': 'white',
            'stroke_color': 'black',
            'stroke_width': 4,  # Increased stroke width for better visibility
            'size': (video.w * 0.8, None),
            'method': 'caption',
            'align': 'center',
        }
        
        # Style for Character2's subtitles
        character2_style = {
            'font': 'Arial-Bold', 
            'fontsize': 85,  # Increased font size for higher resolution
            'color': 'yellow',
            'stroke_color': 'black',
            'stroke_width': 4,  # Increased stroke width for better visibility
            'size': (video.w * 0.8, None),
            'method': 'caption',
            'align': 'center',
        }
        
        # Create subtitle clips and character images for each line
        for line_id, line_data in script.items():
            if config.CHARACTERS["character1"]["name"] in line_data:
                text = line_data[config.CHARACTERS["character1"]["name"]].replace('*', '').replace('"', '')
                style = character1_style
                character = config.CHARACTERS["character1"]["name"]
                char_img = character1_img
                position = ('left', 'bottom')  # Left side, at bottom
            else:
                text = line_data[config.CHARACTERS["character2"]["name"]].replace('*', '').replace('"', '')
                style = character2_style
                character = config.CHARACTERS["character2"]["name"]
                char_img = character2_img
                position = ('right', 'bottom')  # Right side, at bottom
                
            # Get audio duration for timing
            audio_path = f"generated/audios/{line_id}_{character}.wav"
            audio_info = mediainfo(audio_path)
            duration = float(audio_info['duration'])
            
            # Create text clip with transparent background
            txt_clip = TextClip(
                text,
                **style
            ).set_start(current_time).set_end(current_time + duration)
            
            # Position the text higher in the video
            txt_clip = txt_clip.set_position(('center', video.h*0.5 - video.h * 0.25))
            subtitle_clips.append(txt_clip)
            
            # Add character image for this line's duration
            char_clip = char_img.set_start(current_time).set_end(current_time + duration)
            char_clip = char_clip.set_position(position)
            char_clip = char_clip.resize(width=video.w * 0.45)
            character_clips.append(char_clip)
            
            # Update timing for next subtitle
            current_time += duration
        
        # Combine all clips
        final_video = CompositeVideoClip([video] + subtitle_clips + character_clips)
        
        # Add audio and ensure sync
        final_video = final_video.set_audio(audio)
        
        # Speed up the video by 1.1x
        final_video = final_video.speedx(factor=1.1)
        
        # Write the result with higher quality settings
        final_video.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            fps=60,
            bitrate="16000k",  # High bitrate for quality
            preset='slow',  # Slower encoding for better quality
            threads=4,
            ffmpeg_params=[
                "-crf", "18"  # Lower CRF value for higher quality (range 0-51, lower is better)
            ]
        )
        
        # Close clips
        video.close()
        audio.close()
        final_video.close()
        character1_img.close()
        character2_img.close()
        
        print(f"Video generated successfully: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"Video generation failed: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        output_file = generate_video(
            audio_file="combined_voiceover.mp3",
            script_file="test_script.json"
        )
        print(f"Video generated successfully: {output_file}")
    except Exception as e:
        print(f"Video generation failed: {str(e)}")
        raise