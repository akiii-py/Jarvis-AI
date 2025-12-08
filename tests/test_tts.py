import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.core.voice_io import VoiceOutput

def test_tts():
    try:
        tts = VoiceOutput()
        print("Testing TTS...")
        tts.speak("Hello, I am Jarvis. Text to speech is working correctly.")
        print("TTS test completed successfully.")
        return True
    except Exception as e:
        print(f"TTS test failed: {e}")
        return False

if __name__ == "__main__":
    if test_tts():
        sys.exit(0)
    else:
        sys.exit(1)
