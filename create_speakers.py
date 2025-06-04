import outetts
import scripts.config as config
import torch

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

character1 = interface.create_speaker(config.CHARACTERS["character1"]["audio_json_path"])
interface.save_speaker(character1, config.CHARACTERS["character1"]["audio_json_path"])
character2 = interface.create_speaker(config.CHARACTERS["character2"]["audio_json_path"])
interface.save_speaker(character2, config.CHARACTERS["character2"]["audio_json_path"])

