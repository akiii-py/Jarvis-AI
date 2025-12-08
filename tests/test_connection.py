import requests
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.config.config import Config

def test_ollama_connection():
    print(f"Testing connection to Ollama at {Config.OLLAMA_BASE_URL}...")
    try:
        response = requests.get(Config.OLLAMA_BASE_URL)
        if response.status_code == 200:
            print("Successfully connected to Ollama!")
            return True
        else:
            print(f"Failed to connect. Status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError as e:
        print(f"Could not connect to Ollama. Is it running? Error: {e}")
        return False

if __name__ == "__main__":
    if test_ollama_connection():
        sys.exit(0)
    else:
        sys.exit(1)
