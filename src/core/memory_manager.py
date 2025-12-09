"""
Memory Manager Module
Tracks user habits, conversation history, and context for personality
Helps JARVIS:
- Remember what user typically does (coding marathons, sleep deprivation, etc.)
- Recall past conversations
- Make observations based on patterns
- Personalize responses
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


class ConversationMemory:
    """Manages conversation history and user context"""
    
    def __init__(self, memory_file: str = "data/conversation_memory.json"):
        self.memory_file = memory_file
        self.current_session = []
        self.user_habits = {}
        self.history = []
        self.load_memory()
    
    def load_memory(self):
        """Load previous conversation data"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
                    self.user_habits = data.get("habits", {})
                    # Keep last 10 conversations
                    self.history = data.get("history", [])[-10:]
            except:
                self.user_habits = {}
                self.history = []
        else:
            self.user_habits = {}
            self.history = []
    
    def save_memory(self):
        """Save conversation data"""
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        with open(self.memory_file, 'w') as f:
            json.dump({
                "habits": self.user_habits,
                "history": self.history,
                "last_updated": datetime.now().isoformat()
            }, f, indent=2)
    
    def add_exchange(self, user_input: str, jarvis_response: str):
        """Track user-JARVIS exchange"""
        exchange = {
            "user": user_input,
            "jarvis": jarvis_response,
            "timestamp": datetime.now().isoformat(),
        }
        
        self.current_session.append(exchange)
        self.history.append(exchange)
        
        # Update habits based on user input
        self._detect_habits(user_input)
        
        # Keep only last 100 exchanges
        if len(self.history) > 100:
            self.history.pop(0)
        
        self.save_memory()
    
    def _detect_habits(self, user_input: str):
        """Detect user habits from their inputs"""
        lower = user_input.lower()
        
        # Coding habit
        if any(word in lower for word in ["code", "debug", "git", "test", "compile", "function", "algorithm"]):
            self.user_habits["coding"] = self.user_habits.get("coding", 0) + 1
        
        # Sleep deprivation
        if any(word in lower for word in ["sleep", "tired", "exhausted", "haven't slept", "awake"]):
            self.user_habits["sleep_issues"] = True
        
        # Music listening
        if any(word in lower for word in ["music", "spotify", "play", "lo-fi", "song"]):
            self.user_habits["music_lover"] = True
        
        # Research/learning
        if any(word in lower for word in ["learn", "research", "study", "explain", "how does"]):
            self.user_habits["learner"] = self.user_habits.get("learner", 0) + 1
        
        # GitHub user
        if "github" in lower:
            self.user_habits["github_active"] = True
    
    def get_context(self) -> Dict[str, Any]:
        """Get current context for personality generation"""
        context = {
            "session_exchanges": len(self.current_session),
            "habits": self.user_habits,
            "recent_topics": self._extract_recent_topics(),
            "total_conversations": len(self.history),
        }
        return context
    
    def _extract_recent_topics(self) -> List[str]:
        """Extract recent conversation topics"""
        topics = []
        
        # Look at last 5 exchanges
        for exchange in self.current_session[-5:]:
            user_input = exchange["user"].lower()
            
            if "code" in user_input or "debug" in user_input:
                topics.append("coding")
            elif "music" in user_input or "spotify" in user_input:
                topics.append("music")
            elif "learn" in user_input or "explain" in user_input:
                topics.append("learning")
            elif "sleep" in user_input:
                topics.append("sleep")
        
        return list(set(topics))  # Remove duplicates
    
    def get_last_exchanges(self, count: int = 3) -> str:
        """Get formatted recent conversation"""
        if not self.current_session:
            return "(No previous context)"
        
        formatted = []
        for exchange in self.current_session[-count:]:
            formatted.append(f"You: {exchange['user']}")
            formatted.append(f"Jarvis: {exchange['jarvis']}")
        
        return "\n".join(formatted)
    
    def make_observation(self) -> str:
        """Generate an observation based on user habits"""
        observations = []
        
        if self.user_habits.get("coding", 0) > 3:
            observations.append("I notice you're quite focused on coding lately, sir.")
        
        if self.user_habits.get("sleep_issues"):
            observations.append("Your sleep schedule appears to be... flexible, sir.")
        
        if self.user_habits.get("music_lover"):
            observations.append("You do seem to have an affinity for music.")
        
        if self.user_habits.get("github_active"):
            observations.append("Your GitHub activity has been rather impressive, sir.")
        
        if self.user_habits.get("learner", 0) > 2:
            observations.append("You do enjoy learning, sir.")
        
        if observations:
            return " ".join(observations)
        return ""


class ContextAware:
    """Makes JARVIS context-aware"""
    
    def __init__(self, memory: ConversationMemory):
        self.memory = memory
    
    def detect_time_of_day(self) -> str:
        """Detect time and acknowledge appropriately"""
        from datetime import datetime
        hour = datetime.now().hour
        
        if hour < 6:
            return "late night"
        elif hour < 12:
            return "morning"
        elif hour < 18:
            return "afternoon"
        else:
            return "evening"
    
    def detect_user_tone(self, user_input: str) -> str:
        """Detect user's emotional tone"""
        lower = user_input.lower()
        
        if any(word in lower for word in ["urgent", "help", "error", "broken"]):
            return "urgent"
        elif any(word in lower for word in ["tired", "frustrated", "ugh", "argh"]):
            return "frustrated"
        elif any(word in lower for word in ["thanks", "appreciate", "love you", "amazing"]):
            return "grateful"
        elif any(word in lower for word in ["yo", "hey", "lol", "haha", "gang"]):
            return "casual"
        elif any(word in lower for word in ["question", "what", "how", "why"]):
            return "curious"
        
        return "neutral"
    
    def should_reference_habit(self) -> bool:
        """Determine if we should reference a user habit"""
        # Reference habits randomly but not too often
        import random
        return random.random() < 0.3  # 30% of the time
