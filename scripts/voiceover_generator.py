import os
import outetts
import torch
from error_handler import handle_errors, logging
import json
from pydub import AudioSegment
from outetts.models import hf_model

@handle_errors("VoiceoverGenerator")
def generate_voiceover(script_path: str, output_path: str = "combined_voiceover.mp3") -> str:
    """
    Generate voiceovers for Walter White and Jesse Pinkman using Outetts and combine them into a single audio file.
    Each dialogue is generated and stored separately, then combined in sequence.
    Returns the path to the combined audio file.
    """
    try:
        # Create output directories if they don't exist
        os.makedirs("generated/audios", exist_ok=True)
        
        # remove everything inside generated/audios
        for file in os.listdir("generated/audios"):
            os.remove(os.path.join("generated/audios", file))
        
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
        walter_speaker = interface.load_speaker("samples/walter.json")
        jesse_speaker = interface.load_speaker("samples/jesse.json")
        
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
                character = 'walter'
                speaker = walter_speaker
                text = dialogue['walter']
            elif 'jesse' in dialogue:
                character = 'jesse'
                speaker = jesse_speaker
                text = dialogue['jesse']
            else:
                raise ValueError(f"Dialogue {key} must contain either 'walter' or 'jesse'")
            
            # Generate audio for the line
            audio = interface.generate(
                config=outetts.GenerationConfig(
                    text=text,
                    speaker=speaker,
                )
            )
            
            # Save individual audio file
            individual_file = f"generated/audios/{key}_{character}.wav"
            audio.save(individual_file)
            logging.info(f"Saved individual audio to {individual_file}")
            
            # Load audio segment
            segment = AudioSegment.from_wav(individual_file)
            audio_segments.append(segment)
        
        # Combine all segments in sequence
        combined = AudioSegment.empty()
        for segment in audio_segments:
            combined += segment
        
        # Export the combined audio
        combined.export(output_path, format="mp3")
        logging.info(f"Combined voiceover saved to {output_path}")
        
        return output_path
            
    except Exception as e:
        logging.error(f"Voiceover generation failed: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        output_file = generate_voiceover("./test_script.json")
        print(f"Voiceover generated successfully: {output_file}")
    except Exception as e:
        logging.error(f"Voiceover generation failed: {str(e)}")
        raise