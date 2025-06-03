import outetts

interface = outetts.Interface(
            config=outetts.ModelConfig.auto_config(
                model=outetts.Models.VERSION_1_0_SIZE_1B,
                backend=outetts.Backend.LLAMACPP,
                quantization=outetts.LlamaCppQuantization.FP16
            )
        )

walter = interface.create_speaker("samples/walter.wav")
interface.save_speaker(walter, "walter.json")
jesse = interface.create_speaker("samples/jesse.wav")
interface.save_speaker(jesse, "jesse.json")

