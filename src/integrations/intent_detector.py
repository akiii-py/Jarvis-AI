"""
Intent Detector Module
- Uses LLM to understand user intent from natural language
- Handles typos, casual speech, incomplete sentences
- Returns structured intent + extracted data
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
import json
import re


@dataclass
class IntentResult:
    """Structured intent result"""
    type: str  # SPOTIFY_PLAY, YOUTUBE_SEARCH, etc.
    data: Dict[str, Any]  # Query, contact, message, etc.
    confidence: float  # 0.0 to 1.0
    is_app_command: bool  # True if should be handled by app navigator
    
    def __bool__(self):
        """IntentResult is truthy if it's an app command"""
        return self.is_app_command


class IntentDetector:
    """
    Detect user intent using LLM
    
    Handles:
    - Typos ("spoify" → "spotify")
    - Casual speech ("yo play some lofi")
    - Incomplete sentences ("just some chill music")
    - Natural variations
    """
    
    def __init__(self, llm_client, personality):
        self.llm = llm_client
        self.personality = personality
    
    def detect_intent(self, user_input: str) -> IntentResult:
        """
        Detect user intent from natural language input
        
        Returns:
            IntentResult: Structured intent with type and extracted data
        """
        
        # Create prompt for LLM
        prompt = self._create_detection_prompt(user_input)
        
        try:
            # Get LLM response
            response_generator = self.llm.chat([
                {
                    "role": "system",
                    "content": "You are a command intent detector. Respond ONLY with valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ])
            
            # Convert generator to string
            response = ""
            for chunk in response_generator:
                response += chunk
            
            # Parse LLM response
            intent_result = self._parse_llm_response(response, user_input)
            return intent_result
        
        except Exception as e:
            print(f"Intent detection error: {e}")
            # Fallback to unknown intent
            return IntentResult(
                type="UNKNOWN",
                data={},
                confidence=0.0,
                is_app_command=False
            )
    
    def _create_detection_prompt(self, user_input: str) -> str:
        """Create prompt for LLM to detect intent"""
        
        prompt = f"""Analyze this user input and detect their intent. Respond with ONLY valid JSON.

User Input: "{user_input}"

Possible intents:
- APP_OPEN: Opening a general application (Calculator, Notes, Safari, etc.)
- SPOTIFY_PLAY: ONLY if user explicitly asks to play music/song/artist
- SPOTIFY_CONTROL: Controlling Spotify (pause, resume, next, previous)
- YOUTUBE_SEARCH: Searching for and playing a video on YouTube
- GOOGLE_SEARCH: Searching Google
- WHATSAPP_MESSAGE: Sending a message via WhatsApp
- EMAIL_SEARCH: Searching emails in Mail app
- WEBSITE_VISIT: Opening a website or browser with specific URL
- GENERAL_CHAT: Default for conversation, questions, ideas, or if unclear
- UNKNOWN: Can't determine intent

Extract data intelligently:
- For APP_OPEN: Extract app name (Calculator, Notes, Safari, Chrome, etc.)
- For SPOTIFY_PLAY: Extract song/artist/playlist name (autocorrect typos like "spoify"→"spotify")
- For SPOTIFY_CONTROL: Extract action (pause, resume, next, previous, current)
- For WHATSAPP_MESSAGE: Extract contact name and message
- For YOUTUBE_SEARCH: Extract what to search for
- For GOOGLE_SEARCH: Extract search query
- For WEBSITE_VISIT: Extract website URL or site name

Examples:
- "open calculator" → APP_OPEN, app: "Calculator"
- "launch notes" → APP_OPEN, app: "Notes"
- "open safari" → APP_OPEN, app: "Safari"
- "open safari and search youtube.com" → WEBSITE_VISIT, website: "youtube.com"
- "open chrome and go to google.com" → WEBSITE_VISIT, website: "google.com"
- "go to youtube.com" → WEBSITE_VISIT, website: "youtube.com"
- "i want to work on a new project" → GENERAL_CHAT
- "give me some ideas" → GENERAL_CHAT
- "tell me a joke" → GENERAL_CHAT
- "play lo-fi beats" → SPOTIFY_PLAY, query: "lo-fi beats"
- "play back in black on spotify" → SPOTIFY_PLAY, query: "back in black"
- "play rakhlo tum chupaake from spotify" → SPOTIFY_PLAY, query: "rakhlo tum chupaake"
- "yo put on some lofi" → SPOTIFY_PLAY, query: "lofi"
- "pause" → SPOTIFY_CONTROL, action: "pause"
- "what's playing" → SPOTIFY_CONTROL, action: "current"
- "message john saying hey" → WHATSAPP_MESSAGE, contact: "john", message: "hey"
- "search python on youtube" → YOUTUBE_SEARCH, query: "python"
- "google dsa" → GOOGLE_SEARCH, query: "dsa"
- "what time is it" → GENERAL_CHAT

Respond with ONLY this JSON structure:
{{
    "intent_type": "SPOTIFY_PLAY",
    "data": {{"query": "lo-fi beats"}},
    "confidence": 0.95,
    "reasoning": "User wants to play lo-fi beats on Spotify"
}}"""
        return prompt
    
    def _parse_llm_response(self, response: str, user_input: str) -> IntentResult:
        """Parse LLM response into IntentResult"""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if not json_match:
                return IntentResult(
                    type="UNKNOWN",
                    data={},
                    confidence=0.0,
                    is_app_command=False
                )
            
            json_str = json_match.group(0)
            parsed = json.loads(json_str)
            
            intent_type = parsed.get("intent_type", "UNKNOWN")
            data = parsed.get("data", {})
            confidence = parsed.get("confidence", 0.0)
            
            # Determine if this is an app command
            app_commands = {
                "APP_OPEN",
                "SPOTIFY_PLAY", "SPOTIFY_CONTROL",
                "YOUTUBE_SEARCH", "GOOGLE_SEARCH",
                "WHATSAPP_MESSAGE", "EMAIL_SEARCH",
                "WEBSITE_VISIT"
            }
            
            is_app_command = intent_type in app_commands and confidence >= 0.7
            
            return IntentResult(
                type=intent_type,
                data=data,
                confidence=confidence,
                is_app_command=is_app_command
            )
        
        except json.JSONDecodeError as e:
            print(f"Failed to parse LLM response: {e}")
            return IntentResult(
                type="UNKNOWN",
                data={},
                confidence=0.0,
                is_app_command=False
            )
        except Exception as e:
            print(f"Error parsing intent: {e}")
            return IntentResult(
                type="UNKNOWN",
                data={},
                confidence=0.0,
                is_app_command=False
            )
