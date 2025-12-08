"""
App Navigator Module
- Main controller for app navigation commands
- Uses LLM-powered intent detection for natural language understanding
"""

import re
from typing import Tuple
from .spotify_controller import SpotifyController
from .browser_controller import BrowserController
from .app_automator import AppAutomator
from .intent_detector import IntentDetector


class AppNavigator:
    """Master controller for all app navigation and automation with LLM-powered intent detection."""
    
    def __init__(self, mac_control, personality, llm_client):
        self.mac_control = mac_control
        self.personality = personality
        
        # Initialize controllers
        self.spotify = SpotifyController(mac_control)
        self.browser = BrowserController(mac_control)
        self.automator = AppAutomator(mac_control)
        
        # Initialize LLM-powered intent detector
        self.intent_detector = IntentDetector(llm_client, personality)
    
    def handle_app_navigation(self, user_input: str) -> Tuple[bool, str]:
        """
        Main router - Use LLM to detect intent and handle
        
        Replaces keyword matching with intelligent intent detection
        """
        
        # Detect intent using LLM
        intent = self.intent_detector.detect_intent(user_input)
        
        # If not confident it's an app command, return not handled
        if not intent.is_app_command:
            return (False, "")
        
        # Route to appropriate handler based on detected intent
        intent_handlers = {
            "SPOTIFY_PLAY": self._handle_spotify_play,
            "SPOTIFY_CONTROL": self._handle_spotify_control,
            "YOUTUBE_SEARCH": self._handle_youtube_search,
            "GOOGLE_SEARCH": self._handle_google_search,
            "WHATSAPP_MESSAGE": self._handle_whatsapp_message,
            "EMAIL_SEARCH": self._handle_email_search,
            "WEBSITE_VISIT": self._handle_website_visit,
        }
        
        handler = intent_handlers.get(intent.type)
        if handler:
            return handler(intent.data)
        
        return (False, "")
    
    def _handle_spotify_play(self, data: dict) -> Tuple[bool, str]:
        """Handle Spotify play intent"""
        query = data.get("query", "")
        
        if not query:
            return (True, "I'm afraid I didn't catch what to play, sir.")
        
        try:
            success = self.spotify.search_and_play(query)
            
            if success:
                ack = self.personality.get_acknowledgment()
                return (True, f"{ack} Now playing {query} on Spotify, sir.")
            else:
                return (True, f"I'm afraid I couldn't find {query} on Spotify, sir.")
        except Exception as e:
            print(f"Spotify play error: {e}")
            return (True, "I'm afraid something went wrong with Spotify, sir.")
    
    def _handle_spotify_control(self, data: dict) -> Tuple[bool, str]:
        """Handle Spotify control intent (pause, resume, next, etc.)"""
        action = data.get("action", "").lower()
        
        try:
            if action == "pause":
                self.spotify.pause()
                ack = self.personality.get_acknowledgment()
                return (True, f"{ack} Pausing Spotify, sir.")
            
            elif action in ["resume", "play"]:
                self.spotify.play()
                ack = self.personality.get_acknowledgment()
                return (True, f"{ack} Resuming playback, sir.")
            
            elif action in ["next", "skip"]:
                self.spotify.next_track()
                return (True, "Skipping to next track, sir.")
            
            elif action in ["previous", "back"]:
                self.spotify.previous_track()
                return (True, "Going to previous track, sir.")
            
            elif action in ["current", "now_playing"]:
                current = self.spotify.get_current_track()
                if current:
                    return (True, f"Currently playing: {current}, sir.")
                return (True, "Unable to retrieve current track, sir.")
            
            return (False, "")
        
        except Exception as e:
            print(f"Spotify control error: {e}")
            return (True, "I'm afraid something went wrong with Spotify, sir.")
    
    def _handle_youtube_search(self, data: dict) -> Tuple[bool, str]:
        """Handle YouTube search intent"""
        query = data.get("query", "")
        
        if not query:
            return (True, "I'm afraid I didn't catch what to search for, sir.")
        
        try:
            success = self.browser.search_youtube(query)
            
            if success:
                ack = self.personality.get_acknowledgment()
                return (True, f"{ack} Searching YouTube for {query}, sir.")
            else:
                return (True, "I'm afraid I couldn't search YouTube, sir.")
        except Exception as e:
            print(f"YouTube search error: {e}")
            return (True, "I'm afraid something went wrong with YouTube, sir.")
    
    def _handle_google_search(self, data: dict) -> Tuple[bool, str]:
        """Handle Google search intent"""
        query = data.get("query", "")
        
        if not query:
            return (True, "I'm afraid I didn't catch what to search for, sir.")
        
        try:
            success = self.browser.search_google(query)
            
            if success:
                ack = self.personality.get_acknowledgment()
                return (True, f"{ack} Searching for {query}, sir.")
            else:
                return (True, "I'm afraid I couldn't search, sir.")
        except Exception as e:
            print(f"Google search error: {e}")
            return (True, "I'm afraid something went wrong with the search, sir.")
    
    def _handle_whatsapp_message(self, data: dict) -> Tuple[bool, str]:
        """Handle WhatsApp message intent"""
        contact = data.get("contact", "")
        message = data.get("message", "")
        
        if not contact or not message:
            return (True, "I'm afraid I didn't catch the contact or message, sir.")
        
        try:
            success = self.automator.send_whatsapp_message(contact, message)
            
            if success:
                ack = self.personality.get_acknowledgment()
                return (True, f"{ack} Message sent to {contact}, sir.")
            else:
                return (True, f"I'm afraid I couldn't send the message to {contact}, sir.")
        except Exception as e:
            print(f"WhatsApp error: {e}")
            return (True, "I'm afraid something went wrong with WhatsApp, sir.")
    
    def _handle_email_search(self, data: dict) -> Tuple[bool, str]:
        """Handle email search intent"""
        query = data.get("query", "")
        
        if not query:
            return (True, "I'm afraid I didn't catch what to search for, sir.")
        
        try:
            success = self.automator.open_email_search(query)
            
            if success:
                ack = self.personality.get_acknowledgment()
                return (True, f"{ack} Searching emails for {query}, sir.")
            else:
                return (True, "I'm afraid I couldn't search emails, sir.")
        except Exception as e:
            print(f"Email search error: {e}")
            return (True, "I'm afraid something went wrong with email search, sir.")
    
    def _handle_website_visit(self, data: dict) -> Tuple[bool, str]:
        """Handle website visit intent"""
        website = data.get("website", "")
        
        if not website:
            return (True, "I'm afraid I didn't catch the website, sir.")
        
        try:
            success = self.browser.open_website(website)
            
            if success:
                ack = self.personality.get_acknowledgment()
                return (True, f"{ack} Opening {website}, sir.")
            else:
                return (True, f"I'm afraid I couldn't open {website}, sir.")
        except Exception as e:
            print(f"Website visit error: {e}")
            return (True, "I'm afraid something went wrong with opening the website, sir.")
