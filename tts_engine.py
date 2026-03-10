import torch
import functools
from TTS.api import TTS

# Fix for PyTorch 2.6+ "Weights only load failed" error
# Monkey-patch torch.load to default weights_only=False since we trust the Coqui models.
original_torch_load = torch.load
@functools.wraps(original_torch_load)
def patched_torch_load(*args, **kwargs):
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return original_torch_load(*args, **kwargs)
torch.load = patched_torch_load

class TTSEngine:
    def __init__(self, model_name="tts_models/multilingual/multi-dataset/xtts_v2", device=None):
        """Initializes the TTS engine with the specified model."""
        if device is None:
            # Check for Apple Silicon (MPS)
            if torch.backends.mps.is_available():
                device = "mps"
            elif torch.cuda.is_available():
                device = "cuda"
            else:
                device = "cpu"
        
        print(f"Loading {model_name} on {device}...")
        self.tts = TTS(model_name).to(device)
        self.device = device

    def generate_speech(self, text, speaker_wav, language, output_path, temperature=0.75, top_p=0.85, **kwargs):
        """Generates speech with expressiveness controls."""
        # Use XTTS voice cloning interface
        self.tts.tts_to_file(
            text=text,
            speaker_wav=speaker_wav,
            language=language,
            file_path=output_path,
            temperature=temperature,
            top_p=top_p,
            **kwargs
        )
