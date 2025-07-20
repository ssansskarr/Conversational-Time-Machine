import os
import torch
from TTS.api import TTS
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocalTTS:
    def __init__(self):
        """Initialize the Local TTS service using Coqui TTS."""
        self.model = None
        self.speaker_wav = "knowledge_base/voice_samples/oppenheimer_sample.wav"
        
        # Check for CUDA availability
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")

        # Ensure the voice sample exists
        if not os.path.exists(self.speaker_wav):
            raise FileNotFoundError(f"Speaker WAV file not found at: {self.speaker_wav}")

        self._initialize_model()

    def _initialize_model(self):
        """Load the XTTSv2 model."""
        try:
            logger.info("Initializing Coqui TTS with model: tts_models/multilingual/multi-dataset/xtts_v2")
            self.model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(self.device)
            logger.info("Coqui TTS model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Coqui TTS model: {e}")
            raise

    def synthesize(self, text: str, output_path: str) -> str:
        """
        Synthesize speech from text using the cloned voice.

        Args:
            text (str): The text to be synthesized.
            output_path (str): The path to save the output audio file.

        Returns:
            str: The path to the generated audio file.
        """
        if not self.model:
            logger.error("TTS model is not initialized.")
            return None

        try:
            logger.info(f"Synthesizing speech for text: '{text[:50]}...'")
            self.model.tts_to_file(
                text=text,
                speaker_wav=self.speaker_wav,
                language="en",
                file_path=output_path,
            )
            logger.info(f"Speech synthesized successfully to: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error during speech synthesis: {e}")
            return None

def test_local_tts():
    """Test the LocalTTS service with a sample text."""
    print("Testing Local TTS...")
    try:
        tts = LocalTTS()
        text = "Now I am become Death, the destroyer of worlds."
        output_file = "test_oppenheimer_local.wav"
        tts.synthesize(text, output_file)
        if os.path.exists(output_file):
            print(f"Test audio successfully generated at: {output_file}")
        else:
            print("Test audio generation failed.")
    except Exception as e:
        print(f"An error occurred during the test: {e}")

if __name__ == "__main__":
    test_local_tts() 