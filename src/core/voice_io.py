"""
Voice I/O Module with ElevenLabs Integration
- Text-to-Speech using ElevenLabs API
- Speech-to-Text using Whisper
- Fallback to macOS 'say' command if ElevenLabs fails
"""

import os
import whisper
import pyaudio
import wave
import tempfile
import subprocess
import warnings
from elevenlabs import ElevenLabs, VoiceSettings
from dotenv import load_dotenv

# Suppress FP16 warning on CPU
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")

# Load environment variables
load_dotenv()


class VoiceInput:
    """Handle voice input using Whisper."""
    
    def __init__(self, model_size: str = "base"):
        """Initialize Whisper model for speech recognition."""
        print(f"Loading Whisper {model_size} model...")
        self.model = whisper.load_model(model_size)
        self.audio = pyaudio.PyAudio()
    
    def record_audio(self, sample_rate: int = 16000) -> str:
        """
        Record audio from microphone until stopped by user.
        
        Args:
            sample_rate: Audio sample rate
            
        Returns:
            Path to recorded audio file
        """
        print("🎤 Listening... (Press SPACE/ENTER to stop)")
        
        # Set up keyboard monitoring
        import sys, select, termios, tty
        old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())
        
        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=sample_rate,
            input=True,
            frames_per_buffer=1024
        )
        
        frames = []
        try:
            while True:
                # Read audio chunk
                data = stream.read(1024, exception_on_overflow=False)
                frames.append(data)
                
                # Check for keypress to stop
                if select.select([sys.stdin], [], [], 0)[0]:
                    key = sys.stdin.read(1)
                    if key in [' ', '\n', '\r', 'q']:
                        print("\n✅ Stopped listening.")
                        break
                        
        finally:
            stream.stop_stream()
            stream.close()
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        wf = wave.open(temp_file.name, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        return temp_file.name
    
    def transcribe(self, audio_file: str) -> str:
        """
        Transcribe audio file to text.
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Transcribed text
        """
        result = self.model.transcribe(audio_file)
        return result["text"].strip()
    
    def listen(self) -> str:
        """
        Record and transcribe audio.
        
        Returns:
            Transcribed text
        """
        audio_file = self.record_audio()
        print("🧠 Processing...")
        text = self.transcribe(audio_file)
        
        # Clean up temp file
        os.unlink(audio_file)
        
        return text
    
    def __del__(self):
        """Clean up audio resources."""
        if hasattr(self, 'audio'):
            self.audio.terminate()


class VoiceOutput:
    """Handle voice output using ElevenLabs or macOS say command."""
    
    def __init__(self, use_elevenlabs: bool = True):
        """
        Initialize voice output.
        
        Args:
            use_elevenlabs: Whether to use ElevenLabs TTS (fallback to macOS say if False or fails)
        """
        self.use_elevenlabs = use_elevenlabs
        self.elevenlabs_client = None
        
        if use_elevenlabs:
            try:
                api_key = os.getenv("ELEVENLABS_API_KEY")
                if api_key:
                    self.elevenlabs_client = ElevenLabs(api_key=api_key)
                    print("🎙️  ElevenLabs TTS initialized")
                else:
                    print("⚠️  ELEVENLABS_API_KEY not found, using macOS say")
                    self.use_elevenlabs = False
            except Exception as e:
                print(f"⚠️  ElevenLabs initialization failed: {e}, using macOS say")
                self.use_elevenlabs = False
    
    def speak(self, text: str, voice_id: str = "VHlcT3SbwGWyUw1IEjnd") -> bool:
        """
        Speak the given text.
        
        Args:
            text: Text to speak
            voice_id: ElevenLabs voice ID 
                     (default: Custom JARVIS voice)
                     Other popular options:
                     - "pNInz6obpgDQGcFmaJgB" - Adam (British male, professional)
                     - "onwK4e9ZLuTAKqWW03F9" - Daniel (British, deep)
                     - "pMsXgVXv3BLzUgSXRplE" - Charlie (British, casual)
        
        Returns:
            True if successful
        """
        if self.use_elevenlabs and self.elevenlabs_client:
            try:
                # Generate audio using ElevenLabs
                audio_generator = self.elevenlabs_client.text_to_speech.convert(
                    voice_id=voice_id,
                    optimize_streaming_latency="0",
                    output_format="mp3_22050_32",
                    text=text,
                    model_id="eleven_turbo_v2_5",
                    voice_settings=VoiceSettings(
                        stability=0.5,
                        similarity_boost=0.75,
                        style=0.0,
                        use_speaker_boost=True,
                    ),
                )
                
                # Save to temporary file
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
                for chunk in audio_generator:
                    if chunk:
                        temp_file.write(chunk)
                temp_file.close()
                
                # Play audio using afplay (macOS) with interrupt capability
                self.play_audio_file(temp_file.name)
                
                # Clean up
                os.unlink(temp_file.name)
                
                return True
                
            except Exception as e:
                print(f"⚠️  ElevenLabs TTS failed: {e}, falling back to macOS say")
                # Fallback to macOS say
                return self._speak_macos(text)
        else:
            # Use macOS say command
            return self._speak_macos(text)
            
    def play_audio_file(self, file_path: str):
        """Play audio file with interrupt capability."""
        # Use simple playback but check for interruption
        import sys, select, termios, tty
        
        try:
            # Start playback process
            process = subprocess.Popen(['afplay', file_path])
            
            # Monitor for keypress to interrupt
            old_settings = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())
            
            while process.poll() is None:
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    key = sys.stdin.read(1)
                    # Any key interrupts
                    if key:
                        process.terminate()
                        print("\n🛑 Interrupted.")
                        break
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    
    def _speak_macos(self, text: str) -> bool:
        """
        Fallback: Speak using macOS say command.
        
        Args:
            text: Text to speak
            
        Returns:
            True if successful
        """
        try:
            subprocess.run(['say', '-v', 'Samantha', text], check=True)
            return True
        except Exception as e:
            print(f"Error with macOS say: {e}")
            return False
