import pyaudio
import numpy as np
import time

class SimplePushToTalk:
    """
    Simple energy-based voice activation.
    No API keys required - completely free!
    """
    def __init__(self, energy_threshold: int = 1000):
        self.energy_threshold = energy_threshold
        self.pa = pyaudio.PyAudio()
        self.stream = None

    def listen(self, timeout: int = 30):
        """
        Listens for audio above energy threshold.
        Returns True when voice detected, False on timeout.
        """
        print("Listening... (speak to activate, or press Ctrl+C to skip)")
        
        chunk = 1024
        format = pyaudio.paInt16
        channels = 1
        rate = 16000
        
        self.stream = self.pa.open(
            format=format,
            channels=channels,
            rate=rate,
            input=True,
            frames_per_buffer=chunk
        )
        
        start_time = time.time()
        
        try:
            while True:
                # Check timeout
                if time.time() - start_time > timeout:
                    print("Timeout - no voice detected")
                    return False
                
                # Read audio
                data = self.stream.read(chunk, exception_on_overflow=False)
                audio_data = np.frombuffer(data, dtype=np.int16)
                
                # Calculate energy
                energy = np.abs(audio_data).mean()
                
                # Detect voice
                if energy > self.energy_threshold:
                    print("Voice detected!")
                    return True
                    
        except KeyboardInterrupt:
            print("\nSkipped")
            return False
        finally:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()

    def close(self):
        if self.pa:
            self.pa.terminate()
