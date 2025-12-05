import os
import sys
from gtts import gTTS

# Add parent dir to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from localizer.audio_utils import time_stretch_audio, get_duration

def test_sync():
    # Create a dummy mp3
    text = "This is a test audio for synchronization."
    tts = gTTS(text=text, lang='en')
    input_path = "test_input.mp3"
    output_path = "test_output.mp3"
    tts.save(input_path)
    
    duration = get_duration(input_path)
    print(f"Original duration: {duration:.2f}s")
    
    target_duration = duration * 2.0 # Stretch to double length
    print(f"Target duration: {target_duration:.2f}s")
    
    try:
        time_stretch_audio(input_path, target_duration, output_path)
        new_duration = get_duration(output_path)
        print(f"New duration: {new_duration:.2f}s")
        
        if abs(new_duration - target_duration) < 0.5:
            print("Sync successful!")
        else:
            print("Sync failed: Duration mismatch.")
            
    except Exception as e:
        print(f"Sync failed with error: {e}")
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)

if __name__ == "__main__":
    test_sync()
