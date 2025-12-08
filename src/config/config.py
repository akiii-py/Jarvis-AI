import os
from pathlib import Path

class Config:
    # Project Paths
    BASE_DIR = Path(__file__).parent.parent.parent
    DATA_DIR = BASE_DIR / "data"
    PREFERENCES_FILE = DATA_DIR / "preferences.json"
    
    # LLM Settings
    OLLAMA_BASE_URL = "http://localhost:11434"
    DEFAULT_MODEL = "qwen2.5-coder:latest" # Updated to available model
    
    # Model Profiles for Different Tasks
    MODEL_PROFILES = {
        "coding": "qwen2.5-coder:latest",      # Best for code, debugging, DSA
        "research": "deepseek-r1:latest",      # Best for deep reasoning, research
        "general": "mistral:7b",               # Best for general conversation
    }
    
    # Agent Settings
    MAX_CONVERSATION_HISTORY = 10
    
    # Voice Settings
    PICOVOICE_ACCESS_KEY = os.getenv("PICOVOICE_ACCESS_KEY", "") # User must set this env var
    WHISPER_MODEL_SIZE = "base"
    TTS_VOICE = "Samantha"
    
    @classmethod
    def ensure_dirs(cls):
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)

Config.ensure_dirs()
