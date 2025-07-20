import os
from pydub import AudioSegment

def process_oppenheimer_voice_sample():
    """
    Processes the downloaded Oppenheimer interview to extract a clear,
    high-quality voice sample suitable for voice cloning with XTTS.
    """
    input_file = "knowledge_base/voice_samples/oppenheimer_reference.mp3"
    output_file = "knowledge_base/voice_samples/oppenheimer_sample.wav"
    
    # Create the output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    print(f"Loading audio file: {input_file}")
    
    # Load the audio file
    try:
        audio = AudioSegment.from_mp3(input_file)
    except Exception as e:
        print(f"Error loading audio file: {e}")
        print("Please ensure ffmpeg is installed and in your system's PATH.")
        return

    # Extract a clear segment (e.g., from 10s to 25s)
    # This segment is chosen for its clarity and minimal background noise.
    start_ms = 0 * 1000  # 10 seconds
    end_ms = 35 * 1000    # 25 seconds
    sample = audio[start_ms:end_ms]

    print("Processing audio sample...")
    
    # Convert to mono
    sample = sample.set_channels(1)
    
    # Set frame rate to 22050 Hz (required for XTTS)
    sample = sample.set_frame_rate(22050)

    # Export as WAV
    sample.export(output_file, format="wav")

    print(f"Successfully created voice sample: {output_file}")
    print("This sample will be used for voice cloning.")

if __name__ == "__main__":
    process_oppenheimer_voice_sample() 