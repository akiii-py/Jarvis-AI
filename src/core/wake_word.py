import pvporcupine
import pyaudio
import struct
from src.config.config import Config

class WakeWordListener:
    def __init__(self, access_key: str = None):
        self.access_key = access_key or Config.PICOVOICE_ACCESS_KEY
        if not self.access_key:
            raise ValueError("Picovoice AccessKey is required for Wake Word detection.")
            
        self.porcupine = pvporcupine.create(
            access_key=self.access_key,
            keywords=["jarvis"]
        )
        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine.frame_length
        )

    def listen(self):
        """
        Listens for the wake word. Returns True when detected.
        Blocking call.
        """
        print("Listening for 'Jarvis'...")
        try:
            while True:
                pcm = self.stream.read(self.porcupine.frame_length)
                pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
                keyword_index = self.porcupine.process(pcm)
                
                if keyword_index >= 0:
                    print("Wake word detected!")
                    return True
        except KeyboardInterrupt:
            return False
        finally:
            pass # Stream cleanup handled in close()

    def close(self):
        if self.stream:
            self.stream.close()
        if self.pa:
            self.pa.terminate()
        if self.porcupine:
            self.porcupine.delete()
