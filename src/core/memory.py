from collections import deque
from typing import List, Dict, Any
import json
from pathlib import Path
from src.config.config import Config

class ConversationMemory:
    def __init__(self, max_history: int = Config.MAX_CONVERSATION_HISTORY):
        self.max_history = max_history
        self.history: deque = deque(maxlen=max_history)
        self.preferences: Dict[str, Any] = self._load_preferences()
        self.history_file = Config.DATA_DIR / "conversation_history.json"
        
        # Load previous conversation history
        self._load_history()

    def add_turn(self, role: str, content: str):
        """Adds a turn to the conversation history and saves to disk."""
        self.history.append({"role": role, "content": content})
        self._save_history()

    def get_history(self) -> List[Dict[str, str]]:
        """Returns the conversation history as a list."""
        return list(self.history)

    def clear_history(self):
        """Clears the conversation history and deletes saved file."""
        self.history.clear()
        if self.history_file.exists():
            self.history_file.unlink()

    def _load_history(self):
        """Loads conversation history from disk."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    saved_history = json.load(f)
                    # Restore history (respecting max_history limit)
                    for turn in saved_history[-self.max_history:]:
                        self.history.append(turn)
                print(f"Loaded {len(self.history)} previous conversation turns.")
            except (json.JSONDecodeError, Exception) as e:
                print(f"Could not load conversation history: {e}")

    def _save_history(self):
        """Saves conversation history to disk."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(list(self.history), f, indent=2)
        except Exception as e:
            print(f"Could not save conversation history: {e}")

    def _load_preferences(self) -> Dict[str, Any]:
        """Loads user preferences from JSON file."""
        if Config.PREFERENCES_FILE.exists():
            try:
                with open(Config.PREFERENCES_FILE, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def save_preferences(self, new_prefs: Dict[str, Any]):
        """Updates and saves user preferences."""
        self.preferences.update(new_prefs)
        with open(Config.PREFERENCES_FILE, 'w') as f:
            json.dump(self.preferences, f, indent=4)
