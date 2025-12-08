import subprocess
import whisper
import pyaudio
import wave
import os
import tempfile
from pathlib import Path
from src.config.config import Config

class VoiceInput:
    def __init__(self, model_size: str = "base"):
        print(f"Loading Whisper model ({model_size})...")
        self.model = whisper.load_model(model_size)
        print("Whisper model loaded.")

    def record_audio(self, duration: int = 5, sample_rate: int = 16000) -> str:
        """
        Records audio from the microphone for a fixed duration.
        Returns the path to the temporary WAV file.
        """
        chunk = 1024
        format = pyaudio.paInt16
        channels = 1
        
        p = pyaudio.PyAudio()
        
        stream = p.open(format=format,
                        channels=channels,
                        rate=sample_rate,
                        input=True,
                        frames_per_buffer=chunk)
        
        print("Listening...")
        frames = []
        
        for _ in range(0, int(sample_rate / chunk * duration)):
            data = stream.read(chunk)
            frames.append(data)
            
        print("Finished recording.")
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_filename = f.name
            
        wf = wave.open(temp_filename, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(format))
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        return temp_filename

    def transcribe(self, audio_path: str) -> str:
        """Transcribes the audio file using Whisper."""
        result = self.model.transcribe(audio_path)
        return result["text"].strip()

    def listen(self, duration: int = 5) -> str:
        """Records and transcribes audio."""
        audio_path = self.record_audio(duration)
        text = self.transcribe(audio_path)
        os.remove(audio_path) # Clean up
        return text

class VoiceOutput:
    def __init__(self, voice: str = "Samantha"):
        self.voice = voice

    def speak(self, text: str):
        """Speaks the text using macOS 'say' command."""
        try:
            subprocess.run(["say", "-v", self.voice, text], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error speaking text: {e}")
