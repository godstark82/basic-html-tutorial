import os
import outetts
import torch
import json
from pydub import AudioSegment
from outetts.models import hf_model
from scripts.config import *


def generate_voiceover() -> str:
    """
    Generate voiceovers for characters using Outetts and combine them into a single audio file.
    Each dialogue is generated and stored separately, then combined in sequence.
    Returns the path to the combined audio file.
    """
    try:
        script_path = 'generated/scripts/generated_script.json'
        audios_path = 'generated/audios'
        
        # remove everything inside generated/audios
        for file in os.listdir(audios_path):
            os.remove(os.path.join(audios_path, file))
        
        # Initialize Outetts
        interface = outetts.Interface(
            config=outetts.ModelConfig(
                model_path="OuteAI/Llama-OuteTTS-1.0-1B", 
                tokenizer_path="OuteAI/Llama-OuteTTS-1.0-1B",
                interface_version=outetts.InterfaceVersion.V3,
                backend=outetts.Backend.HF,
                quantization=outetts.LlamaCppQuantization.FP16,
                device=torch.device("cuda" if torch.cuda.is_available() else "cpu"),
                dtype=torch.bfloat16
            )
        )

        # Load speaker profiles
        character1_speaker = interface.load_speaker(CHARACTERS["character1"]["audio_json_path"])
        character2_speaker = interface.load_speaker(CHARACTERS["character2"]["audio_json_path"])
        
        # Read the script
        with open(script_path, 'r') as f:
            script = json.load(f)
            
        # Validate script format
        if not isinstance(script, dict):
            raise ValueError("Script must be a dictionary with numbered keys")
            
        audio_segments = []
        
        # Process each dialogue in order
        for key in sorted(script.keys(), key=int):
            dialogue = script[key]
            
            # Determine character and get appropriate speaker
            if 'walter' in dialogue:
                character = CHARACTERS["character1"]["name"]
                speaker = character1_speaker
                text = dialogue['walter']
            elif 'jesse' in dialogue:
                character = CHARACTERS["character2"]["name"]
                speaker = character2_speaker
                text = dialogue['jesse']
            else:
                raise ValueError(f"Dialogue {key} must contain either {CHARACTERS['character1']['name']} or {CHARACTERS['character2']['name']}")
            
            # Generate audio for the line
            audio = interface.generate(
                config=outetts.GenerationConfig(
                    text=text,
                    speaker=speaker,
                )
            )
            
            # Save individual audio file
            individual_file = f"{audios_path}/{key}_{character}.wav"
            audio.save(individual_file)
            print(f"Saved individual audio to {individual_file}")
            
            # Load audio segment
            segment = AudioSegment.from_wav(individual_file)
            audio_segments.append(segment)
        
        # Combine all segments in sequence
        combined = AudioSegment.empty()
        for segment in audio_segments:
            combined += segment
        
        # Export the combined audio
        combined.export('generated/audios/combined_voiceover.mp3', format="mp3")
        print(f"Combined voiceover saved to generated/audios/combined_voiceover.mp3")
        
        return 'generated/audios/combined_voiceover.mp3'
            
    except Exception as e:
        print(f"Voiceover generation failed: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        output_file = generate_voiceover()
        print(f"Voiceover generated successfully: {output_file}")
    except Exception as e:
        print(f"Voiceover generation failed: {str(e)}")
        raise